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
Created on 8 Nov 2012

@author: George
'''
'''
Models a machine that can also have failures
'''

from SimPy.Simulation import Process, Resource, SimEvent
from SimPy.Simulation import activate, passivate, waituntil, now, hold, request, release, waitevent

from Failure import Failure
from CoreObject import CoreObject

from OperatorRouter import Router

from OperatedPoolBroker import Broker
from OperatorPool import OperatorPool

from RandomNumberGenerator import RandomNumberGenerator

# ===========================================================================
# the Machine object
# ===========================================================================
class Machine(CoreObject):
    class_name = 'Dream.Machine'
    # =======================================================================
    # initialise the id the capacity, of the resource and the distribution
    # =======================================================================
    def __init__(self, id, name, capacity=1, processingTime=None,
                  failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None',\
                  operatorPool='None',operationType='None',\
                  setupTime=None, loadTime=None,
                  isPreemptive=False, resetOnPreemption=False):

        CoreObject.__init__(self, id, name)
        self.type="Machine"                         #String that shows the type of object
        if not processingTime:
          processingTime = { 'distributionType': 'Fixed',
                             'mean': 1, }
        if processingTime['distributionType'] == 'Normal' and\
              processingTime.get('max', None) is None:
          processingTime['max'] = processingTime['mean'] + 5 * processingTime['stdev']

        if not setupTime:
          setupTime = { 'distributionType': 'Fixed',
                        'mean': 1, }
        if setupTime['distributionType'] == 'Normal' and\
              setupTime.get('max', None) is None:
          setupTime['max'] = setupTime['mean'] + 5 * setupTime['stdev']

        if not loadTime:
          loadTime = { 'distributionType': 'Fixed',
                        'mean': 1, }
        if loadTime['distributionType'] == 'Normal' and\
              loadTime.get('max', None) is None:
          loadTime['max'] = loadTime['mean'] + 5 * loadTime['stdev']

        #     holds the capacity of the machine 
        self.capacity=capacity
        #     define the distribution types of the processing and failure times respectively
        self.failureDistType=failureDistribution    #the distribution that the failure follows   
        #     sets the repairman resource of the Machine
        self.repairman=repairman
        #     Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, **processingTime)
        self.MTTF=MTTF
        self.MTTR=MTTR
        self.availability=availability
        ''' sets the operator resource of the Machine
             check if the operatorPool is a List or a OperatorPool type Object
             if it is a list then initiate a OperatorPool type object containing
             the list of operators provided
            if the  list is empty create operator pool with empty list
        '''
        # XXX operatorPool is not None ?
        if (type(operatorPool) is list) and len(operatorPool)>0:
            id = id+'_OP'
            name=self.objName+'_operatorPool'
            self.operatorPool=OperatorPool(id, name, operatorsList=operatorPool)
        elif(type(operatorPool) is OperatorPool):
            self.operatorPool=operatorPool         
        else:
            self.operatorPool='None'
            #self.operatorPool=operatorPool
        # update the operatorPool coreObjects list
        if self.operatorPool!='None':
             self.operatorPool.coreObjectIds.append(self.id)
             self.operatorPool.coreObjects.append(self)
        # holds the Operator currently processing the Machine
        self.currentOperator=None
        # define if load/setup/removal/processing are performed by the operator 
        self.operationType=operationType
        # boolean to check whether the machine is being operated
        self.toBeOperated = False
        # define the load times
        self.loadRng = RandomNumberGenerator(self, **loadTime)
        # variable that informs on the need for setup
        self.setUp=True
        # define the setup times
        self.stpRng = RandomNumberGenerator(self, **setupTime)
        # examine if there are multiple operation types performed by the operator
        #     there can be Setup/Processing operationType
        #     or the combination of both (MT-Load-Setup-Processing) 
        self.multOperationTypeList=[]   
        if self.operationType.startswith("MT"):
            OTlist = operationType.split('-')
            self.operationType=OTlist.pop(0)
            self.multOperationTypeList = OTlist
        else:
            self.multOperationTypeList.append(self.operationType)
        # initiate the Broker and the router
        if (self.operatorPool!='None'):
            self.broker=Broker(self)
            from Globals import G
            # if there is no router in G.RouterList
            if len(G.RoutersList)==0:
                self.router=Router()
                G.RoutersList.append(self.router)
            # otherwise set the already existing router as the machines Router
            else:
                self.router=G.RoutersList[0]
        #     lists to hold statistics of multiple runs
        self.WaitingForOperator=[]
        self.WaitingForLoadOperator=[]
        self.Loading = []
        self.SettingUp =[]
        # flags used for preemption purposes
        self.isPreemptive=isPreemptive
        self.resetOnPreemption=resetOnPreemption
        # event used by the router
        self.routerCycleOver=SimEvent('routerCycleOver')
    
    # =======================================================================
    # initialize the machine
    # =======================================================================        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)        
        # initialize the internal Queue (type Resource) of the Machine 
        self.Res=Resource(self.capacity)
        # initiate the Broker responsible to control the request/release
        # initialize the operator pool if any
        if (self.operatorPool!="None"):
            self.operatorPool.initialize()
            self.broker.initialize()
            activate(self.broker,self.broker.run())
            # initialise the router only once
            if not self.router.isInitialized:
                self.router.initialize()
                activate(self.router,self.router.run())
            for operator in self.operatorPool.operators:
                operator.coreObjectIds.append(self.id)
                operator.coreObjects.append(self)
        # the time that the machine started/ended its wait for the operator
        self.timeWaitForOperatorStarted=0
        self.timeWaitForOperatorEnded=0
        self.totalTimeWaitingForOperator=0
        # the time that the machine started/ended its wait for the operator
        self.timeWaitForLoadOperatorStarted=0
        self.timeWaitForLoadOperatorEnded=0
        self.totalTimeWaitingForLoadOperator=0
        # the time that the operator started/ended loading the machine
        self.timeLoadStarted=0
        self.timeLoadEnded=0
        self.totalLoadTime=0
        # the time that the operator started/ended setting-up the machine
        self.timeSetupStarted=0
        self.timeSetupEnded=0
        self.totalSetupTime=0
        # Current entity load/setup/loadOperatorwait/operatorWait related times 
        self.operatorWaitTimeCurrentEntity=0        # holds the time that the machine was waiting for the operator
        self.loadOperatorWaitTimeCurrentEntity = 0  # holds the time that the machine waits for operator to load the it
        self.loadTimeCurrentEntity = 0              # holds the time to load the current entity
        self.setupTimeCurrentEntity = 0             # holds the time to setup the machine before processing the current entity
        # TODO: check whether the requestingEntity variable can be used in OperatorPreemptive
        self.requestingEntity=None
        # flag that shows if the station is ready to proceed with the getEntity
        #    the router must set the flag to false if the station must not proceed with getEntity
        #    he must also assign the operator to the station that will proceed (operatorAssignedTo)
        self.canProceedWithGetEntity=False
        self.inPositionToGet=False
        # variables used for interruptions
        self.tinM=0
        self.timeRestartingProcessing=0
        self.interruption=False
        self.breakTime=0
    
    # =======================================================================
    # the main process of the machine
    # =======================================================================
    def run(self):
        # check if there is WIP and signal receiver
        self.initialSignalReceiver()
        # execute all through simulation time
        while 1:
            # waitEvent isRequested or interruption start 
            while 1:
                yield waitevent, self, [self.isRequested, self.interruptionStart]
                # if the machine is interrupted
                if self.interruptionStart.signalparam==now():
                    # wait until the interruption is ended
                    yield waitevent, self, self.interruptionEnd         # interruptionEnd to be triggered by ObjectInterruption
                    assert self==self.interruptionEnd.signalparam, 'the victim of the failure is not the object that received it'
                    # and signal the Giver, otherwise wait until it is requested
                    if self.signalGiver():
                        break   
                # if the machine can accept an entity and one predecessor requests it continuew with receiving the entity
                else:
                    break
            # TODO: maybe here have to assigneExit of the giver and add self to operator activeCallers list
            requestingObject=self.isRequested.signalparam
            assert requestingObject==self.giver, 'the giver is not the requestingObject'
              
#===============================================================================
#             # reset the canProceedWithGetEntity flag
#             self.canProceedWithGetEntity=False
#              
#             #===================================================================
# #             # TESTING
# #             print now(), self.id, 'is in position to get'
#             #===================================================================
#              
#             # if the machine must be operated for the loading then the operators must be picked wisely for every machine
#             if (self.operatorPool!="None")\
#                     and any(type=="Load" for type in self.multOperationTypeList):
#                 # the machine informs the router that it can receive from a requesting object
#                 self.requestRouter()
#                 self.router.startCycle.signal(self.id)
#                 # the machine must wait until the router has decided which machine will operated by which operator
# #                 yield waitevent, self, self.routerCycleOver
#                 yield waituntil, self, self.router.isSet
#                 self.router.victim=None
#                 # if the machine is not picked by the router the it should wait again 
#                 if not self.canProceedWithGetEntity:
#                     continue 
#===============================================================================
                
            # here or in the getEntity (apart from the loadTimeCurrentEntity)
            # in case they are placed inside the getEntity then the initialize of
            # the corresponding variables should be moved to the initialize() of the CoreObject
            self.operatorWaitTimeCurrentEntity = 0
            self.loadOperatorWaitTimeCurrentEntity = 0
            self.loadTimeCurrentEntity = 0
            self.setupTimeCurrentEntity = 0
            
    #===========================================================================
    # # ======= request a resource
    #         if(self.operatorPool!="None") and any(type=='Load' for type in self.multOperationTypeList):
    #             # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
    #             # machines waits to be operated (waits for the operator)
    #             self.requestOperator()
    #             self.timeWaitForLoadOperatorStarted = now()
    #             # wait until the Broker has waited times equal to loadTime (if any)
    #             yield waituntil, self, self.broker.isSet
    #             self.timeWaitForLoadOperatorEnded = now()
    #             self.loadOperatorWaitTimeCurrentEntity += self.timeWaitForLoadOperatorEnded-self.timeWaitForLoadOperatorStarted
    #             self.totalTimeWaitingForLoadOperator += self.loadOperatorWaitTimeCurrentEntity 
    #             
    # # ======= Load the machine if the Load is defined as one of the Operators' operation types
    #         if any(type=="Load" for type in self.multOperationTypeList) and self.isOperated():
    #             self.timeLoadStarted = now()
    #             yield hold,self,self.calculateLoadTime()
    #             # TODO: if self.interrupted(): There is the issue of failure during the Loading
    #             self.timeLoadEnded = now()
    #             self.loadTimeCurrentEntity = self.timeLoadEnded-self.timeLoadStarted 
    #             self.totalLoadTime += self.loadTimeCurrentEntity
    #             
    # # ======= release a resource if the only operation type is Load
    #         if (self.operatorPool!="None")\
    #              and any(type=="Load" for type in self.multOperationTypeList)\
    #              and not (any(type=="Processing" for type in self.multOperationTypeList)\
    #                       or any(type=="Setup" for type in self.multOperationTypeList))\
    #              and self.isOperated():
    #             # after getting the entity release the operator
    #             # machine has to release the operator
    #             self.releaseOperator()
    #             # wait until the Broker has finished processing
    #             yield waituntil, self, self.broker.isSet
    #         
    #         # TODO: reset the requestinEntity before receiving the currentEntity
    #         self.requestingEntity=None
    #===========================================================================
            # get the entity
                    # TODO: if there was loading time then we must solve the problem of getting an entity
                    # from an unidentified giver or not getting an entity at all as the giver 
                    # may fall in failure mode (assignExit()?)
            self.currentEntity=self.getEntity()
            # TODO: the Machine receive the entity  after the operator is available
            #     the canAcceptAndIsRequested method checks only in case of Load type of operation 
            
    #===========================================================================
    # # ======= request a resource if it is not already assigned an Operator
    #         if(self.operatorPool!="None")\
    #              and (any(type=="Processing" for type in self.multOperationTypeList)\
    #                   or any(type=="Setup" for type in self.multOperationTypeList))\
    #              and not self.isOperated():
    #             # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
    #             # machines waits to be operated (waits for the operator)
    #             self.requestOperator()
    #             self.timeWaitForOperatorStarted = now()
    #             # wait until the Broker has waited times equal to loadTime (if any)
    #             yield waituntil, self, self.broker.isSet
    #             self.timeWaitForOperatorEnded = now()
    #             self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
    #===========================================================================
            
            # variables dedicated to hold the processing times, the time when the Entity entered, 
            # and the processing time left 
            self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()                # get the processing time, tinMStarts holds the processing time of the machine 
            self.tinM=self.totalProcessingTimeInCurrentEntity                                          # timer to hold the processing time left
            
#===============================================================================
#     # ======= setup the machine if the Setup is defined as one of the Operators' operation types
#             # in plantSim the setup is performed when the machine has to process a new type of Entity and only once
#             if any(type=="Setup" for type in self.multOperationTypeList) and self.isOperated():
#                 self.timeSetupStarted = now()
#                 yield hold,self,self.calculateSetupTime()
#                 # TODO: if self.interrupted(): There is the issue of failure during the setup
#                 self.timeSetupEnded = now()
#                 self.setupTimeCurrentEntity = self.timeSetupEnded-self.timeSetupStarted
#                 self.totalSetupTime += self.setupTimeCurrentEntity
#                 
#             # setup is performed only when setup is set in Machines multOperationTypeList
#             # TODO: This must be also performed when no such operation is defined for the operator
#             #     but setupTime is given for the entity to be processed
# #             try:
# #                 if self.setupTime and not any(type=="Setup" for type in self.multOperationTypeList):
# #                     #===============================================================
# #                     # testing
# #                     if self.id=='MILL1' or self.id=='MILL2':
# #                         print '    ', now(), self.id, 'auto-setup'
# #                     #===============================================================
# #                     self.timeSetupStarted = now()
# #                     yield hold,self,self.calculateSetupTime()
# #                     #===========================================================
# #                     # testing
# #                     if self.id=='MILL1' or self.id=='MILL2':
# #                         print '    ', now()
# #                     #===========================================================
# #                     # TODO: if self.interrupted(): There is the issue of failure during the setup
# #                     self.timeSetupEnded = now()
# #                     self.setupTimeCurrentEntity = self.timeSetupEnded-self.timeSetupStarted
# #                     self.totalSetupTime += self.setupTimeCurrentEntity
# #             except:
# #                 pass
#             
#     # ======= release a resource if the only operation type is Setup
#             if (self.operatorPool!="None")\
#                 and self.isOperated()\
#                 and (any(type=="Setup" for type in self.multOperationTypeList)\
#                      or any(type=="Load" for type in self.multOperationTypeList))\
#                 and not any(type=="Processing" for type in self.multOperationTypeList):
#                 # after getting the entity release the operator
#                 # machine has to release the operator
#                 self.releaseOperator()
#                 # wait until the Broker has finished processing
#                 yield waituntil, self, self.broker.isSet
#===============================================================================
                                                                                 
            # variables used to flag any interruptions and the end of the processing
            self.interruption=False
            processingNotFinished=True
            # timers to follow up the failure time of the machine while on current Entity
            self.downTimeInCurrentEntity=0                          #holds the total time that the 
                                                                    #object was down while holding current entity
            # this loop is repeated until the processing time is expired with no failure
            # check when the processingEndedFlag switched to false              
            while processingNotFinished:
                # timeRestartingProcessing : dummy variable to keep track of the time that the processing starts after 
                #           every interruption                        
                self.timeRestartingProcessing=now()
                # wait for the processing time left tinM, if no interruption occurs then change the 
                # processingEndedFlag and exit loop,
                # else (if interrupted()) set interruption flag to true (only if tinM==0),
                # and recalculate the processing time left tinM, passivate while waiting for repair.
                yield hold,self,self.tinM                           # getting processed for remaining processing time tinM
                if self.interrupted():                              # if a failure occurs while processing the machine is interrupted.
                    self.interruptionActions()                      # execute interruption actions
                    
    #===========================================================================
    # # =============== release the operator if there is interruption 
    #                 if (self.operatorPool!="None")\
    #                     and self.isOperated()\
    #                     and any(type=="Processing" for type in self.multOperationTypeList):
    #                     self.releaseOperator()
    #                     yield waituntil,self,self.broker.isSet 
    #===========================================================================
    
                    # if there is a failure  in the machine or interruption due to preemption, it is passivated
                    # passivate the Machine for as long as there is no repair
                    yield waitevent, self, self.interruptionEnd
                    assert self==self.interruptionEnd.signalparam, 'the victim of the failure is not the object that received it'
                    self.postInterruptionActions()
                    
                    #===========================================================
                    # #if during the interruption the object became empty break        
                    # if (len(self.getActiveObjectQueue())==0 and self.shouldPreempt):
                    #     break
                    #===========================================================
                
    #===========================================================================
    # # =============== request a resource after the repair
    #                 if (self.operatorPool!="None")\
    #                     and any(type=="Processing" for type in self.multOperationTypeList)\
    #                     and not self.interruption:
    #                     self.timeWaitForOperatorStarted = now()
    #                     self.requestOperator()
    #                     yield waituntil,self,self.broker.isSet
    #                     self.timeWaitForOperatorEnded = now() 
    #                     self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
    #===========================================================================
                
                # if no interruption occurred the processing in M1 is ended 
                else:
                    processingNotFinished=False
                    
            #===================================================================
            # #if during the interruption the object became empty continue        
            # if (len(self.getActiveObjectQueue())==0 and self.shouldPreempt):
            #     self.shouldPreempt=False
            #     self.totalWorkingTime+=now()-(self.timeLastEntityEntered)
            #===================================================================
    #===========================================================================
    #             # TODO: Should release operator here
    # # =============== release resource in case of preemption
    #             if (self.operatorPool!='None')\
    #                 and any(type=="Processing" for type in self.multOperationTypeList)\
    #                 and not self.interruption: 
    #                 self.releaseOperator()
    #                 yield waituntil,self,self.broker.isSet
    #             continue
    #===========================================================================
            
            # carry on actions that have to take place when an Entity ends its processing
            self.endProcessingActions()
             
    #===========================================================================
    # # =============== release resource after the end of processing
    #         if (self.operatorPool!='None')\
    #             and any(type=="Processing" for type in self.multOperationTypeList)\
    #             and not self.interruption: 
    #             self.releaseOperator()
    #             yield waituntil,self,self.broker.isSet
    #===========================================================================
            
            # signal the receiver that the activeObject has something to dispose of
            if not self.signalReceiver():
            # if there was no available receiver, get into blocking control
                while 1:

                    # wait the event canDispose, this means that the station can deliver the item to successor
                    event=yield waitevent, self, [self.canDispose, self.interruptionStart]
                    # if there was interruption
                    #if self.interrupted():
                    # TODO not good implementation
                    if self.interruptionStart.signalparam==now():
                    # wait for the end of the interruption
                        self.interruptionActions()                          # execute interruption actions
                        yield waitevent, self, self.interruptionEnd         # interruptionEnd to be triggered by ObjectInterruption
                        assert self==self.interruptionEnd.signalparam, 'the victim of the failure is not the object that received it'
                        self.postInterruptionActions()
                        #=======================================================
                        # TODO: not sure if this is required now
                        # #if during the interruption the object became empty break
                        # if (len(self.getActiveObjectQueue())==0 and self.shouldPreempt):
                        #     self.shouldPreempt==False
                        #     break
                        #=======================================================
                        
                    if self.signalReceiver():
                        break
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def endProcessingActions(self):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        activeEntity=activeObjectQueue[0]
        # reset the variables used to handle the interruptions timing 
        self.timeRestartingProcessing=0
        self.breakTime=0
        # output to trace that the processing in the Machine self.objName ended 
        try:
            activeObject.outputTrace(activeObject.getActiveObjectQueue()[0].name,"ended processing in "+activeObject.objName)
        except IndexError:
            pass
        # the entity that just got processed is cold again it will get 
        # hot again by the time it reaches the giver of the next machine
        # TODO: Not only Machines require time to process entities
        #     entities such as batchReassembly/Decomposition require time to process entities
        # TODO: We must consider also the case that entities can be blocked before they can reach 
        #     the heating point. In such a case they must be removed from the G.pendingEntities list
        #     and added again after they are unblocked
        if activeEntity.family=='Entity':
            successorsAreMachines=True
            from Globals import G
            for object in activeObject.next:
                if not object in G.MachineList:
                    successorsAreMachines=False
                    break
            if not successorsAreMachines:
                activeObjectQueue[0].hot = False
        from Globals import G
        # the just processed entity is added to the list of entities 
        # pending for the next processing
        G.pendingEntities.append(activeObjectQueue[0])
        # set the variable that flags an Entity is ready to be disposed 
        activeObject.waitToDispose=True
        #do this so that if it is overtime working it is not counted as off-shift time
        if not activeObject.onShift:
            activeObject.timeLastShiftEnded=now()
        # update the total working time # the total processing time for this entity is what the distribution initially gave
        activeObject.totalWorkingTime+=activeObject.totalProcessingTimeInCurrentEntity
        # update the variables keeping track of Entity related attributes of the machine    
        activeObject.timeLastEntityEnded=now()                          # this holds the time that the last entity ended processing in Machine 
        activeObject.nameLastEntityEnded=activeObject.currentEntity.name        # this holds the name of the last entity that ended processing in Machine
        activeObject.completedJobs+=1                                   # Machine completed one more Job
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def interruptionActions(self):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        activeEntity=activeObjectQueue[0]
        # if the interrupt occured while processing an entity
        if not activeObject.waitToDispose:
            # output to trace that the Machine (self.objName) got interrupted           
            try:                                                       
                self.outputTrace(self.getActiveObjectQueue()[0].name, "Interrupted at "+self.objName)
            except IndexError:
                pass
            # recalculate the processing time left tinM
            self.tinM=self.tinM-(now()-self.timeRestartingProcessing)
            if(self.tinM==0):       # sometimes the failure may happen exactly at the time that the processing would finish
                                    # this may produce disagreement with the simul8 because in both SimPy and Simul8
                                    # it seems to be random which happens 1st
                                    # this should not appear often to stochastic models though where times are random
                self.interruption=True
        # start counting the down time at breatTime dummy variable
        self.breakTime=now()        # dummy variable that the interruption happened
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def postInterruptionActions(self):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        activeEntity=activeObjectQueue[0]
        # if the machine returns from an failure while processing an entity
        if not activeObject.waitToDispose:
            # use the timers to count the time that Machine is down and related 
            self.downTimeProcessingCurrentEntity+=now()-self.breakTime      # count the time that Machine is down while processing this Entity
            self.downTimeInCurrentEntity+=now()-self.breakTime              # count the time that Machine is down while on currentEntity
            self.timeLastFailureEnded=now()                                 # set the timeLastFailureEnded
            self.failureTimeInCurrentEntity+=now()-self.breakTime           # dummy variable keeping track of the failure time 
            # output to trace that the Machine self.objName was passivated for the current failure time
            self.outputTrace(self.getActiveObjectQueue()[0].name, "passivated in "+self.objName+" for "+str(now()-self.breakTime))
        # when a machine returns from failure while trying to deliver an entity
        else:
            # count the failure while on current entity time with failureTime variable
            self.failureTimeInCurrentEntity+=now()-self.breakTime
            # calculate the time the Machine was down while trying to dispose the current Entity,
            # and the total down time while on current Entity
            self.downTimeInTryingToReleaseCurrentEntity+=now()-self.breakTime
            self.downTimeInCurrentEntity+=now()-self.breakTime        # already updated from failures during processing
            # update the timeLastFailureEnded
            self.timeLastFailureEnded=now()
            # reset the variable holding the time the failure happened
            self.breakTime=0
                            
    # =======================================================================
    # checks if the machine is Up
    # =======================================================================
    def checkIfMachineIsUp(self):
        return self.Up

    # =======================================================================
    # checks if the Machine can accept an entity
    # it checks also who called it and returns TRUE only to the predecessor 
    # that will give the entity.
    # =======================================================================  
    def canAccept(self, callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        # if we have only one predecessor just check if there is a place and the machine is up
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(len(activeObject.previous)==1 or callerObject==None):
            if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                    or any(type=='Setup' for type in activeObject.multOperationTypeList))):
                return activeObject.operatorPool.checkIfResourceIsAvailable()\
                        and activeObject.checkIfMachineIsUp()\
                        and len(activeObjectQueue)<activeObject.capacity
            else:
                return activeObject.checkIfMachineIsUp() and len(activeObjectQueue)<activeObject.capacity\
                      
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            return activeObject.operatorPool.checkIfResourceIsAvailable()\
                and activeObject.checkIfMachineIsUp()\
                and len(activeObjectQueue)<activeObject.capacity
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            return activeObject.checkIfMachineIsUp() and len(activeObjectQueue)<activeObject.capacity and (thecaller in activeObject.previous)
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some possible giver waiting for it
    # also updates the giver to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        # check if there is a place, the machine is up and the predecessor has an entity to dispose. if the machine has to compete 
        # for an Operator that loads the entities onto it check if the predecessor if blocked by an other Machine. if not then the machine 
        # has to block the predecessor giverObject to avoid conflicts with other competing machines
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            if giverObject.haveToDispose(activeObject):
                #===============================================================
                # # TODO: check whether this entity is the one to be hand in
                # #     to be used in operatorPreemptive
                # activeObject.requestingEntity=giverObject.getActiveObjectQueue()[0]
                # # TODO: update the objects requesting the operator
                # activeObject.operatorPool.requestingObject=activeObject.giver
                # # TODOD: update the last object calling the operatorPool
                # activeObject.operatorPool.receivingObject=activeObject
                #===============================================================
                if activeObject.operatorPool.checkIfResourceIsAvailable()\
                    and activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity:
                    if not giverObject.exitIsAssignedTo():
                        activeObject.giver.assignExitTo()
                    elif giverObject.exitIsAssignedTo()!=activeObject:
                        return False
                    # if the activeObject is not in operators' activeCallersList
                    if activeObject not in activeObject.operatorPool.operators[0].activeCallersList:
                        # append it to the activeCallerList of the operatorPool operators list
                        for operator in activeObject.operatorPool.operators:
                            operator.activeCallersList.append(activeObject)
                    return True
            else:
                return False
        else:
            # the operator performs no load and the entity is received by the machine while there is 
            # no need for operators presence. The operator needs to be present only where the load Type 
            # operation is assigned
            if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity\
                    and giverObject.haveToDispose(activeObject):
                if not giverObject.exitIsAssignedTo():
                    activeObject.giver.assignExitTo()
                elif giverObject.exitIsAssignedTo()!=activeObject:
                    return False
                return True
    
    # =======================================================================
    # checks if the machine down or it can dispose the object
    # =======================================================================
    def ifCanDisposeOrHaveFailure(self):
        return self.Up==False or self.getReceiverObject().canAccept(self) or len(self.getActiveObjectQueue())==0
    
    # =======================================================================
    # get an entity from the giver
    # =======================================================================
    def getEntity(self):
        activeObject=self.getActiveObject()
        activeEntity=CoreObject.getEntity(self)          # run the default method   
        # after the machine receives an entity, it must be removed from the pendingEntities list
        from Globals import G
        if activeEntity in G.pendingEntities:
            G.pendingEntities.remove(activeEntity)  
        return activeEntity
  
    # =======================================================================
    # removes an entity from the Machine
    # =======================================================================
    def removeEntity(self, entity=None):
        activeObject=self.getActiveObject()
        activeEntity=CoreObject.removeEntity(self, entity)          # run the default method     
        activeObject.waitToDispose=False                            # update the waitToDispose flag
        if activeObject.canAccept():
            activeObject.signalGiver()
        return activeEntity
    
    # ======================================================================= 
    # checks if the Machine can dispose an entity to the following object
    # =======================================================================
    def haveToDispose(self, callerObject=None):
        # get active and the receiver object
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        #if we have only one successor just check if machine waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            return len(activeObjectQueue)>0 and activeObject.waitToDispose and activeObject.checkIfActive()
        thecaller=callerObject
        return len(activeObjectQueue)>0 and activeObject.waitToDispose\
             and activeObject.checkIfActive() and (thecaller in activeObject.next)
    
    # =======================================================================
    #                       calculates the setup time
    # =======================================================================
    def calculateSetupTime(self):
        return self.stpRng.generateNumber()
    
    # =======================================================================
    #                        calculates the Load time
    # =======================================================================
    def calculateLoadTime(self):
        return self.loadRng.generateNumber()
    
    # =======================================================================
    #                   prepare the machine to be operated
    # =======================================================================
    def requestRouter(self):
        self.inPositionToGet=True
        if not self.router.isCalled():
            self.router.invoke()
    
    # =======================================================================
    #                   prepare the machine to be operated
    # =======================================================================
    def requestOperator(self):
        self.broker.invoke()
        self.toBeOperated = True
    
    # =======================================================================
    #                   prepare the machine to be released
    # =======================================================================
    def releaseOperator(self):
        self.outputTrace(self.currentOperator.objName, "released from "+ self.objName)
        # set the flag operatorAssignedTo to None
        self.currentOperator.operatorAssignedTo=None
        # if the operationType is just Load and not Setup or Processing
        #     then clear the activeCallersList of the currentOperator
        if any(type=='Load' for type in self.multOperationTypeList)\
            and not (any(type=='Setup' for type in self.multOperationTypeList)\
                     or any(type=='Processing' for type in self.multOperationTypeList)):
            self.currentOperator.activeCallersList=[]
            
        self.broker.invoke()
        self.toBeOperated = False
        
    # =======================================================================
    #       check if the machine is currently operated by an operator
    # =======================================================================
    def isOperated(self):
        return self.toBeOperated
    
    # =======================================================================
    #               check if the machine is already set-up
    # =======================================================================
    def isSetUp(self):
        return self.setUp
    
    # =======================================================================
    #          request that the machine is set-up by an operator
    # =======================================================================
    def requestSetup(self):
        self.setUp=False
    
    # =======================================================================
    # actions to be taken after the simulation ends
    # =======================================================================
    def postProcessing(self, MaxSimtime=None): 
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime
        
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        alreadyAdded=False                      # a flag that shows if the blockage time has already been added
        
        # checks all the successors. If no one can accept an Entity then the machine might be blocked
        mightBeBlocked=True
        for nextObject in self.next:
            if nextObject.canAccept():
                mightBeBlocked=False
        
        #calculate the offShift time for current entity
        offShiftTimeInCurrentEntity=0
        if self.interruptCause:
            if self.onShift==False and self.interruptCause.type=='ShiftScheduler':
                offShiftTimeInCurrentEntity=now()-activeObject.timeLastShiftEnded

        # if there is an entity that finished processing in a Machine but did not get to reach 
        # the following Object till the end of simulation, 
        # we have to add this blockage to the percentage of blockage in Machine
        # we should exclude the failure time in current entity though!
        if (len(activeObjectQueue)>0) and (mightBeBlocked)\
             and ((activeObject.nameLastEntityEntered == activeObject.nameLastEntityEnded)) and self.onShift:
            # be careful here, might have to reconsider
            activeObject.totalBlockageTime+=now()-(activeObject.timeLastEntityEnded+activeObject.downTimeInTryingToReleaseCurrentEntity)
            if activeObject.Up==False:
                activeObject.totalBlockageTime-=now()-activeObject.timeLastFailure
                alreadyAdded=True

        #if Machine is currently processing an entity we should count this working time  
        if(len(activeObject.getActiveObjectQueue())>0)\
            and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered))\
            and (not (activeObject.operationType=='Processing' and (activeObject.currentOperator==None))):
            #if Machine is down we should add this last failure time to the time that it has been down in current entity 
            if self.Up==False:
#             if(len(activeObjectQueue)>0) and (self.Up==False):
                activeObject.downTimeProcessingCurrentEntity+=now()-activeObject.timeLastFailure         
            activeObject.totalWorkingTime+=now()-activeObject.timeLastEntityEntered\
                                                -activeObject.downTimeProcessingCurrentEntity\
                                                -activeObject.operatorWaitTimeCurrentEntity\
                                                -activeObject.setupTimeCurrentEntity\
                                                -offShiftTimeInCurrentEntity
            activeObject.totalTimeWaitingForOperator+=activeObject.operatorWaitTimeCurrentEntity
        elif(len(activeObject.getActiveObjectQueue())>0)\
            and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered))\
            and (activeObject.currentOperator==None):
            # TODO: needs further research as the time of failure while waiting for operator is not counted yet
            if self.Up==False:
                activeObject.downTimeProcessingCurrentEntity+=now()-activeObject.timeLastFailure
            activeObject.totalTimeWaitingForOperator+=now()-activeObject.timeWaitForOperatorStarted\
                                                           -activeObject.downTimeProcessingCurrentEntity\
                                                           -offShiftTimeInCurrentEntity
        # if Machine is down we have to add this failure time to its total failure time
        # we also need to add the last blocking time to total blockage time     
        if(activeObject.Up==False):
            activeObject.totalFailureTime+=now()-activeObject.timeLastFailure
            # we add the value only if it hasn't already been added
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(now()-activeObject.timeLastEntityEnded)-(now()-activeObject.timeLastFailure)-activeObject.downTimeInTryingToReleaseCurrentEntity 
                alreadyAdded=True
        
        #if the machine is off shift,add this to the off-shift time
        # we also need to add the last blocking time to total blockage time  
        if activeObject.onShift==False:
            #add the time only if the object is interrupted because of off-shift
            if self.interruptCause:
                if self.interruptCause.type=='ShiftScheduler':
                    self.totalOffShiftTime+=now()-self.timeLastShiftEnded 
            elif len(self.getActiveObjectQueue())==0 or self.waitToDispose:
                self.totalOffShiftTime+=now()-self.timeLastShiftEnded 
            # we add the value only if it hasn't already been added
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(now()-activeObject.timeLastEntityEnded)-(now()-activeObject.timeLastShiftEnded)-offShiftTimeInCurrentEntity 
                
        #Machine was idle when it was not in any other state    
        activeObject.totalWaitingTime=MaxSimtime-activeObject.totalWorkingTime-activeObject.totalBlockageTime-activeObject.totalFailureTime-activeObject.totalLoadTime-activeObject.totalSetupTime-self.totalOffShiftTime
        
        if activeObject.totalBlockageTime<0 and activeObject.totalBlockageTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalBlockageTime=0  
        
        if activeObject.totalWaitingTime<0 and activeObject.totalWaitingTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalWaitingTime=0  
        
        activeObject.Failure.append(100*self.totalFailureTime/MaxSimtime)    
        activeObject.Blockage.append(100*self.totalBlockageTime/MaxSimtime)  
        activeObject.Waiting.append(100*self.totalWaitingTime/MaxSimtime)    
        activeObject.Working.append(100*self.totalWorkingTime/MaxSimtime)
        activeObject.WaitingForOperator.append(100*self.totalTimeWaitingForOperator/MaxSimtime)
        activeObject.WaitingForLoadOperator.append(100*self.totalTimeWaitingForLoadOperator/MaxSimtime)
        activeObject.Loading.append(100*self.totalLoadTime/MaxSimtime)
        activeObject.SettingUp.append(100*self.totalSetupTime/MaxSimtime)
        activeObject.OffShift.append(100*self.totalOffShiftTime/MaxSimtime)

     
    # =======================================================================
    # outputs the the "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G
        from Globals import getConfidenceIntervals
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
        
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel    
            G.outputSheet.write(G.outputIndex,0, "The percentage of Failure of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalFailureTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Working of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWorkingTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Blockage of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalBlockageTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Waiting of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWaitingTime/MaxSimtime)
            G.outputIndex+=1       
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value    
            
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Failure of "+ self.objName+" is:")
            failure_ci = getConfidenceIntervals(self.Failure)
            G.outputSheet.write(G.outputIndex, 1, failure_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, failure_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, failure_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Working of "+ self.objName+" is:")
            working_ci = getConfidenceIntervals(self.Working)
            G.outputSheet.write(G.outputIndex, 1, working_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, working_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, working_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Blockage of "+ self.objName+" is:")
            blockage_ci = getConfidenceIntervals(self.Blockage)
            G.outputSheet.write(G.outputIndex, 1, blockage_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, blockage_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, blockage_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+ self.objName+" is:")
            waiting_ci = getConfidenceIntervals(self.Waiting)
            G.outputSheet.write(G.outputIndex, 1, waiting_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, waiting_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, waiting_ci['max'])
            G.outputIndex+=1
        G.outputIndex+=1
    
    # =======================================================================    
    # outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        from Globals import getConfidenceIntervals
        json = {'_class': self.class_name,
                'id': self.id,
                'results': {}}
        if (G.numberOfReplications == 1):
            # if we had just one replication output the results as numbers
            json['results']['failure_ratio']=100*self.totalFailureTime/G.maxSimTime
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['blockage_ratio']=100*self.totalBlockageTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
            #output the off-shift time only if there is any
            if self.totalOffShiftTime:
                json['results']['off_shift_ratio']=100*self.totalOffShiftTime/G.maxSimTime
            if any(type=='Setup' for type in self.multOperationTypeList):
                json['results']['setup_ratio']=100*self.totalSetupTime/G.maxSimTime
            if any(type=='Load' for type in self.multOperationTypeList):
                json['results']['load_ratio']=100*self.totalLoadTime/G.maxSimTime
        else:
            json['results']['failure_ratio'] = getConfidenceIntervals(self.Failure)
            json['results']['working_ratio'] = getConfidenceIntervals(self.Working)
            json['results']['blockage_ratio'] = getConfidenceIntervals(self.Blockage)
            json['results']['waiting_ratio'] = getConfidenceIntervals(self.Waiting)
            json['results']['off_shift_ratio'] = getConfidenceIntervals(self.OffShift)
            json['results']['setup_ratio'] = getConfidenceIntervals(self.SettingUp)
            json['results']['loading_ratio'] = getConfidenceIntervals(self.Loading)

        G.outputJSON['elementList'].append(json)

