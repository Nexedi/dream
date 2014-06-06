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

# from SimPy.Simulation import Process, Resource, SimEvent
# from SimPy.Simulation import activate, passivate, waituntil, now, hold, request, release, waitevent
import simpy

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
            from Globals import G
            G.OperatorPoolsList.append(self.operatorPool)
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
            # if there is no router
            if not G.Router:
                self.router=Router()
                G.Router=self.router
            # otherwise set the already existing router as the machines Router
            else:
                self.router=G.Router
        #lists to hold statistics of multiple runs
        self.WaitingForOperator=[]
        self.WaitingForLoadOperator=[]
        self.Loading = []
        self.SettingUp =[]
        # flags used for preemption purposes
        self.isPreemptive=isPreemptive
        self.resetOnPreemption=resetOnPreemption
        # flag notifying that there is operator assigned to the actievObject
        self.assignedOperator=True
    
    # =======================================================================
    # initialize the machine
    # =======================================================================        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        
        # initialize the internal Queue (type Resource) of the Machine 
        #self.Res=Resource(self.capacity)
        self.Res=simpy.Resource(self.env, capacity=1)
        # initiate the Broker responsible to control the request/release
        # initialize the operator pool if any
        if (self.operatorPool!="None"):
            self.operatorPool.initialize()
            self.broker.initialize()
            self.env.process(self.broker.run())
            # initialise the router only once
            if not self.router.isInitialized:
                self.router.initialize()
            if not self.router.isActivated:
                self.env.process(self.router.run())
                self.router.isActivated=True
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
        # variables used for interruptions
        self.tinM=0
        self.timeRestartingProcessing=0
        self.interruption=False
        self.breakTime=0
        # flag notifying that there is operator assigned to the actievObject
        self.assignedOperator=True
        
        self.brokerIsSet=self.env.event()
        # this event is generated every time an operator is requested by machine for Load operation type.
        #     if the machine has not succeeded in getting an entity due to the resource absence 
        #     and waits for the next event to get the entity, 
        #     then it must be signalled that the operator is now available
        self.loadOperatorAvailable=self.env.event()
        # signal used for preemption
        self.preemptQueue=self.env.event()
    
    # =======================================================================
    # the main process of the machine
    # =======================================================================
    def run(self):
        # check if there is WIP and signal receiver
        self.initialSignalReceiver()
        # execute all through simulation time
        while 1:
            # waitEvent isRequested /interruptionEnd/loadOperatorAvailable
            while 1:
                self.printTrace(self.id, waitEvent='')
                receivedEvent = yield self.isRequested | self.interruptionEnd | self.loadOperatorAvailable
                self.printTrace(self.id, received='')
                # if the machine can accept an entity and one predecessor requests it continue with receiving the entity
                if self.isRequested in receivedEvent:
                    self.printTrace(self.id, isRequested=self.isRequested.value.id)
                    assert self.isRequested.value==self.giver, 'the giver is not the requestingObject'
                    assert self.giver.receiver==self, 'the receiver of the signalling object in not the station'
                    # reset the signalparam of the isRequested event
                    self.isRequested=self.env.event()
                    break
                # if an interruption caused the control to be taken by the machine or
                # if an operator was rendered available while it was needed by the machine to proceed with getEntity
                if self.interruptionEnd in receivedEvent or self.loadOperatorAvailable in receivedEvent:
                    if self.interruptionEnd in receivedEvent:
                        assert self.interruptionEnd.value==self.env.now, 'interruptionEnd received later than created'
                        self.printTrace(self.id, interruptionEnd=str(self.interruptionEnd.value))
                        self.interruptionEnd=self.env.event()
                    if self.loadOperatorAvailable in receivedEvent:
                        assert self.loadOperatorAvailable.value==self.env.now,'loadOperatorAvailable received later than created'
                        self.printTrace(self.id,loadOperatorAvailable=str(self.loadOperatorAvailable.value))
                        self.loadOperatorAvailable=self.env.event()
                    # try to signal the Giver, otherwise wait until it is requested
                    if self.signalGiver():
                        break
            # TODO: maybe here have to assigneExit of the giver and add self to operator activeCallers list
                
            # here or in the getEntity (apart from the loadTimeCurrentEntity)
            # in case they are placed inside the getEntity then the initialize of
            # the corresponding variables should be moved to the initialize() of the CoreObject
            self.operatorWaitTimeCurrentEntity = 0
            self.loadOperatorWaitTimeCurrentEntity = 0
            self.loadTimeCurrentEntity = 0
            self.setupTimeCurrentEntity = 0
            
    # ======= request a resource
            if(self.operatorPool!="None") and any(type=='Load' for type in self.multOperationTypeList):
                # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
                # machines waits to be operated (waits for the operator)
                self.requestOperator()
                self.timeWaitForLoadOperatorStarted = self.env.now
                # wait until the Broker has waited times equal to loadTime (if any)
                yield self.brokerIsSet
                self.brokerIsSet=self.env.event()
                self.timeWaitForLoadOperatorEnded = self.env.now
                self.loadOperatorWaitTimeCurrentEntity += self.timeWaitForLoadOperatorEnded-self.timeWaitForLoadOperatorStarted
                self.totalTimeWaitingForLoadOperator += self.loadOperatorWaitTimeCurrentEntity 
                 
    # ======= Load the machine if the Load is defined as one of the Operators' operation types
            if any(type=="Load" for type in self.multOperationTypeList) and self.isOperated():
                self.timeLoadStarted = self.env.now
                yield self.env.timeout(self.calculateLoadTime())
                # TODO: if self.interrupted(): There is the issue of failure during the Loading
                self.timeLoadEnded = self.env.now
                self.loadTimeCurrentEntity = self.timeLoadEnded-self.timeLoadStarted 
                self.totalLoadTime += self.loadTimeCurrentEntity
                 
    # ======= release a resource if the only operation type is Load
            if (self.operatorPool!="None")\
                 and any(type=="Load" for type in self.multOperationTypeList)\
                 and not (any(type=="Processing" for type in self.multOperationTypeList)\
                          or any(type=="Setup" for type in self.multOperationTypeList))\
                 and self.isOperated():
                # after getting the entity release the operator
                # machine has to release the operator
                self.releaseOperator()
                # wait until the Broker has finished processing
                yield self.brokerIsSet
                self.brokerIsSet=self.env.event()
             
            # TODO: reset the requestinEntity before receiving the currentEntity
            self.requestingEntity=None
            # get the entity
                    # TODO: if there was loading time then we must solve the problem of getting an entity
                    # from an unidentified giver or not getting an entity at all as the giver 
                    # may fall in failure mode (assignExit()?)
            self.currentEntity=self.getEntity()
            # TODO: the Machine receive the entity  after the operator is available
            #     the canAcceptAndIsRequested method checks only in case of Load type of operation 
            
    # ======= request a resource if it is not already assigned an Operator
            if(self.operatorPool!="None")\
                 and (any(type=="Processing" for type in self.multOperationTypeList)\
                      or any(type=="Setup" for type in self.multOperationTypeList))\
                 and not self.isOperated():
                # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
                # machines waits to be operated (waits for the operator)
                self.requestOperator()
                self.timeWaitForOperatorStarted = self.env.now
                # wait until the Broker has waited times equal to loadTime (if any)
                yield self.brokerIsSet
                self.brokerIsSet=self.env.event()
                self.timeWaitForOperatorEnded = self.env.now
                self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
            
            # variables dedicated to hold the processing times, the time when the Entity entered, 
            # and the processing time left 
            self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()                # get the processing time, tinMStarts holds the processing time of the machine 
            self.tinM=self.totalProcessingTimeInCurrentEntity                                          # timer to hold the processing time left
            
    # ======= setup the machine if the Setup is defined as one of the Operators' operation types
            # in plantSim the setup is performed when the machine has to process a new type of Entity and only once
            if any(type=="Setup" for type in self.multOperationTypeList) and self.isOperated():
                self.timeSetupStarted = self.env.now
                yield self.env.timeout(self.calculateSetupTime())
                # TODO: if self.interrupted(): There is the issue of failure during the setup
                self.timeSetupEnded = self.env.now
                self.setupTimeCurrentEntity = self.timeSetupEnded-self.timeSetupStarted
                self.totalSetupTime += self.setupTimeCurrentEntity
                 
            # setup is performed only when setup is set in Machines multOperationTypeList
            # TODO: This must be also performed when no such operation is defined for the operator
            #     but setupTime is given for the entity to be processed
#             try:
#                 if self.setupTime and not any(type=="Setup" for type in self.multOperationTypeList):
#                     self.timeSetupStarted = self.env.now
#                     yield hold,self,self.calculateSetupTime()
#                     # TODO: if self.interrupted(): There is the issue of failure during the setup
#                     self.timeSetupEnded = self.env.now
#                     self.setupTimeCurrentEntity = self.timeSetupEnded-self.timeSetupStarted
#                     self.totalSetupTime += self.setupTimeCurrentEntity
#             except:
#                 pass
             
    # ======= release a resource if the only operation type is Setup
            if (self.operatorPool!="None")\
                and self.isOperated()\
                and (any(type=="Setup" for type in self.multOperationTypeList)\
                     or any(type=="Load" for type in self.multOperationTypeList))\
                and not any(type=="Processing" for type in self.multOperationTypeList):
                # after getting the entity release the operator
                # machine has to release the operator
                self.releaseOperator()
                # wait until the Broker has finished processing
                yield self.brokerIsSet
                self.brokerIsSet=self.env.event()
                                                                                 
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
                self.timeRestartingProcessing=self.env.now
                # wait for the processing time left tinM, if no interruption occurs then change the processingEndedFlag and exit loop,
                #     else (if interrupted()) set interruption flag to true (only if tinM==0), 
                #     and recalculate the processing time left tinM, passivate while waiting for repair.
                # if a preemption has occurred then react accordingly (proceed with getting the critical entity)
                receivedEvent=yield self.env.timeout(self.tinM) | self.interruptionStart | self.preemptQueue        # getting processed for remaining processing time tinM
                if self.interruptionStart in receivedEvent:                              # if a failure occurs while processing the machine is interrupted.
                    assert self.interruptionStart.value==self.env.now, 'the interruption has not been processed on the time of activation'
                    self.interruptionStart=self.env.event()
                    self.interruptionActions()                      # execute interruption actions
                    
    # =============== release the operator if there is interruption 
                    if (self.operatorPool!="None")\
                        and self.isOperated()\
                        and any(type=="Processing" for type in self.multOperationTypeList):
                        self.releaseOperator()
                        yield self.brokerIsSet
                        self.brokerIsSet=self.env.event()
    
                    # if there is a failure  in the machine or interruption due to preemption, it is passivated
                    # passivate the Machine for as long as there is no repair
                    yield self.interruptionEnd
                    assert self.env.now==self.interruptionEnd.value, 'the victim of the failure is not the object that received it'
                    self.interruptionEnd=self.env.event()
                    self.postInterruptionActions()
                    
                
    # =============== request a resource after the repair
                    if (self.operatorPool!="None")\
                        and any(type=="Processing" for type in self.multOperationTypeList)\
                        and not self.interruption:
                        self.timeWaitForOperatorStarted = self.env.now
                        self.requestOperator()
                        yield self.brokerIsSet
                        self.brokerIsSet=self.env.event()
                        self.timeWaitForOperatorEnded = self.env.now 
                        self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
                # if the station is reactivated by the preempt method
                elif(self.shouldPreempt):
                    if (self.preemptQueue in receivedEvent):
                        assert self.preemptQueue.value==self.env.now, 'the preemption must be performed on the time of request'
                        self.preemptQueue=self.env.event()
                    self.interruptionActions()                      # execute interruption actions
                         
    # =============== release the operator if there is interruption 
                    if (self.operatorPool!="None")\
                        and self.isOperated()\
                        and any(type=="Processing" for type in self.multOperationTypeList):
                        self.releaseOperator()
                        yield self.brokerIsSet
                        self.brokerIsSet=self.env.event()
                     
                    self.postInterruptionActions()
                    break
                
                # if no interruption occurred the processing in M1 is ended 
                else:
                    processingNotFinished=False
            
            # carry on actions that have to take place when an Entity ends its processing
            self.endProcessingActions()
    # =============== release resource after the end of processing
            if (self.operatorPool!='None')\
                and self.isOperated()\
                and any(type=="Processing" for type in self.multOperationTypeList)\
                and not self.interruption: 
                self.releaseOperator()
                yield self.brokerIsSet
                self.brokerIsSet=self.env.event()
            # signal the receiver that the activeObject has something to dispose of
            if not self.signalReceiver():
            # if there was no available receiver, get into blocking control
                while 1:
                    # wait the event canDispose, this means that the station can deliver the item to successor
                    receivedEvent=yield self.canDispose | self.interruptionStart
                    # if there was interruption
                    #if self.interrupted():
                    # TODO not good implementation
                    if self.interruptionStart in receivedEvent:
                        assert self.interruptionStart.value==self.env.now, 'the interruption has not been processed on the time of activation'
                        self.interruptionStart=self.env.event()
                    # wait for the end of the interruption
                        self.interruptionActions()                          # execute interruption actions
                        yield self.interruptionEnd         # interruptionEnd to be triggered by ObjectInterruption
                        assert self.env.now==self.interruptionEnd.value, 'the victim of the failure is not the object that received it'
                        self.interruptionEnd=self.env.event()
                        self.postInterruptionActions()
                    if self.canDispose in receivedEvent:
                        self.canDispose=self.env.event()
                    # try to signal a receiver, if successful then proceed to get an other entity
                    if self.signalReceiver():
                        break
                    # TODO: router most probably should signal givers and not receivers in order to avoid this hold,self,0
                    #       As the receiver (e.g.) a machine that follows the machine receives an loadOperatorAvailable event,
                    #       signals the preceding station (e.g. self.machine) and immediately after that gets the entity.
                    #       the preceding machine gets the canDispose signal which is actually useless, is emptied by the following station
                    #       and then cannot exit an infinite loop.
                    yield self.entityRemoved #env.timeout(0)
                    self.entityRemoved=self.env.event()
                    # if while waiting (for a canDispose event) became free as the machines that follows emptied it, then proceed
                    if not self.haveToDispose():
                        break
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def endProcessingActions(self):
        activeObjectQueue=self.Res.users
        activeEntity=activeObjectQueue[0]
        self.printTrace(self.getActiveObjectQueue()[0].name, processEnd=self.objName)
        # reset the variables used to handle the interruptions timing 
        self.timeRestartingProcessing=0
        self.breakTime=0
        # output to trace that the processing in the Machine self.objName ended 
        try:
            self.outputTrace(activeObjectQueue[0].name,"ended processing in "+self.objName)
        except IndexError:
            pass
        # TODO: Not only Machines require time to process entities
        #     entities such as batchReassembly/Decomposition require time to process entities
        if activeEntity.family=='Entity':
            successorsAreMachines=True
            from Globals import G
            for object in self.next:
                if not object in G.MachineList:
                    successorsAreMachines=False
                    break
            if not successorsAreMachines:
                activeObjectQueue[0].hot = False
        from Globals import G
        if G.Router:
            # the just processed entity is added to the list of entities 
            # pending for the next processing
            G.pendingEntities.append(activeObjectQueue[0])
        # set the variable that flags an Entity is ready to be disposed 
        self.waitToDispose=True
        #do this so that if it is overtime working it is not counted as off-shift time
        if not self.onShift:
            self.timeLastShiftEnded=self.env.now
        # update the total working time 
        # the total processing time for this entity is what the distribution initially gave
        if not self.shouldPreempt:
            self.totalWorkingTime+=self.totalProcessingTimeInCurrentEntity
        # if the station was preemptied for a critical order then calculate the total working time accorindingly
        else:
            self.totalWorkingTime+=self.env.now-(self.timeLastEntityEntered)
        # update the variables keeping track of Entity related attributes of the machine    
        self.timeLastEntityEnded=self.env.now                          # this holds the time that the last entity ended processing in Machine 
        self.nameLastEntityEnded=self.currentEntity.name        # this holds the name of the last entity that ended processing in Machine
        self.completedJobs+=1                                   # Machine completed one more Job
        # reseting the shouldPreempt flag
        self.shouldPreempt=False
        # in case Machine just performed the last work before end of shift it should signal the ShiftScheduler
        if self.isWorkingOnTheLastBeforeOffShift:
            # find the ShiftSchedulerList
            mySS=None
            for SS in G.ShiftSchedulerList:
                if SS.victim==self:
                    mySS=SS
                    break
            # set the signal
            mySS.victimEndedLastProcessing.succeed()
            # reset the flag
            self.isWorkingOnTheLastBeforeOffShift=False
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def interruptionActions(self):
        activeObjectQueue=self.Res.users
        activeEntity=activeObjectQueue[0]
        self.printTrace(activeEntity.name, interrupted=self.objName)
        # if the interrupt occurred while processing an entity
        if not self.waitToDispose:
            # output to trace that the Machine (self.objName) got interrupted           
            try:                                                       
                self.outputTrace(activeObjectQueue[0].name, "Interrupted at "+self.objName)
            except IndexError:
                pass
            # recalculate the processing time left tinM
            self.tinM=self.tinM-(self.env.now-self.timeRestartingProcessing)
            if(self.tinM==0):       # sometimes the failure may happen exactly at the time that the processing would finish
                                    # this may produce disagreement with the simul8 because in both SimPy and Simul8
                                    # it seems to be random which happens 1st
                                    # this should not appear often to stochastic models though where times are random
                self.interruption=True
        # start counting the down time at breatTime dummy variable
        self.breakTime=self.env.now        # dummy variable that the interruption happened
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def postInterruptionActions(self):
        activeObjectQueue=self.Res.users
        activeEntity=activeObjectQueue[0]
        # if the machine returns from an failure while processing an entity
        if not self.waitToDispose:
            # use the timers to count the time that Machine is down and related 
            self.downTimeProcessingCurrentEntity+=self.env.now-self.breakTime      # count the time that Machine is down while processing this Entity
            self.downTimeInCurrentEntity+=self.env.now-self.breakTime              # count the time that Machine is down while on currentEntity
            self.timeLastFailureEnded=self.env.now                                 # set the timeLastFailureEnded
            self.failureTimeInCurrentEntity+=self.env.now-self.breakTime           # dummy variable keeping track of the failure time 
            # output to trace that the Machine self.objName was passivated for the current failure time
            self.outputTrace(activeObjectQueue[0].name, "passivated in "+self.objName+" for "+str(self.env.now-self.breakTime))
        # when a machine returns from failure while trying to deliver an entity
        else:
            # count the failure while on current entity time with failureTime variable
            self.failureTimeInCurrentEntity+=self.env.now-self.breakTime
            # calculate the time the Machine was down while trying to dispose the current Entity,
            # and the total down time while on current Entity
            self.downTimeInTryingToReleaseCurrentEntity+=self.env.now-self.breakTime
            self.downTimeInCurrentEntity+=self.env.now-self.breakTime        # already updated from failures during processing
            # update the timeLastFailureEnded
            self.timeLastFailureEnded=self.env.now
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
        activeObjectQueue=self.Res.users
        # if we have only one predecessor just check if there is a place and the machine is up
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(callerObject==None):
            if (self.operatorPool!='None' and (any(type=='Load' for type in self.multOperationTypeList)\
                                                    or any(type=='Setup' for type in self.multOperationTypeList))):
                return self.operatorPool.checkIfResourceIsAvailable()\
                        and self.checkIfMachineIsUp()\
                        and len(activeObjectQueue)<self.capacity\
                        and not self.entryIsAssignedTo()
            else:
                return self.checkIfMachineIsUp()\
                        and len(activeObjectQueue)<self.capacity\
                        and not self.entryIsAssignedTo()
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        if (self.operatorPool!='None' and (any(type=='Load' for type in self.multOperationTypeList)\
                                                or any(type=='Setup' for type in self.multOperationTypeList))):
            return self.operatorPool.checkIfResourceIsAvailable()\
                and self.checkIfMachineIsUp()\
                and len(activeObjectQueue)<self.capacity\
                and not self.entryIsAssignedTo()
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            return self.checkIfMachineIsUp()\
                and len(activeObjectQueue)<self.capacity\
                and (thecaller in self.previous)\
                and not self.entryIsAssignedTo()
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some possible giver waiting for it
    # also updates the giver to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        activeObjectQueue=self.Res.users
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        # check if there is a place, the machine is up and the predecessor has an entity to dispose. if the machine has to compete 
        # for an Operator that loads the entities onto it check if the predecessor if blocked by an other Machine. if not then the machine 
        # has to block the predecessor giverObject to avoid conflicts with other competing machines
        if (self.operatorPool!='None' and (any(type=='Load' for type in self.multOperationTypeList))):
            if giverObject.haveToDispose(self):
                if self.checkOperator()\
                    and self.checkIfActive() and len(activeObjectQueue)<self.capacity:
                    if not giverObject.exitIsAssignedTo():
                        giverObject.assignExitTo(self)
                    elif giverObject.exitIsAssignedTo()!=self:
                        return False
                    return True
            else:
                return False
        else:
            # the operator performs no load and the entity is received by the machine while there is 
            # no need for operators presence. The operator needs to be present only where the load Type 
            # operation is assigned
            if self.checkIfActive() and len(activeObjectQueue)<self.capacity\
                    and giverObject.haveToDispose(self):
                if not giverObject.exitIsAssignedTo():
                    giverObject.assignExitTo(self)
                elif giverObject.exitIsAssignedTo()!=self:
                    return False
                return True
    
    #===========================================================================
    # return whether Load or setup Requested
    #===========================================================================
    def isLoadRequested(self):
        return any(type=='Load' or type=='Setup' for type in self.multOperationTypeList)
    
    # =======================================================================
    # to be called by canAcceptAndIsRequested and check for the operator
    # =======================================================================    
    def checkOperator(self,callerObject=None):
        mayProceed=False
        if self.operatorPool.operators:
            # flag notifying that there is operator assigned to the actievObject
            self.assignedOperator=False
            # the operators operating the station
            operators=self.operatorPool.operators
            if self.operatorPool.checkIfResourceIsAvailable():
                for operator in [x for x in operators if x.checkIfResourceIsAvailable()]:
                    # if there are operators available not assigned to the station then the station may proceed signalling the Router
                    if not operator.isAssignedTo():
                        mayProceed=True
                    # if there are operators assigned to the station then proceed without invoking the Router
                    elif operator.isAssignedTo()==self:
                        self.assignedOperator=True
                        break
            return mayProceed or self.assignedOperator
        else:
            return True
    
    # =======================================================================
    # get an entity from the giver
    # =======================================================================
    def getEntity(self):
        activeEntity=CoreObject.getEntity(self)          # run the default method   
        # after the machine receives an entity, it must be removed from the pendingEntities list
        from Globals import G
        if G.Router:
            if activeEntity in G.pendingEntities:
                G.pendingEntities.remove(activeEntity)
        return activeEntity
  
    # =======================================================================
    # removes an entity from the Machine
    # =======================================================================
    def removeEntity(self, entity=None):
        activeEntity=CoreObject.removeEntity(self, entity)          # run the default method     
        self.waitToDispose=False                            # update the waitToDispose flag
        # if the Machine canAccept then signal a giver
        if self.canAccept():
            self.printTrace(self.id, attemptSignalGiver='(removeEntity)')
            self.signalGiver()
        return activeEntity
    
    # ======================================================================= 
    # checks if the Machine can dispose an entity to the following object
    # =======================================================================
    def haveToDispose(self, callerObject=None):
        activeObjectQueue=self.Res.users
        #if we have only one successor just check if machine waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(self.next)==1 or callerObject==None):
            return len(activeObjectQueue)>0 and self.waitToDispose and self.checkIfActive()
        thecaller=callerObject
        return len(activeObjectQueue)>0 and self.waitToDispose\
             and self.checkIfActive() and (thecaller in self.next)
    
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
    
            
    #===========================================================================
    # find candidate operators within the free operators
    #===========================================================================
    def findCandidateOperator(self):
        # TODO: this way no sorting is performed
        # find an available operator
        candidateOperator=self.operatorPool.findAvailableOperator()
        # append the station into its candidateStations
        candidateOperator.candidateStations.append(self)
        return candidateOperator
    
    #===========================================================================
    # checks whether the entity can proceed to a successor object
    #===========================================================================
    def canDeliver(self, entity=None):
        assert self.isInActiveQueue(entity), entity.id +' not in the internalQueue of'+ self.id
        activeEntity=entity
        
        from Globals import G
        router = G.Router
        # if the entity is in a machines who's broker waits for operator then
        if self in router.pendingMachines:
            activeEntity.proceed=True
            activeEntity.candidateReceivers.append(self)
            return True
        return False
    
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
        self.broker.invoke()
        self.toBeOperated = False
        
    # =======================================================================
    #       check if the machine is currently operated by an operator
    # =======================================================================
    def isOperated(self):
        return self.toBeOperated
    
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
        if self.interruptedBy:
            if self.onShift==False and self.interruptedBy=='ShiftScheduler':
                offShiftTimeInCurrentEntity=self.env.now-activeObject.timeLastShiftEnded

        # if there is an entity that finished processing in a Machine but did not get to reach 
        # the following Object till the end of simulation, 
        # we have to add this blockage to the percentage of blockage in Machine
        # we should exclude the failure time in current entity though!
        if (len(activeObjectQueue)>0) and (mightBeBlocked)\
             and ((activeObject.nameLastEntityEntered == activeObject.nameLastEntityEnded)) and self.onShift:
            # be careful here, might have to reconsider
            activeObject.totalBlockageTime+=self.env.now-(activeObject.timeLastEntityEnded+activeObject.downTimeInTryingToReleaseCurrentEntity)
            if activeObject.Up==False:
                activeObject.totalBlockageTime-=self.env.now-activeObject.timeLastFailure
                alreadyAdded=True

        #if Machine is currently processing an entity we should count this working time  
        if(len(activeObject.getActiveObjectQueue())>0)\
            and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered))\
            and (not (activeObject.operationType=='Processing' and (activeObject.currentOperator==None))):
            #if Machine is down we should add this last failure time to the time that it has been down in current entity 
            if self.Up==False:
#             if(len(activeObjectQueue)>0) and (self.Up==False):
                activeObject.downTimeProcessingCurrentEntity+=self.env.now-activeObject.timeLastFailure         
            activeObject.totalWorkingTime+=self.env.now-activeObject.timeLastEntityEntered\
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
                activeObject.downTimeProcessingCurrentEntity+=self.env.now-activeObject.timeLastFailure
            activeObject.totalTimeWaitingForOperator+=self.env.now-activeObject.timeWaitForOperatorStarted\
                                                           -activeObject.downTimeProcessingCurrentEntity\
                                                           -offShiftTimeInCurrentEntity
        # if Machine is down we have to add this failure time to its total failure time
        # we also need to add the last blocking time to total blockage time     
        if(activeObject.Up==False):
            activeObject.totalFailureTime+=self.env.now-activeObject.timeLastFailure
            # we add the value only if it hasn't already been added
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(self.env.now-activeObject.timeLastEntityEnded)-(self.env.now-activeObject.timeLastFailure)-activeObject.downTimeInTryingToReleaseCurrentEntity 
                alreadyAdded=True
        
        #if the machine is off shift,add this to the off-shift time
        # we also need to add the last blocking time to total blockage time  
        if activeObject.onShift==False:
            #add the time only if the object is interrupted because of off-shift
            if self.interruptedBy:
                if self.interruptedBy=='ShiftScheduler':
                    self.totalOffShiftTime+=self.env.now-self.timeLastShiftEnded 
            elif len(self.getActiveObjectQueue())==0 or self.waitToDispose:
                self.totalOffShiftTime+=self.env.now-self.timeLastShiftEnded 
            # we add the value only if it hasn't already been added
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(self.env.now-activeObject.timeLastEntityEnded)-(self.env.now-activeObject.timeLastShiftEnded)-offShiftTimeInCurrentEntity 
                
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

