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
Created on 12 Jul 2012

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All the core-objects should inherit from it
'''

from SimPy.Simulation import Process, Resource, now, SimEvent, waitevent

# ===========================================================================
# the core object
# ===========================================================================
class CoreObject(Process):
    
    def __init__(self, id, name, **kw):
        Process.__init__(self) 
        self.id = id
        self.objName = name
        #     lists that hold the previous and next objects in the flow
        self.next=[]                                #list with the next objects in the flow
        self.previous=[]                            #list with the previous objects in the flow
        self.nextIds=[]                             #list with the ids of the next objects in the flow
        self.previousIds=[]                         #list with the ids of the previous objects in the flow
        
        self.Failure=[]
        self.Working=[]
        self.Blockage=[]
        self.Waiting=[]
        self.OffShift=[]
        
        #default attributes set so that the CoreObject has them
        self.isPreemptive=False
        self.resetOnPreemption=False
        self.interruptCause=None
        self.gatherWipStat=False
        # signalizing an event that activates the generator
        self.isRequested=SimEvent('isRequested')
        self.canDispose=SimEvent('canDispose')
        self.interruptionEnd=SimEvent('interruptionEnd')
        self.interruptionStart=SimEvent('interruptionStart')
    
    def initialize(self):
        # XXX why call super.__init__ outside of __init__ ?
        Process.__init__(self) 
        self.Up=True                                    #Boolean that shows if the machine is in failure ("Down") or not ("up")
        self.onShift=True
        self.currentEntity=None      
        # ============================== total times ===============================================
        self.totalBlockageTime=0                        #holds the total blockage time
        self.totalFailureTime=0                         #holds the total failure time
        self.totalWaitingTime=0                         #holds the total waiting time
        self.totalWorkingTime=0                         #holds the total working time
        self.totalOffShiftTime=0                        #holds the total off-shift time
        self.completedJobs=0                            #holds the number of completed jobs 
        # ============================== Entity related attributes =================================
        self.timeLastEntityEnded=0                      #holds the last time that an entity ended processing in the object
        self.nameLastEntityEnded=""                     #holds the name of the last entity that ended processing in the object
        self.timeLastEntityEntered=0                    #holds the last time that an entity entered in the object
        self.nameLastEntityEntered=""                   #holds the name of the last entity that entered in the object

        # ============================== shift related times =====================================
        self.timeLastShiftStarted=0                     #holds the time that the last shift of the object started
        self.timeLastShiftEnded=0                       #holds the time that the last shift of the object ended
        self.offShiftTimeTryingToReleaseCurrentEntity=0 #holds the time that the object was off-shift while trying 
                                                        #to release the current entity  
        # ============================== failure related times =====================================
        self.timeLastFailure=0                          #holds the time that the last failure of the object started
        self.timeLastFailureEnded=0                     #holds the time that the last failure of the object ended
        self.downTimeProcessingCurrentEntity=0          #holds the time that the machine was down while 
                                                        #processing the current entity
        self.downTimeInTryingToReleaseCurrentEntity=0   #holds the time that the object was down while trying 
                                                        #to release the current entity                                                          
        self.downTimeInCurrentEntity=0                  #holds the total time that the 
                                                        #object was down while holding current entity
        self.timeLastEntityLeft=0                       #holds the last time that an entity left the object
        
        self.processingTimeOfCurrentEntity=0            #holds the total processing time that the current entity required                                               
        # ============================== waiting flag ==============================================                                      
        self.waitToDispose=False                        #shows if the object waits to dispose an entity   

        # ============================== the below are currently used in Jobshop =======================   
        self.giver=None                                 #the CoreObject that the activeObject will take an Entity from
        if len(self.previous)>0:
            self.giver=self.previous[0]
        self.receiver=None                              #the CoreObject that the activeObject will give an Entity to
        if len(self.next)>0:
            self.receiver=self.next[0]
        # ============================== variable that is used for the loading of machines =============
        self.exitAssignedToReceiver = None              # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 
        # ============================== variable that is used signalling of machines ==================
        self.entryAssignedToGiver = None                # by default the objects are not blocked 
                                                        # when the entities have to be received by machines
                                                        # then the machines have to be blocked after the first signal they receive
                                                        # in order to avoid signalling the same machine 
                                                        # while it has not received the entity it has been originally signalled for
        # ============================== lists to hold statistics of multiple runs =====================
        self.totalTimeWaitingForOperator=0 
        self.operatorWaitTimeCurrentEntity=0 
        self.totalTimeInCurrentEntity=0
        self.operatorWaitTimeCurrentEntity=0
        self.totalProcessingTimeInCurrentEntity=0
        self.failureTimeInCurrentEntity=0
        self.setupTimeCurrentEntity=0
 
        self.shouldPreempt=False    #flag that shows that the machine should preempt or not
        
        self.lastGiver=None         # variable that holds the last giver of the object, used by machine in case of preemption    
        # initialize the wipStatList - 
        # TODO, think what to do in multiple runs
        # TODO, this should be also updated in Globals.setWIP (in case we have initial wip)
        self.wipStatList=[[0,0]]

    # =======================================================================
    #                the main process of the core object 
    #     this is dummy, every object must have its own implementation
    # =======================================================================
    def run(self):
        raise NotImplementedError("Subclass must define 'run' method")
    
    # =======================================================================
    # sets the routing in and out elements for the Object
    # =======================================================================
    def defineRouting(self, predecessorList=[], successorList=[]):
        self.next=successorList
        self.previous=predecessorList
        
    # =======================================================================
    # checks if there is anything set as WIP at the begging of the simulation
    # and sends an event to initialize the simulation
    # =======================================================================
    def initialSignalReceiver(self):
        activeObject=self.getActiveObject()
        if self.haveToDispose():
            self.signalReceiver()
    
    # =======================================================================
    # removes an Entity from the Object the Entity to be removed is passed
    # as argument by getEntity of the receiver
    # =======================================================================
    def removeEntity(self, entity=None):
        self.addBlockage()
        
        activeObjectQueue=self.getActiveObjectQueue()  
        activeObjectQueue.remove(entity)       #remove the Entity from the queue
        if self.receiver:
            receiverObject=self.getReceiverObject()
            receiverObjectQueue=receiverObject.getActiveObjectQueue()
            receiverObjectQueue.append(entity)
        
        self.failureTimeInCurrentEntity=0 
        self.downTimeInTryingToReleaseCurrentEntity=0
        self.offShiftTimeTryingToReleaseCurrentEntity=0
        
        self.timeLastEntityLeft=now()
        self.outputTrace(entity.name, "released "+self.objName) 
        # update wipStatList
        if self.gatherWipStat:
            self.wipStatList.append([now(), len(activeObjectQueue)])
        return entity     
    
    # =======================================================================
    #             called be getEntity it identifies the Entity 
    #                        to be obtained so that 
    #            getEntity gives it to removeEntity as argument
    # =======================================================================    
    def identifyEntityToGet(self):
        giverObjectQueue=self.giver.getActiveObjectQueue() 
        return giverObjectQueue[0]
    
    # =======================================================================
    #              adds the blockage time to totalBlockageTime 
    #                    each time an Entity is removed
    # =======================================================================
    def addBlockage(self): 
        self.totalTimeInCurrentEntity=now()-self.timeLastEntityEntered
        self.totalTimeWaitingForOperator += self.operatorWaitTimeCurrentEntity
        if self.timeLastEntityEnded<self.timeLastShiftStarted:      
            self.offShiftTimeTryingToReleaseCurrentEntity=self.timeLastShiftStarted-self.timeLastShiftEnded
        blockage=now()-(self.timeLastEntityEnded+self.downTimeInTryingToReleaseCurrentEntity+self.offShiftTimeTryingToReleaseCurrentEntity)       
        self.totalBlockageTime+=blockage     
    
    # =======================================================================
    # gets an entity from the giver 
    # =======================================================================   
    def getEntity(self):
        # get active object and its queue, as well as the active (to be) entity 
        #(after the sorting of the entities in the queue of the giver object)
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        # get giver object, its queue, and sort the entities according to this object priorities
        giverObject=self.getGiverObject()
        giverObject.sortEntities()                      #sort the Entities of the giver 
                                                        #according to the scheduling rule if applied
        giverObjectQueue=self.getGiverObjectQueue()
        # if the giverObject is blocked then unBlock it
        if giverObject.exitIsAssignedTo():
            giverObject.unAssignExit()
        # if the activeObject entry is blocked then unBlock it
        if activeObject.entryIsAssignedTo():
            activeObject.unAssignEntry()
            
        # remove entity from the giver
        activeEntity = giverObject.removeEntity(entity=self.identifyEntityToGet())
        # variable that holds the last giver; used in case of preemption
        self.lastGiver=self.giver
#         #get the entity from the previous object and put it in front of the activeQ 
#         activeObjectQueue.append(activeEntity)
        
        #append the time to schedule so that it can be read in the result
        #remember that every entity has it's schedule which is supposed to be updated every time 
        # he entity enters a new object
        activeEntity.schedule.append([activeObject,now()])
        #update variables
        activeEntity.currentStation=self
        self.timeLastEntityEntered=now()
        self.nameLastEntityEntered=activeEntity.name      # this holds the name of the last entity that got into Machine      
        self.downTimeProcessingCurrentEntity=0
        # update the next list of the object
        activeObject.updateNext(activeEntity)
        self.outputTrace(activeEntity.name, "got into "+self.objName)
        self.printTrace(activeEntity.name, "got into "+self.id)
        return activeEntity
    
    #===========================================================================
    # updates the next list of the object
    #===========================================================================
    def updateNext(self, entity=None):
        pass
    
    #===========================================================================
    # check whether there is a critical entity to be disposed
    # and if preemption is required
    #===========================================================================
    def preemptReceiver(self):
        self.printTrace(self.id, 'trying to preempt a receiver')
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
    
        # find a critical order if any
        critical=False
        for entity in activeObjectQueue:
            if entity.isCritical:
                activeEntity=entity
                critical=True
                break
        if critical:
            # pick a receiver
            receiver=next(object for object in activeObject.next if object.isPreemptive and object.checkIfActive())
            # if there is any receiver that can be preempted check if it is operated
            if receiver:
                receiverOperated=False          # local variable to inform if the receiver is operated for Loading
                try:
                    # TODO: implement preemption for simple machines
                    if receiver.operatorPool\
                        and (type(receiver) is MachineJobShop\
                             or type(receiver) is MachineManagedJob):
                        # and the operationType list contains Load, the receiver is operated
                        if (receiver.operatorPool!="None")\
                            and any(type=="Load" for type in receiver.multOperationTypeList):
                            receiverOperated=True
                except:
                    pass
            # if the obtained Entity is critical and the receiver is preemptive and not operated
            #     in the case that the receiver is operated the preemption is performed by the operators
            #     if the receiver is not Up then no preemption will be performed
            if not receiverOperated:
                #if the receiver is not empty
                if len(self.receiver.getActiveObjectQueue())>0:
                    #if the receiver does not hold an Entity that is also critical
                    if not self.receiver.getActiveObjectQueue()[0].isCritical:
                        self.receiver.shouldPreempt=True
                        self.printTrace(self.id, 'preempting receiver'+self.receiver.id+'.. '*6)
                        self.receiver.preempt()
                        self.receiver.timeLastEntityEnded=now()     #required to count blockage correctly in the preemptied station
                        # TODO: sort so that the critical entity is placed in front
                        activeObjectQueue.sort(key=lambda x: x==activeEntity, reverse=True)
        # update wipStatList
        if self.gatherWipStat:
            self.wipStatList.append([now(), len(activeObjectQueue)])
    
    #===========================================================================
    # find possible receivers
    #===========================================================================
    def findReceivers(self):
        activeObject=self.getActiveObject()
        receivers=[]
        for object in [x for x in self.next if x.canAccept(activeObject)]:
            receivers.append(object)
        return receivers
    
    # =======================================================================
    # signal the successor that the object can dispose an entity 
    # =======================================================================
    def signalReceiver(self):
        self.printTrace(self.id, 'trying to signal receiver')
        activeObject=self.getActiveObject()
        possibleReceivers=activeObject.findReceivers()
        if possibleReceivers:
            receiver=activeObject.selectReceiver(possibleReceivers)
            receiversGiver=activeObject
            # perform the checks that canAcceptAndIsRequested used to perform and update activeCallersList or assignExit and operatorPool
            while not receiver.canAcceptAndIsRequested(receiversGiver):
                possibleReceivers.remove(receiver)
                if not possibleReceivers:
                    receiversGiver=None
                    receiver=None
                    # if no receiver can accept then try to preempt a receive if the stations holds a critical order
                    self.preemptReceiver()
                    return False
                receiver=activeObject.selectReceiver(possibleReceivers)
                receiversGiver=activeObject
            # sorting the entities of the object for the receiver
            activeObject.sortEntitiesForReceiver(receiver)
            # signalling the Router if the receiver is operated and not assigned an operator
            if activeObject.signalRouter(receiver):
                return False

            activeObject.receiver=receiver
            activeObject.receiver.giver=activeObject
            self.printTrace(self.id, ' '*50+'signalling receiver '+self.receiver.id)
            # assign the entry of the receiver
            activeObject.receiver.assignEntryTo()
            activeObject.receiver.isRequested.signal(activeObject)
            return True
        # if no receiver can accept then try to preempt a receive if the stations holds a critical order
        self.preemptReceiver()
        return False
    
    # =======================================================================
    # select a receiver Object
    # =======================================================================
    def selectReceiver(self,possibleReceivers=[]):
        activeObject=self.getActiveObject()
        candidates=possibleReceivers
        # dummy variables that help prioritize the objects requesting to give objects to the Machine (activeObject)
        maxTimeWaiting=0                                            # dummy variable counting the time a successor is waiting
        receiver=None
        for object in candidates:
            timeWaiting=now()-object.timeLastEntityLeft         # the time it has been waiting is updated and stored in dummy variable timeWaiting
            if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# if the timeWaiting is the maximum among the ones of the successors 
                maxTimeWaiting=timeWaiting
                receiver=object                                 # set the receiver as the longest waiting possible receiver
        return receiver
    
    #===========================================================================
    #  signalRouter method
    #===========================================================================
    def signalRouter(self, receiver=None):
        # if an operator is not assigned to the receiver then do not signal the receiver but the Router
        try:
            if not receiver.assignedOperator:
                if receiver.isLoadRequested():
                    from Globals import G
                    if not G.Router.invoked:
                        self.printTrace(self.id, ' '*50+'signalling router')
                        G.Router.invoked=True
                        G.Router.isCalled.signal(now())
                    return True
            else:
                return False
        except:
            return False
    
    #===========================================================================
    # sort the entities of the queue for the receiver
    #===========================================================================
    def sortEntitiesForReceiver(self, receiver=None):
        pass
    
    #===========================================================================
    # find possible givers
    #===========================================================================
    def findGivers(self):
        activeObject=self.getActiveObject()
        givers=[]
        for object in [x for x in activeObject.previous if(not x is activeObject)]:
            if object.haveToDispose(activeObject): 
                givers.append(object)
        return givers
    
    # =======================================================================
    # signal the giver that the entity is removed from its internalQueue
    # =======================================================================
    def signalGiver(self):
#         self.printTrace(self.id, 'trying to signal giver')
        activeObject=self.getActiveObject()
        possibleGivers=activeObject.findGivers()
        if possibleGivers:
            giver=activeObject.selectGiver(possibleGivers)
            giversReceiver=activeObject
            # perform the checks that canAcceptAndIsRequested used to perform and update activeCallersList or assignExit and operatorPool
            while not activeObject.canAcceptAndIsRequested(giver):
                possibleGivers.remove(giver)
                if not possibleGivers:
                    return False
                giver=activeObject.selectGiver(possibleGivers)
                giversReceiver=activeObject
            activeObject.giver=giver
            activeObject.giver.receiver=activeObject
            self.printTrace(self.id, ' '*50+'signalling giver '+self.giver.id)
            activeObject.giver.canDispose.signal(activeObject)
            return True
        return False
    
    # =======================================================================
    # select a giver Object
    # =======================================================================
    def selectGiver(self,possibleGivers=[]):
        activeObject=self.getActiveObject()
        candidates=possibleGivers
        # dummy variables that help prioritize the objects requesting to give objects to the Machine (activeObject)
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked
        giver=None
        # loop through the possible givers to see which have to dispose and which is the one blocked for longer
        for object in candidates:
            if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the predecessor has been down while trying to give away the Entity
                timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
            else:
                timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
            #if more than one predecessor have to dispose take the part from the one that is blocked longer
            if(timeWaiting>=maxTimeWaiting): 
                giver=object                 # the object to deliver the Entity to the activeObject is set to the ith member of the previous list
                maxTimeWaiting=timeWaiting    
        return giver
    
    #===========================================================================
    # checks whether the entity can proceed to a successor object
    #===========================================================================
    def canEntityProceed(self):
        pass
    
    # =======================================================================
    # actions to be taken after the simulation ends 
    # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        pass    
    
    # =======================================================================
    # outputs message to the trace.xls 
    # =======================================================================
    #outputs message to the trace.xls. Format is (Simulation Time | Entity or Frame Name | message)
    def outputTrace(self, entityName, message):
        from Globals import G
        if(G.trace=="Yes"):         #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,entityName)
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1       #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)
    
    #===========================================================================
    # prints message to the console
    #===========================================================================
    #print message in the console. Format is (Simulation Time | Entity or Frame Name | message)
    def printTrace(self, entityName, message):
        from Globals import G
        if(G.console=="Yes"):         #output only if the user has selected to
            print now(), entityName, message
            
    # =======================================================================
    # outputs data to "output.xls" 
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        pass
    
    # =======================================================================
    # outputs results to JSON File 
    # =======================================================================
    def outputResultsJSON(self):
        pass
    
    # =======================================================================
    # checks if the Object can dispose an entity to the following object 
    # =======================================================================
    def haveToDispose(self, callerObject=None): 
        activeObjectQueue=self.getActiveObjectQueue()    
        return len(activeObjectQueue)>0
    
    #========================================================================
    # checks if the object can dispose an entity 
    #     and returns the entity that it will dispose
    # To be used as self.canAcceptEntity(giver.haveToDisposeEntity(self))
    #========================================================================
    def haveToDisposeEntity(self, callerObject=None):
        activeObjectQueue=self.getActiveObjectQueue()
        if self.haveToDispose(callerObject):
            return activeObjectQueue[0]
    # =======================================================================
    #    checks if the Object can accept an entity and there is an entity 
    #                in some possible giver waiting for it
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        pass
    
    # =======================================================================
    # checks if the Object can accept an entity 
    # =======================================================================
    def canAccept(self, callerObject=None): 
        pass
    
    # =======================================================================
    # checks if the object can accept an specific Entity       
    # ======================================================================= 
    def canAcceptEntity(self, callerEntity=None):
        return True
    
    # =======================================================================
    # sorts the Entities in the activeQ of the objects 
    # =======================================================================
    def sortEntities(self):
        pass

    # =======================================================================
    # get the active object. This always returns self 
    # =======================================================================  
    def getActiveObject(self):
        return self
    
    # =======================================================================
    # get the activeQ of the active object. 
    # =======================================================================
    def getActiveObjectQueue(self):
        return self.Res.activeQ
    
    # =======================================================================
    # get the giver object in a getEntity transaction.
    # =======================================================================         
    def getGiverObject(self):
        return self.giver

    # =======================================================================
    # get the giver object queue in a getEntity transaction. 
    # =======================================================================    
    def getGiverObjectQueue(self):
        return self.getGiverObject().getActiveObjectQueue()
    
    # =======================================================================
    # get the receiver object in a removeEntity transaction.
    # ======================================================================= 
    def getReceiverObject(self):
        return self.receiver
    
    # =======================================================================
    # get the receiver object queue in a removeEntity transaction. 
    # =======================================================================    
    def getReceiverObjectQueue(self):
        return self.getReceiverObject().getActiveObjectQueue()
	
    # =======================================================================
    # calculates the processing time
    # =======================================================================
    def calculateProcessingTime(self):
        return self.rng.generateNumber()           # this is if we have a default processing time for all the entities
    
    # =======================================================================
    # checks if the machine is blocked
    # =======================================================================
    def exitIsAssignedTo(self):
        return self.exitAssignedToReceiver
    
    # =======================================================================
    # assign Exit of the object
    # =======================================================================
    def assignExitTo(self, callerObject=None):
#         self.printTrace(self.id, 'assignExit')
        self.exitAssignedToReceiver=callerObject
        
    # =======================================================================
    # unblock the object
    # =======================================================================
    def unAssignExit(self):
#         self.printTrace(self.id, 'unassignExit')
        self.exitAssignedToReceiver = None
        
    # =======================================================================
    # checks if the machine is blocked
    # =======================================================================
    def entryIsAssignedTo(self):
        return self.entryAssignedToGiver
    
    # =======================================================================
    # assign Exit of the object
    # =======================================================================
    def assignEntryTo(self):
        self.entryAssignedToGiver = self.giver
        
    # =======================================================================
    # unblock the object
    # =======================================================================
    def unAssignEntry(self):
        self.entryAssignedToGiver = None
        
    # =======================================================================
    #        actions to be carried whenever the object is interrupted 
    #                  (failure, break, preemption, etc)
    # =======================================================================
    def interruptionActions(self):
        pass

    # =======================================================================
    # method to execute preemption
    # =======================================================================    
    def preempt(self):
        #ToDO make a generic method
        pass
    
    # =======================================================================
    # checks if the object is in an active position
    # =======================================================================    
    def checkIfActive(self):
        return self.Up and self.onShift
    
    #===========================================================================
    # filter that returns True if the activeObject Queue is empty and 
    #     false if object holds entities in its queue
    #===========================================================================
    def activeQueueIsEmpty(self):
        return len(self.Res.activeQ)==0
    
#     # =======================================================================
#     # checks if the object is ready to receive an Entity
#     # =======================================================================    
#     def isReadyToGet(self):
#         return True     # set to true since this control was not needed until now. 
#                         # to return canAcceptAndIsRequested() would be more logical, but also computationally expensive
#         #return self.canAcceptAndIsRequested()
        
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def endProcessingActions(self):
        pass
    
    #===========================================================================
    # check if an entity is in the internal Queue of the object
    #===========================================================================
    def isInActiveQueue(self, entity=None):
        activeObjectQueue = self.getActiveObjectQueue()
        return any(x==entity for x in activeObjectQueue)
