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

import simpy
from Machine import Machine
from RandomNumberGenerator import RandomNumberGenerator
# ===========================================================================
# the MachineJobShop object
# ===========================================================================
class MachineJobShop(Machine):
    @staticmethod
    def getProcessingTime(processingTime):
        '''returns the processingTime dictionary updated'''
        if not processingTime:
            processingTime = { 'distributionType': 'Fixed',
                               'mean': 0, }
        if processingTime['distributionType'] == 'Normal' and\
                processingTime.get('max', None) is None:
            processingTime['max'] = float(processingTime['mean']) + 5 * float(processingTime['stdev'])
        return processingTime
    @staticmethod
    def getSetupTime(setupTime):
        '''returns the setupTime dictionary updated'''
        if not setupTime:
            setupTime = { 'distributionType': 'Fixed',
                          'mean': 0, }
        if setupTime['distributionType'] == 'Normal' and\
                setupTime.get('max', None) is None:
            setupTime['max'] = float(setupTime['mean']) + 5 * float(setupTime['stdev'])
        return setupTime
    @staticmethod
    def getLoadTime(loadTime):
        '''returns the loadTime dictionary updated'''
        if not loadTime:
            loadTime = { 'distributionType': 'Fixed',
                         'mean': 0, }
        if loadTime['distributionType'] == 'Normal' and\
                loadTime.get('max', None) is None:
            loadTime['max'] = float(loadTime['mean']) + 5 * float(loadTime['stdev'])
        return loadTime
    
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
        # set isProcessing to False
        self.isProcessing=False
        # add working time
        self.totalWorkingTime+=self.env.now-self.timeLastProcessingStarted

        # blocking starts
        self.isBlocked=True
        self.timeLastBlockageStarted=self.env.now

        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.Res.users
        activeEntity=activeObjectQueue[0]
#         self.printTrace(activeEntity.name,processEnd=activeObject.objName)
        # reset the variables used to handle the interruptions timing 
        # self.timeRestartingProcessing=0
        self.breakTime=0
        # output to trace that the processing in the Machine self.objName ended 
        try:
            activeObject.outputTrace(activeEntity.name,"ended processing in "+activeObject.objName)
        except IndexError:
            pass
        
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
        # set the variable that flags an Entity is ready to be disposed 
        activeObject.waitToDispose=True
        #do this so that if it is overtime working it is not counted as off-shift time
        if not activeObject.onShift:
            activeObject.timeLastShiftEnded=self.env.now
        # update the variables keeping track of Entity related attributes of the machine
        activeObject.timeLastEntityEnded=self.env.now                              # this holds the time that the last entity ended processing in Machine 
        activeObject.nameLastEntityEnded=activeObject.currentEntity.name    # this holds the name of the last entity that ended processing in Machine
        activeObject.completedJobs+=1                                       # Machine completed one more Job
        # reset flags
        self.shouldPreempt=False 
        self.isProcessingInitialWIP=False 

        # TODO: collapse that to Machine


    # =======================================================================
    # gets an entity from the predecessor that the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeObject=self.getActiveObject()
        activeEntity=Machine.getEntity(self)     #run the default code
        
        # read the processing/setup/load times from the corresponding remainingRoute entry
        processingTime=activeEntity.remainingRoute[0].get('processingTime',{})
        processingTime=self.getProcessingTime(processingTime)
        self.rng=RandomNumberGenerator(self, **processingTime)
        self.procTime=self.rng.generateNumber()
        
        setupTime=activeEntity.remainingRoute[0].get('setupTime',{})
        setupTime=self.getSetupTime(setupTime)
        self.stpRng=RandomNumberGenerator(self, **setupTime)
        
        removedStep = activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return activeEntity
    
    
    
    #===========================================================================
    # update the next list of the object based on the activeEentity
    #===========================================================================
    def updateNext(self,entity=None):
        activeObject = self.getActiveObject()
        activeEntity=entity
        # read the possible receivers - update the next list
        import Globals
        # XXX: in the case of MouldAssembler there is no next defined in the route of the entities that are received
        # the position activeEntity.remainingRoute[1] is out of bound. the next should be updated by the remaining route of the entity to be assembled
        if len(activeEntity.remainingRoute)>1:
            nextObjectIds=activeEntity.remainingRoute[1].get('stationIdsList',[])
            nextObjects = []
            for nextObjectId in nextObjectIds:
                nextObject = Globals.findObjectById(nextObjectId)
                nextObjects.append(nextObject)
            # update the next list of the object
            for nextObject in nextObjects:
                # append only if not already in the list
                if nextObject not in activeObject.next:
                    activeObject.next.append(nextObject)
                                                                             
    # =======================================================================  
    # calculates the processing time
    # =======================================================================
    def calculateProcessingTime(self):
        # this is only for processing of the initial wip
        if self.isProcessingInitialWIP:
            # read the processing/setup/load times from the first entry of the full route
            activeEntity=self.getActiveObjectQueue()[0]
            processingTime=activeEntity.route[0].get('processingTime',{})
            processingTime=self.getProcessingTime(processingTime)
            self.rng=RandomNumberGenerator(self, **processingTime)
            self.procTime=self.rng.generateNumber()
            
            setupTime=activeEntity.route[0].get('setupTime',{})
            setupTime=self.getSetupTime(setupTime)
            self.stpRng=RandomNumberGenerator(self, **setupTime)
        return self.procTime    #this is the processing time for this unique entity 
    
    # =======================================================================
    # checks if the Queue can accept an entity       
    # it checks also the next station of the Entity 
    # and returns true only if the active object is the next station
    # ======================================================================= 
    def canAccept(self, callerObject=None):
        activeObjectQueue=self.Res.users
        thecaller=callerObject
        #return according to the state of the Queue
        # also check if (if the machine is to be operated) there are available operators
        if (self.operatorPool!='None' and (any(type=='Load' for type in self.multOperationTypeList))):
            return self.operatorPool.checkIfResourceIsAvailable()\
                    and len(activeObjectQueue)<self.capacity\
                    and self.checkIfMachineIsUp()\
                    and self.isInRoute(thecaller)\
                    and not self.entryIsAssignedTo()
        else:
            return len(activeObjectQueue)<self.capacity\
                    and self.checkIfMachineIsUp()\
                    and self.isInRoute(thecaller)\
                    and not self.entryIsAssignedTo()
                        
    #===========================================================================
    # method used to check whether the station is in the entity-to-be-received route
    # TODO: consider giving the activeEntity as attribute
    # TODO: consider the case when no caller is defined, 
    #         postProcessing calls canAccept on next members with no arguments
    #===========================================================================
    def isInRoute(self, callerObject=None):
        activeObjectQueue=self.Res.users
        thecaller=callerObject
        # if the caller is not defined then return True. We are only interested in checking whether 
        # the station can accept whatever entity from whichever giver
        if not thecaller:
            return True
        #check it the caller object holds an Entity that requests for current object
        if len(thecaller.Res.users)>0:
            # TODO: make sure that the first entity of the callerObject is to be disposed
            activeEntity=thecaller.Res.users[0]
            # if the machine's Id is in the list of the entity's next stations
            if self.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                return True
        return False
    
    # =======================================================================   
    # checks if the Machine can dispose an entity. 
    # Returns True only to the potential receiver
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        activeObjectQueue=self.Res.users
        thecaller=callerObject
        #if we have only one successor just check if machine waits to dispose and also is up
        # this is done to achieve better (cpu) processing time
        if(callerObject==None):
            return len(activeObjectQueue)>0\
                 and self.waitToDispose\
                 and self.checkIfActive()\
        #return True if the Machine in the state of disposing and the caller is the receiver
        return len(activeObjectQueue)>0\
             and self.waitToDispose\
             and self.checkIfActive()\
             and (thecaller in self.next)\
             and thecaller.isInRoute(self)

    # =======================================================================
    # method to execute preemption
    # =======================================================================    
    def preempt(self):
#         self.printTrace(self.id,preempted='')
        activeEntity=self.Res.users[0] #get the active Entity
        #calculate the remaining processing time
        #if it is reset then set it as the original processing time
        if self.resetOnPreemption:
            remainingProcessingTime=self.procTime
        #else subtract the time that passed since the entity entered
        #(may need also failure time if there was. TO BE MELIORATED)
        else:
            remainingProcessingTime=self.procTime-(self.env.now-self.timeLastEntityEntered)
        #update the remaining route of activeEntity
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.id)],\
                                               'processingTime':\
                                                    {'distributionType':'Fixed',\
                                                     'mean':str(remainingProcessingTime)}})
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.lastGiver.id)],\
                                               'processingTime':\
                                                    {'distributionType':'Fixed',\
                                                     'mean':'0'}})   
        #set the receiver  as the object where the active entity was preempted from 
        self.receiver=self.lastGiver
        self.next=[self.receiver]
        self.waitToDispose=True                     #set that I have to dispose
        self.receiver.timeLastEntityEnded=self.env.now     #required to count blockage correctly in the preemptied station
        # TODO: use a signal and wait for it, reactivation is not recognised as interruption
#         reactivate(self)
        self.preemptQueue.succeed(self.env.now)
        # TODO: consider the case when a failure has the Station down. The event preempt will not be received now()
        #     but at a later simulation time. 
            
    #===========================================================================
    # extend the default behaviour to check if whether the station 
    #     is in the route of the entity to be received
    #===========================================================================
    def canAcceptAndIsRequested(self,callerObject):
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        if self.isInRoute(giverObject):
            if Machine.canAcceptAndIsRequested(self,giverObject):
                self.readLoadTime(giverObject)
                return True
        return False

    #===========================================================================
    # to be called by canAcceptAndIsRequested if it is to return True.
    # the load timeof the Entity must be read
    #===========================================================================
    def readLoadTime(self,callerObject=None):
        assert callerObject!=None, 'the caller of readLoadTime cannot be None'
        thecaller=callerObject
        thecaller.sortEntities()
        activeEntity=thecaller.Res.users[0]
        loadTime=activeEntity.remainingRoute[0].get('loadTime',{})
        loadTime=self.getLoadTime(loadTime)
        self.loadRng=RandomNumberGenerator(self, **loadTime)
        
    # =======================================================================
    # removes an entity from the Machine
    # extension to remove possible receivers accordingly
    # =======================================================================
    def removeEntity(self, entity=None):
        receiverObject=self.receiver  
        activeEntity=Machine.removeEntity(self, entity)         #run the default method  
        removeReceiver=True 
        # search in the internalQ. If an entity has the same receiver do not remove
        for ent in self.Res.users:
            nextObjectIds=ent.remainingRoute[0].get('stationIdsList',[])
            if receiverObject.id in nextObjectIds:
                removeReceiver=False      
        # if not entity had the same receiver then the receiver will be removed    
        if removeReceiver:
            self.next.remove(receiverObject)
        return activeEntity

        
