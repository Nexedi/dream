# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================
'''
Created on 1 oct 2012

@author: George
'''
'''
extends the machine object so that it can act as a jobshop station. It reads the processing time and the successive station from the Entity
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold, reactivate

from Machine import Machine
# ===========================================================================
# the MachineJobShop object
# ===========================================================================
class MachineJobShop(Machine):
    # =======================================================================
    # set all the objects in previous and next
    # =======================================================================
    def initialize(self):
        from Globals import G
        self.previous=G.ObjList
        self.next=[]
        Machine.initialize(self)    #run default behaviour
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def endProcessingActions(self):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        activeEntity=activeObjectQueue[0]
        import Globals
        from Globals import G
        # the entity that just got processed is cold again it will get 
        # hot again by the time it reaches the giver of the next machine
        # TODO: Not only Machines require time to process entities
        if activeEntity.family=='Job':
            # read the list of next stations for the entity in just finished processing
            nextObjectIds=activeEntity.remainingRoute[0].get('stationIdsList',[])
            nextObjects = []
            for nextObjectId in nextObjectIds:
                nextObject=Globals.findObjectById(nextObjectId)
                nextObjects.append(nextObject)
            successorsAreMachines=True
            for object in nextObjects:
                if not object in G.MachineList:
                    successorsAreMachines=False
                    break
            if not successorsAreMachines:
                activeObjectQueue[0].hot = False
        # the just processed entity is added to the list of entities 
        # pending for the next processing
        G.pendingEntities.append(activeObjectQueue[0])

    # =======================================================================
    # gets an entity from the predecessor that the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeObject=self.getActiveObject()
        activeEntity=Machine.getEntity(self)     #run the default code
        
        # read the processing/setup/load times from the corresponding remainingRoute entry
        processingTime=activeEntity.remainingRoute[0].get('processingTime',{})
        self.distType=processingTime.get('distributionType','Fixed')
        self.procTime=float(processingTime.get('mean', 0))
        
        setupTime=activeEntity.remainingRoute[0].get('setupTime',{})
        self.distType=setupTime.get('setupDistribution','Fixed')
        self.setupTime=float(setupTime.get('setupMean', 0))
        
        import Globals
        # read the list of next stations
        nextObjectIds=activeEntity.remainingRoute[1].get('stationIdsList',[])
        nextObjects = []
        for nextObjectId in nextObjectIds:
            nextObject=Globals.findObjectById(nextObjectId)
            nextObjects.append(nextObject)
        # update the next list of the object
        for nextObject in nextObjects:
            # append only if not already in the list
            if nextObject not in activeObject.next:
                activeObject.next.append(nextObject)
        removedStep = activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return activeEntity  
                                                                             
    # =======================================================================  
    # calculates the processing time
    # =======================================================================
    def calculateProcessingTime(self):
        return self.procTime    #this is the processing time for this unique entity 
    
    # =======================================================================
    #                       calculates the setup time
    # =======================================================================
    def calculateSetupTime(self):
        return self.setupTime    #this is the setup time for this unique entity
    
    # =======================================================================
    #                        calculates the Load time
    # =======================================================================
    def calculateLoadTime(self):
        return self.loadTime    #this is the load time for this unique entity
    
    # =======================================================================
    # checks if the Queue can accept an entity       
    # it checks also the next station of the Entity 
    # and returns true only if the active object is the next station
    # ======================================================================= 
    def canAccept(self, callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        thecaller=callerObject
        if (thecaller!=None):
            #check it the caller object holds an Entity that requests for current object
            if len(thecaller.getActiveObjectQueue())>0:
                # TODO: make sure that the first entity of the callerObject is to be disposed
                activeEntity=thecaller.getActiveObjectQueue()[0]
                # if the machine's Id is in the list of the entity's next stations
                if activeObject.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                    #return according to the state of the Queue
                    # also check if (if the machine is to be operated) there are available operators
                    if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                            or any(type=='Setup' for type in activeObject.multOperationTypeList))):
                        return activeObject.operatorPool.checkIfResourceIsAvailable()\
                                and len(activeObject.getActiveObjectQueue())<activeObject.capacity\
                                and activeObject.Up
                    else:
                        return len(activeObject.getActiveObjectQueue())<activeObject.capacity\
                                and activeObject.Up
        return False
    
    # =======================================================================   
    # checks if the Machine can dispose an entity. 
    # Returns True only to the potential receiver
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller = callerObject
        
        #if we have only one successor just check if machine waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            activeObject.receiver=activeObject.next[0]
            return len(activeObjectQueue)>0\
                 and activeObject.waitToDispose\
                 and activeObject.Up\
                 and thecaller==activeObject.receiver
        
        thecaller=callerObject
        # give the entity to the successor that is waiting for the most time. 
        # (plant simulation does not do this in every occasion!)       
        maxTimeWaiting=0                                            # dummy variable counting the time a successor is waiting
        for object in activeObject.next:
            if(object.canAccept(activeObject)):                     # if a successor can accept an object
                timeWaiting=now()-object.timeLastEntityLeft         # the time it has been waiting is updated and stored in dummy variable timeWaiting
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# if the timeWaiting is the maximum among the ones of the successors 
                    maxTimeWaiting=timeWaiting
                    activeObject.receiver=object                    # set the receiver as the longest waiting possible receiver
                                                                    # in the next loops, check the other successors in the previous list

        
        #return True if the Machine in the state of disposing and the caller is the receiver  
        return len(activeObjectQueue)>0\
             and activeObject.waitToDispose\
             and activeObject.Up\
             and (thecaller is self.receiver)       

    # =======================================================================
    # method to execute preemption
    # =======================================================================    
    def preempt(self):
        activeObject=self.getActiveObject()
        activeEntity=self.getActiveObjectQueue()[0] #get the active Entity
        #calculate the remaining processing time
        #if it is reset then set it as the original processing time
        if self.resetOnPreemption:
            remainingProcessingTime=self.procTime
        #else subtract the time that passed since the entity entered
        #(may need also failure time if there was. TO BE MELIORATED)
        else:
            remainingProcessingTime=self.procTime-(now()-self.timeLastEntityEntered)
        #update the remaining route of activeEntity
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.id)],\
                                               'processingTime':\
                                                    {'distributionType':'Fixed',\
                                                     'mean':str(remainingProcessingTime)}})
#         activeEntity.remainingRoute.insert(0, [self.id, remainingProcessingTime])
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.lastGiver.id)],\
                                               'processingTime':\
                                                    {'distributionType':'Fixed',\
                                                     'mean':'0'}})
#         activeEntity.remainingRoute.insert(0, [self.lastGiver.id, 0])        
        #set the receiver  as the object where the active entity was preempted from 
        self.receiver=self.lastGiver
        self.next=[self.receiver]
        self.waitToDispose=True                     #set that I have to dispose
        self.receiver.timeLastEntityEnded=now()     #required to count blockage correctly in the preemptied station
        reactivate(self)
            
    #===========================================================================
    # just extend the default behaviour in order to read the load time 
    # from the Entity to be obtained        
    #===========================================================================
    def canAcceptAndIsRequested(self):
        if Machine.canAcceptAndIsRequested(self):
            self.readLoadTime()
            return True
        return False

    #===========================================================================
    # to be called by canAcceptAndIsRequested if it is to return True.
    # the load timeof the Entity must be read
    #===========================================================================
    def readLoadTime(self):
        self.giver.sortEntities()
        activeEntity=self.giver.getActiveObjectQueue()[0]
        loadTime=activeEntity.remainingRoute[0].get('loadTime',{})
        self.distType=loadTime.get('loadDistribution','Fixed')
        self.loadTime=float(loadTime.get('loadMean', 0))
        
    # =======================================================================
    # removes an entity from the Machine
    # extension to remove possible receivers accordingly
    # =======================================================================
    def removeEntity(self, entity=None):
        activeObject=self.getActiveObject()
        receiverObject=self.receiver  
        activeEntity=Machine.removeEntity(self, entity)         #run the default method  
        removeReceiver=True 
        # search in the internalQ. If an entity has the same receiver do not remove
        for ent in self.getActiveObjectQueue():
            nextObjectIds=ent.remainingRoute[0].get('stationIdsList',[])
            if receiverObject.id in nextObjectIds:
                removeReceiver=False      
        # if not entity had the same receiver then the receiver will be removed    
        if removeReceiver:
            activeObject.next.remove(receiverObject)
        return activeEntity

        