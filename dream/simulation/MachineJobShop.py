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
    # =======================================================================
    # set all the objects in previous and next
    # =======================================================================
    def initialize(self):
        from Globals import G
        self.previous=G.ObjList
        self.next=[]
        Machine.initialize(self)    #run default behaviour
    
    # =======================================================================
    # gets an entity from the predecessor that the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeObject=self.getActiveObject()
        activeEntity=Machine.getEntity(self)     #run the default code
        # read the processing time from the corresponding remainingRoute entry
        processingTime=activeEntity.remainingRoute[0].get('processingTime',{})
        processingTime=self.getOperationTime(processingTime)
        self.rng=RandomNumberGenerator(self, processingTime)
        self.procTime=self.rng.generateNumber()
        # check if there is a need for manual processing
        self.checkForManualOperation(type='Processing',entity=activeEntity)
        # read the setup time from the corresponding remainingRoute entry
        setupTime=activeEntity.remainingRoute[0].get('setupTime',{})
        setupTime=self.getOperationTime(setupTime)
        self.stpRng=RandomNumberGenerator(self, setupTime)
        # check if there is a need for manual processing
        self.checkForManualOperation(type='Setup',entity=activeEntity)
        activeEntity.currentStep = activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        if activeEntity.currentStep:
            # update the task_id of the currentStep dict within the schedule
            try:
                activeEntity.schedule[-1]["task_id"] = activeEntity.currentStep["task_id"]
                # if there is currentOperator then update the taskId of corresponding step of their schedule according to the task_id of the currentStep
                if self.currentOperator:
                    self.currentOperator.schedule[-1]["task_id"] = activeEntity.currentStep["task_id"]
            except KeyError:
                pass
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
            self.procTime = self.rng.generateNumber()
        return self.procTime    #this is the processing time for this unique entity  
    
    #===========================================================================
    # get the initial operation times (setup/processing); 
    # XXX initialy only setup time is calculated here
    #===========================================================================
    def calculateInitialOperationTimes(self):
        # read the setup/processing time from the first entry of the full route
        activeEntity=self.getActiveObjectQueue()[0]
        #if the entity has its route defined in the BOM then remainingProcessing/SetupTime is provided
        # XX consider moving setupUPtime update to checkForManualOperationTypes as Setup is performed before Processing
        if activeEntity.routeInBOM:
            processingTime=self.getOperationTime(activeEntity.remainingProcessingTime)
            setupTime=self.getOperationTime(activeEntity.remainingSetupTime)
        else:   # other wise these should be read from the route
            processingTime=activeEntity.route[0].get('processingTime',{})
            processingTime=self.getOperationTime(processingTime)
            setupTime=activeEntity.route[0].get('setupTime',{})
            setupTime=self.getOperationTime(setupTime)
        self.rng=RandomNumberGenerator(self, processingTime)
        self.stpRng=RandomNumberGenerator(self, setupTime)
                
    
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
                    and self.isInRouteOf(thecaller)\
                    and not self.entryIsAssignedTo()
        else:
            return len(activeObjectQueue)<self.capacity\
                    and self.checkIfMachineIsUp()\
                    and self.isInRouteOf(thecaller)\
                    and not self.entryIsAssignedTo()
                        
    #===========================================================================
    # method used to check whether the station is in the entity-to-be-received route
    #===========================================================================
    def isInRouteOf(self, callerObject=None):
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
             and thecaller.isInRouteOf(self)

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
                                                    {'Fixed':{'mean':str(remainingProcessingTime)}}})
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.lastGiver.id)],\
                                               'processingTime':{'Fixed':{'mean':'0'}}})   
        #set the receiver  as the object where the active entity was preempted from 
        self.receiver=self.lastGiver
        self.next=[self.receiver]
        self.waitToDispose=True                     #set that I have to dispose
        self.receiver.timeLastEntityEnded=self.env.now     #required to count blockage correctly in the preemptied station
        # TODO: use a signal and wait for it, reactivation is not recognised as interruption
#         reactivate(self)
        if self.expectedSignals['preemptQueue']:
            self.sendSignal(receiver=self, signal=self.preemptQueue)
        # TODO: consider the case when a failure has the Station down. The event preempt will not be received now()
        #     but at a later simulation time. 
            
    #===========================================================================
    # extend the default behaviour to check if whether the station 
    #     is in the route of the entity to be received
    #===========================================================================
    def canAcceptAndIsRequested(self,callerObject):
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        if self.isInRouteOf(giverObject):
            if Machine.canAcceptAndIsRequested(self,giverObject):
                self.readLoadTime(giverObject)
                return True
        return False

    #===========================================================================
    # to be called by canAcceptAndIsRequested if it is to return True.
    # the load time of the Entity must be read
    #===========================================================================
    def readLoadTime(self,callerObject=None):
        assert callerObject!=None, 'the caller of readLoadTime cannot be None'
        thecaller=callerObject
        thecaller.sortEntities()
        activeEntity=thecaller.Res.users[0]
        # read the load time from the corresponding remainingRoute entry
        loadTime=activeEntity.remainingRoute[0].get('loadTime',{})
        loadTime=self.getOperationTime(loadTime)
        self.loadRng=RandomNumberGenerator(self, loadTime)
    
    #===========================================================================
    # get the initial operationTypes (Setup/Processing) : manual or automatic
    #===========================================================================
    def checkInitialOperationTypes(self):
        # check if manual Setup is required
        self.checkForManualOperation(type='Setup')
        # check if manual Processing is required
        self.checkForManualOperation(type='Processing')
    
    #===========================================================================
    # check if the operation defined as an argument requires manual operation
    #===========================================================================
    def checkForManualOperation(self,type,entity=None):
        typeDict={'Setup':'setupTime', 'Processing':'processingTime'}
        assert type!=None, 'a type must be defined for the checkForManualOperation method'
        if not entity:
            activeEntity=self.getActiveObjectQueue()[0]
        else:
            activeEntity=entity
        # read the definition of the time from the remainingRoute dict
        if not self.isProcessingInitialWIP:
            operationTypeDict=activeEntity.remainingRoute[0].get('operationType',{})
            operationType=operationTypeDict.get(str(type),'not defined')
        else: # if the active entity is initialWIP at the start of simulation
            operationType=activeEntity.initialOperationTypes.get(str(type),'not defined')
        # if the operationType is not 'not defined'
        if operationType!='not defined':
            # if the operationType key has value 1 (manual operation)
            if operationType:
                # add setup to the multOpeartionTypeList
                if not type in self.multOperationTypeList:
                    self.multOperationTypeList.append(str(type))
            else:   # otherwise remove it from the multOperationTypeList
                if type in self.multOperationTypeList:
                    self.multOperationTypeList.remove(str(type))
        
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

        
