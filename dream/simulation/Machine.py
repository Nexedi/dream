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
from SkilledOperatorRouter import SkilledRouter

from OperatedPoolBroker import Broker
from OperatorPool import OperatorPool

from RandomNumberGenerator import RandomNumberGenerator

# ===========================================================================
# the Machine object
# ===========================================================================
class Machine(CoreObject):
    family='Server'
    
    # =======================================================================
    # initialise the id the capacity, of the resource and the distribution
    # =======================================================================
    def __init__(self, id, name, capacity=1, processingTime=None,
                  repairman='None',\
                  operatorPool='None',operationType='None',\
                  setupTime=None, loadTime=None,
                  preemption={},
                  canDeliverOnInterruption=False, **kw):
        self.type="Machine"                         #String that shows the type of object
        CoreObject.__init__(self, id, name)
        from Globals import G

        processingTime=self.getOperationTime(time=processingTime)

        setupTime=self.getOperationTime(time=setupTime)

        loadTime=self.getOperationTime(time=loadTime)
        
        #     holds the capacity of the machine 
        self.capacity=capacity
        #     sets the repairman resource of the Machine
        self.repairman=repairman
        #     Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, processingTime)
        # check whether the operators are provided with a skills set
        # check whether the operators are provided with a skills set
        self.dedicatedOperator=self.checkForDedicatedOperators()
        if operatorPool and not (operatorPool=='None'):
            self.operatorPool=operatorPool
        else:
            if len(G.OperatorPoolsList)>0:
                for operatorPool in G.OperatorPoolsList:                    # find the operatorPool assigned to the machine
                    if(self.id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
                        machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
                                                                            # otherwise only one of them will be taken into account
                    else:
                        machineOperatorPoolList=[]                          # if there is no operatorPool assigned to the machine
            else:                                                           # then machineOperatorPoolList/operatorPool is a list
                machineOperatorPoolList=[]                                  # if there are no operatorsPool created then the 
                                                                            # then machineOperatorPoolList/operatorPool is a list
            if (type(machineOperatorPoolList) is list):                 # if the machineOperatorPoolList is a list
                                                                        # find the operators assigned to it and add them to the list
                for operator in G.OperatorsList:                        # check which operator in the G.OperatorsList
                    if(self.id in operator.coreObjectIds):                   # (if any) is assigned to operate
                        machineOperatorPoolList.append(operator)        # the machine with ID equal to id
            
            self.operatorPool=machineOperatorPoolList
        
        self.dedicatedOperator=self.checkForDedicatedOperators()
        # create an operatorPool if needed
        self.createOperatorPool(self.operatorPool)
        # holds the Operator currently processing the Machine
        self.currentOperator=None
        # define if load/setup/removal/processing are performed by the operator 
        self.operationType=operationType
        # boolean to check whether the machine is being operated
        self.toBeOperated = False
        # define the load times
        self.loadRng = RandomNumberGenerator(self, loadTime)
        # XX variable that informs on the need for setup
        self.setUp=True
        # define the setup times
        self.stpRng = RandomNumberGenerator(self, setupTime)
        # examine if there are multiple operation types performed by the operator
        #     there can be Setup/Processing operationType
        #     or the combination of both (MT-Load-Setup-Processing) 
        self.multOperationTypeList=[]   
        if isinstance(self.operationType, basestring) and self.operationType.startswith("MT"):
            OTlist = operationType.split('-')
            self.operationType=OTlist.pop(0)
            self.multOperationTypeList = OTlist
        else:
            self.multOperationTypeList.append(self.operationType)
 
        # flags used for preemption purposes
        self.isPreemptive=False
        self.resetOnPreemption=False
        if len(preemption)>0:
            self.isPreemptive=bool(int(preemption.get('isPreemptive') or 0))
            self.resetOnPreemption=bool(int(preemption.get('resetOnPreemption', 0)))
        # flag notifying that there is operator assigned to the actievObject
        self.assignedOperator=True
        # flag notifying the the station can deliver entities that ended their processing while interrupted
        self.canDeliverOnInterruption=canDeliverOnInterruption
        self.repairman='None'
        for repairman in G.RepairmanList:                   # check which repairman in the G.RepairmanList
            if(self.id in repairman.coreObjectIds):              # (if any) is assigned to repair 
                self.repairman=repairman                                 # the machine with ID equal to id
        G.MachineList.append(self)                             # add machine to global MachineList
        if self.operatorPool!="None":
            G.OperatedMachineList.append(self)                 # add the machine to the operatedMachines List
   
    # =======================================================================
    # initialize the machine
    # =======================================================================        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        
        # initialize the internal Queue (type Resource) of the Machine 
        self.Res=simpy.Resource(self.env, capacity=1)
        # initiate the Broker and the router
        self.createBroker()
        self.createRouter()
        # initialize the operator pool if any
        self.initializeOperatorPool()
        # initiate the Broker responsible to control the request/release
        self.initializeBroker()
        # initialise the router if not initialized already
        self.initializeRouter()
        
        # variables used for interruptions
        self.isProcessing=False
        # variable that shows what kind of operation is the station performing at the moment
        '''
            it can be Processing or Setup 
            XXX: others not yet implemented
        '''
        self.currentlyPerforming=None
        self.tinM=0
        self.timeLastProcessingStarted=0
        self.timeLastOperationStarted=-1
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
        # signal used for informing objectInterruption objects that the current entity processed has finished processnig
        self.endedLastProcessing=self.env.event()
        
        self.expectedSignals['isRequested']=1
        self.expectedSignals['interruptionEnd']=1
        self.expectedSignals['loadOperatorAvailable']=1
        self.expectedSignals['initialWIP']=1
        # events about the availability of process operator
        # TODO group those operator relate events
        self.processOperatorUnavailable=self.env.event()

    @staticmethod
    def getOperationTime(time):
        # XXX update time to comply with old definition
        '''returns the dictionary updated'''
        if not time:
            time = {'Fixed':{'mean': 0 }}
        if 'Normal' in time.keys() and\
                time['Normal'].get('max', None) is None:
            time['Normal']['max'] = float(time['Normal']['mean']) + 5 * float(time['Normal']['stdev'])
        return time
    
    #===========================================================================
    # create an operatorPool if needed
    #===========================================================================
    def createOperatorPool(self,operatorPool):
        ''' sets the operator resource of the Machine
             check if the operatorPool is a List or a OperatorPool type Object
             if it is a list then initiate a OperatorPool type object containing
             the list of operators provided
            if the  list is empty create operator pool with empty list
        '''
        from Globals import G
        # XXX operatorPool is not None ?
        # if a list of operators is provided as argument
        if (type(operatorPool) is list) and len(operatorPool)>0:
            id = self.id+'_OP'
            name=self.objName+'_operatorPool'
            self.operatorPool=OperatorPool(id, name, operatorsList=operatorPool)
            G.OperatorPoolsList.append(self.operatorPool)
        # if an operatorPool object is connected to the machine
        elif(type(operatorPool) is OperatorPool):
            self.operatorPool=operatorPool
        # otherwise
        else:
            # if there are operators with skillList
            if self.dedicatedOperator:
                id = self.id+'_OP'
                name=self.objName+'_operatorPool'
                self.operatorPool=OperatorPool(id,name,operatorsList=[])
                G.OperatorPoolsList.append(self.operatorPool)
            # otherwise create no operatorPool
            else:
                self.operatorPool='None'
        # update the operatorPool coreObjects list
        if self.operatorPool!='None':
             self.operatorPool.coreObjectIds.append(self.id)
             self.operatorPool.coreObjects.append(self)
    
    #===========================================================================
    # create broker if needed
    #===========================================================================
    def createBroker(self):
        # initiate the Broker and the router
        if (self.operatorPool!='None'):
            self.broker=Broker(operatedMachine=self)
    
    #===========================================================================
    # create router if needed
    #===========================================================================
    def createRouter(self):
        # initiate the Broker and the router
        if (self.operatorPool!='None'):
            from Globals import G
            # if there is no router
            if not G.Router:
                # TODO if the dedicatedOperator flag is raised then create a SkilledRouter (temp)
                if self.dedicatedOperator:
                    self.router=SkilledRouter()
                else:
                    self.router=Router()
                G.Router=self.router
            # otherwise set the already existing router as the machines Router
            else:
                self.router=G.Router
    #===========================================================================
    # initialise broker if needed
    #===========================================================================
    def initializeOperatorPool(self):
        # initialise the operator pool if any
        if (self.operatorPool!="None"):
            self.operatorPool.initialize()
            # if the flag dedicatedOperator is true then reset/empty the operators list of the pool
            if self.dedicatedOperator:
                self.operatorPool.operators=[]
            # otherwise update the coreObjectIds/coreObjects list of the operators
            else:
                for operator in self.operatorPool.operators:
                    operator.coreObjectIds.append(self.id)
                    operator.coreObjects.append(self)
    
    #===========================================================================
    # initialise broker if needed
    #===========================================================================
    def initializeBroker(self):
        # initiate the Broker responsible to control the request/release
        if (self.operatorPool!="None"):
            self.broker.initialize()
            self.env.process(self.broker.run())
                
    #===========================================================================
    # initialise router if needed
    #===========================================================================
    def initializeRouter(self):
        if (self.operatorPool!="None"):
            # initialise the router only once
            if not self.router.isInitialized:
                self.router.initialize()
            if not self.router.isActivated:
                self.env.process(self.router.run())
                self.router.isActivated=True
                
    #===========================================================================
    # get the initial operationTypes (setup/processing) : manual or automatic
    #===========================================================================
    def checkInitialOperationTypes(self):
        pass
    
    #===========================================================================
    # method controlling if there is a need to yield 
    #===========================================================================
    def shouldYield(self, operationTypes={}, methods={}):
        '''
            "methods":{'isInterrupted':'0'},
            "operationTypes"={"Processing":1,                % must
                               "Setup":0                   % must NOT
                             }
        '''
        operationsRequired=[]
        operationsNotRequired=[]
        opRequest=True
        if operationTypes:
            for operationType, func in operationTypes.iteritems():
                tup=(operationType, func)
                if bool(func):
                    operationsRequired.append(tup)
                else:
                    operationsNotRequired.append(tup)
            required = False
            if operationsRequired:
                for opTup in operationsRequired:
                    operation, func = opTup
                    required = required or (any(type==str(operation) for type in self.multOperationTypeList))
            else:
                required=True
            notRequired = False
            if operationsNotRequired:
                for opTup in operationsNotRequired:
                    operation, func = opTup
                    notRequired = notRequired or (any(type==str(operation) for type in self.multOperationTypeList))
            opRequest=required and not notRequired
        
        methodsRequired=[]
        methodsNotRequired=[]
        methodsRequest=True
        if methods:
            for methodType, func in methods.iteritems():
                tup=(methodType, func)
                if bool(func):
                    methodsRequired.append(tup)
                else:
                    methodsNotRequired.append(tup)
            required = True
            from Globals import getMethodFromName
            if methodsRequired:
                for methodTup in methodsRequired:
                    method, func = methodTup
                    objMethod=getMethodFromName('Dream.Machine.'+method)
                    required = required and (objMethod(self))
            notRequired = True
            if methodsNotRequired:
                for methodTup in methodsNotRequired:
                    method, func = methodTup
                    objMethod=getMethodFromName('Dream.Machine.'+method)
                    notRequired = notRequired and (objMethod(self))
            else:
                notRequired=False
            methodsRequest=required and not notRequired
        
        if (self.operatorPool!="None")\
             and opRequest\
             and methodsRequest:
            return True
        return False
    
    #===========================================================================
    # yielding the broker process for releasing the resource 
    #===========================================================================
    def release(self):
        # after getting the entity release the operator
        # machine has to release the operator
        self.releaseOperator()
        # wait until the Broker has finished processing
        self.expectedSignals['brokerIsSet']=1
        yield self.brokerIsSet
        transmitter, eventTime=self.brokerIsSet.value
        assert transmitter==self.broker, 'brokerIsSet is not sent by the stations broker'
        assert eventTime==self.env.now, 'brokerIsSet is not received on time'
        self.brokerIsSet=self.env.event()
    
    #===========================================================================
    # yielding the broker process for requesting an operator
    #===========================================================================
    def request(self):
        # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
        # machines waits to be operated (waits for the operator)
        self.requestOperator()
        # wait until the Broker has waited times equal to loadTime (if any)
        self.expectedSignals['brokerIsSet']=1
        yield self.brokerIsSet
        transmitter, eventTime=self.brokerIsSet.value
        assert transmitter==self.broker, 'brokerIsSet is not sent by the stations broker'
        assert eventTime==self.env.now, 'brokerIsSet is not received on time'
        self.brokerIsSet=self.env.event() 
    
    #===========================================================================
    # general process, it can be processing or setup
    #===========================================================================
    def operation(self,type='Processing'):
        # assert that the type is not None and is one of the already implemented ones
        assert type!=None, 'there must be an operation type defined'
        assert type in set(['Processing','Setup']), 'the operation type provided is not yet defined'
        # identify the method to get the operation time and initialise the totalOperationTime 
        if type=='Setup':
            self.totalOperationTime=self.totalSetupTime
        elif type=='Processing':
            self.totalOperationTime=self.totalWorkingTime
        # variables dedicated to hold the processing times, the time when the Entity entered, 
        # and the processing time left
        # get the operation time, tinMStarts holds the processing time of the machine
        self.totalOperationTimeInCurrentEntity=self.calculateTime(type)
        # timer to hold the operation time left
        self.tinM=self.totalOperationTimeInCurrentEntity    
        self.timeToEndCurrentOperation=self.env.now+self.tinM                                      
        # variables used to flag any interruptions and the end of the processing
        self.interruption=False
        # local variable that is used to check whether the operation is concluded
        operationNotFinished=True
        # if there is a failure that depends on the working time of the Machine
        # send it the victimStartsProcess signal                                            
        for oi in self.objectInterruptions:
            if oi.type=='Failure':
                if oi.deteriorationType=='working':
                    if oi.expectedSignals['victimStartsProcess']:
                        self.sendSignal(receiver=oi, signal=oi.victimStartsProcess)
        # this loop is repeated until the processing time is expired with no failure
        # check when the processingEndedFlag switched to false
        while operationNotFinished:
            self.expectedSignals['interruptionStart']=1
            self.expectedSignals['preemptQueue']=1
            self.expectedSignals['processOperatorUnavailable']=1
            # dummy variable to keep track of the time that the operation starts after every interruption
            
            # update timeLastOperationStarted both for Machine and Operator (if any)
            self.timeLastOperationStarted=self.env.now
            if self.currentOperator:
                self.currentOperator.timeLastOperationStarted=self.env.now
#             # if the type is setup then the time to record is timeLastProcessingStarted
#             if type=='Setup':
#                 self.timeLastSetupStarted=self.timeLastOperationStarted
#             # else if the type is processing then the time to record is timeLastProcessingStarted
#             elif type=='Processing':
#                 self.timeLastProcessingStarted=self.timeLastOperationStarted
            # processing starts, update the flags
            self.isProcessing=True
            self.currentlyPerforming=type
            # wait for the processing time left tinM, if no interruption occurs then change the processingEndedFlag and exit loop,
            #     else (if interrupted()) set interruption flag to true (only if tinM==0), 
            #     and recalculate the processing time left tinM, passivate while waiting for repair.
            # if a preemption has occurred then react accordingly (proceed with getting the critical entity)
            receivedEvent = yield self.env.any_of([self.interruptionStart, self.env.timeout(self.tinM), 
                                                   self.preemptQueue, self.processOperatorUnavailable])
            # if a failure occurs while processing the machine is interrupted.
            if self.interruptionStart in receivedEvent:
                transmitter, eventTime=self.interruptionStart.value
                assert eventTime==self.env.now, 'the interruption has not been processed on the time of activation'
                self.interruptionStart=self.env.event()
                self.interruptionActions(type)                      # execute interruption actions
                #===========================================================
                # # release the operator if there is interruption 
                #===========================================================
                if self.shouldYield(operationTypes={str(self.currentlyPerforming):1},methods={'isOperated':1}):
                    yield self.env.process(self.release())  
                # loop until we reach at a state that there is no interruption
                while 1:
                    self.expectedSignals['interruptionEnd']=1
                    yield self.interruptionEnd         # interruptionEnd to be triggered by ObjectInterruption
                    transmitter, eventTime=self.interruptionEnd.value
                    assert eventTime==self.env.now, 'the interruptionEnd was received later than anticipated'
                    self.interruptionEnd=self.env.event()
                    if self.Up and self.onShift:
                        break
                    self.postInterruptionActions()                      # execute interruption actions
                    #===========================================================
                    # # request a resource after the repair
                    #===========================================================
                    if self.shouldYield(operationTypes={str(self.currentlyPerforming):1}, methods={"isInterrupted":0}):
                        self.timeWaitForOperatorStarted = self.env.now
                        yield self.env.process(self.request())
                        self.timeWaitForOperatorEnded = self.env.now
                        self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
            # if the processing operator left
            elif self.processOperatorUnavailable in receivedEvent:
                transmitter, eventTime=self.processOperatorUnavailable.value
                assert self.env.now==eventTime, 'the operator leaving has not been processed at the time it should'   
                self.processOperatorUnavailable=self.env.event()                
                # carry interruption actions
                self.interruptionActions(type)
                #===========================================================
                # # release the operator  
                #===========================================================
                self.currentOperator.totalWorkingTime+=self.env.now-self.currentOperator.timeLastOperationStarted 
                yield self.env.process(self.release())                 
                from Globals import G
                # append the entity that was stopped to the pending ones
                if G.Router:
                    G.pendingEntities.append(self.currentEntity)
                #===========================================================
                # # request a resource after the interruption
                #===========================================================
                self.timeWaitForOperatorStarted = self.env.now
                yield self.env.process(self.request())
                self.timeWaitForOperatorEnded = self.env.now
                self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
                # carry post interruption actions
                self.postInterruptionActions() 
            
            
            # if the station is reactivated by the preempt method
            elif(self.shouldPreempt):
                if (self.preemptQueue in receivedEvent):
                    transmitter, eventTime=self.preemptQueue.value
                    assert eventTime==self.env.now, 'the preemption must be performed on the time of request'
                    self.preemptQueue=self.env.event()
                    self.interruptionActions(type)                      # execute interruption actions
                #===========================================================
                # # release the operator if there is interruption 
                #===========================================================
                if self.shouldYield(operationTypes={str(self.currentlyPerforming):1},methods={'isOperated':1}):
                    yield self.env.process(self.release())
                self.postInterruptionActions()                              # execute interruption actions
                break
            # if no interruption occurred the processing in M1 is ended 
            else:
                operationNotFinished=False
    
    # =======================================================================
    # the main process of the machine
    # =======================================================================
    def run(self):
        # request for allocation if needed
        from Globals import G
        self.initialAllocationRequest()
        # execute all through simulation time
        while 1:
            # waitEvent isRequested /interruptionEnd/loadOperatorAvailable
            while 1:
                self.printTrace(self.id, waitEvent='')
                
                self.expectedSignals['isRequested']=1
                self.expectedSignals['interruptionEnd']=1
                self.expectedSignals['loadOperatorAvailable']=1
                self.expectedSignals['initialWIP']=1
                
                receivedEvent = yield self.env.any_of([self.isRequested, self.interruptionEnd, 
                                                       self.loadOperatorAvailable, self.initialWIP])
                self.printTrace(self.id, received='')
                # if the machine can accept an entity and one predecessor requests it continue with receiving the entity
                if self.isRequested in receivedEvent:
                    transmitter, eventTime=self.isRequested.value
                    self.printTrace(self.id, isRequested=transmitter.id)
                    assert eventTime==self.env.now, 'isRequested was triggered earlier, not now'
                    assert transmitter==self.giver, 'the giver is not the requestingObject'
                    assert self.giver.receiver==self, 'the receiver of the signalling object in not the station'
                    # reset the signalparam of the isRequested event
                    self.isRequested=self.env.event()
                    break
                # if an interruption caused the control to be taken by the machine or
                # if an operator was rendered available while it was needed by the machine to proceed with getEntity
                if self.interruptionEnd in receivedEvent or self.loadOperatorAvailable in receivedEvent:
                    if self.interruptionEnd in receivedEvent:
                        transmitter, eventTime=self.interruptionEnd.value
                        assert eventTime==self.env.now, 'interruptionEnd received later than created'
                        self.printTrace(self.id, interruptionEnd=str(eventTime))
                        self.interruptionEnd=self.env.event()
                        # try to signal the Giver, otherwise wait until it is requested
                        if self.signalGiver():
                            # XXX cleaner implementation needed
                            # if there is skilled router the giver should also check
                            if G.Router:
                                if 'Skilled' in str(G.Router.__class__):
                                    continue
                            break
                    if self.loadOperatorAvailable in receivedEvent:
                        transmitter, eventTime=self.loadOperatorAvailable.value
                        assert eventTime==self.env.now,'loadOperatorAvailable received later than created'
                        self.printTrace(self.id,loadOperatorAvailable=str(eventTime))
                        self.loadOperatorAvailable=self.env.event()
                        # try to signal the Giver, otherwise wait until it is requested
                        if self.signalGiver():
                            # XXX cleaner implementation needed
                            # if there is router that is not skilled break
                            if G.Router:
                                if not 'Skilled' in str(G.Router.__class__):
                                    break
                            # else continue, the giver should also check
                            continue
                if self.initialWIP in receivedEvent:
                    transmitter, eventTime=self.initialWIP.value
                    assert transmitter==self.env, 'initialWIP was not sent by the Environment'
                    assert eventTime==self.env.now, 'initialWIP was not received on time'
                    self.initialWIP=self.env.event()
                    self.isProcessingInitialWIP=True
                    break
                    
            # TODO: maybe here have to assigneExit of the giver and add self to operator activeCallers list
                
            # here or in the getEntity (apart from the loadTimeCurrentEntity)
            # in case they are placed inside the getEntity then the initialize of
            # the corresponding variables should be moved to the initialize() of the CoreObject
            self.operatorWaitTimeCurrentEntity = 0
            self.loadOperatorWaitTimeCurrentEntity = 0
            self.loadTimeCurrentEntity = 0
            self.setupTimeCurrentEntity = 0
                      
            #===================================================================
            # #  request a resource if there is a need for load operation
            #===================================================================
            if self.shouldYield(operationTypes={"Load":1}):
                self.timeWaitForLoadOperatorStarted = self.env.now
                yield self.env.process(self.request())
                self.timeWaitForLoadOperatorEnded = self.env.now
                self.loadOperatorWaitTimeCurrentEntity += self.timeWaitForLoadOperatorEnded-self.timeWaitForLoadOperatorStarted
                self.totalTimeWaitingForLoadOperator += self.loadOperatorWaitTimeCurrentEntity 
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # loading
            #===================================================================
            #===================================================================
            #===================================================================
            
    # ======= Load the machine if the Load is defined as one of the Operators' operation types
            if any(type=="Load" for type in self.multOperationTypeList) and self.isOperated():
                self.timeLoadStarted = self.env.now
                yield self.env.timeout(self.calculateTime(type='Load'))
                # TODO: if self.interrupted(): There is the issue of failure during the Loading
                self.timeLoadEnded = self.env.now
                self.loadTimeCurrentEntity = self.timeLoadEnded-self.timeLoadStarted 
                self.totalLoadTime += self.loadTimeCurrentEntity
                
            #===================================================================
            #===================================================================
            #===================================================================
            # # # end loading
            #===================================================================
            #===================================================================
            #===================================================================
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # getting entity
            #===================================================================
            #===================================================================
            #===================================================================
            
            # get the entity 
                    # TODO: if there was loading time then we must solve the problem of getting an entity
                    # from an unidentified giver or not getting an entity at all as the giver 
                    # may fall in failure mode (assignExit()?)
            if not self.isProcessingInitialWIP:     # if we are in the state of having initial wip no need to take an Entity
                self.currentEntity=self.getEntity()
            else:
                # find out if the initialWIP requires manual operations (manual/setup)
                self.checkInitialOperationTypes()
            # TODO: the Machine receive the entity after the operator is available
            #     the canAcceptAndIsRequested method checks only in case of Load type of operation
            
            
            #===================================================================
            # # release a resource if the only operation type is Load
            #===================================================================
            if self.shouldYield(operationTypes={"Load":1, "Processing":0,"Setup":0},methods={'isOperated':1}):
                yield self.env.process(self.release())
            
            #===================================================================
            # # request a resource if it is not already assigned an Operator
            #===================================================================
            if self.shouldYield(operationTypes={"Setup":1,"Processing":1}, methods={"isOperated":0}):
                self.timeWaitForOperatorStarted = self.env.now
                yield self.env.process(self.request())
                self.timeWaitForOperatorEnded = self.env.now
                self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # setup
            #===================================================================
            #===================================================================
            #===================================================================
            # if the distribution is Fixed and the mean is zero then yield not
            if not (self.stpRng.mean==0 and self.stpRng.distributionType=='Fixed'):
                yield self.env.process(self.operation(type='Setup'))
                self.endOperationActions(type='Setup')
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # end setup
            #===================================================================
            #===================================================================
            #===================================================================
                
            #===================================================================
            # # release a resource at the end of setup
            #===================================================================
            if self.shouldYield(operationTypes={"Setup":1,"Load":1,"Processing":0},methods={'isOperated':1}):
                yield self.env.process(self.release())
            elif (self.currentOperator):
                if self.currentOperator.skillDict:
                    if not self.id in self.currentOperator.skillDict["process"]:
                        yield self.env.process(self.release())

            #===================================================================
            # # request a resource if it is not already assigned an Operator
            #===================================================================
            if self.shouldYield(operationTypes={"Processing":1}, methods={"isOperated":0}):
                self.timeWaitForOperatorStarted = self.env.now
                yield self.env.process(self.request())
                self.timeWaitForOperatorEnded = self.env.now
                self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
            
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # processing
            #===================================================================
            #===================================================================
            #===================================================================
            
            yield self.env.process(self.operation(type='Processing'))
            self.endOperationActions(type='Processing')
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # end of processing
            #===================================================================
            #===================================================================
            #===================================================================
            
            #===================================================================
            # # release resource after the end of processing
            #===================================================================
            if self.shouldYield(operationTypes={"Processing":1},methods={'isInterrupted':0, 'isOperated':1}):
                yield self.env.process(self.release())
            
            #===================================================================
            #===================================================================
            #===================================================================
            # # # disposing if not already emptied 
            #===================================================================
            #===================================================================
            #===================================================================
            
            # signal the receiver that the activeObject has something to dispose of
            if not self.signalReceiver():
            # if there was no available receiver, get into blocking control
                                
                while 1:
                    if not len(self.getActiveObjectQueue()):
                        break
                    self.expectedSignals['interruptionStart']=1
                    self.expectedSignals['canDispose']=1
                    self.timeLastBlockageStarted=self.env.now       # blockage is starting
                    # wait the event canDispose, this means that the station can deliver the item to successor
                    self.printTrace(self.id, waitEvent='(canDispose or interruption start)')
                    receivedEvent=yield self.env.any_of([self.canDispose , self.interruptionStart])
                    # if there was interruption
                    # TODO not good implementation
                    if self.interruptionStart in receivedEvent:
                        transmitter, eventTime=self.interruptionStart.value
                        assert eventTime==self.env.now, 'the interruption has not been processed on the time of activation'
                        self.interruptionStart=self.env.event()
                        # wait for the end of the interruption
                        self.interruptionActions()                          # execute interruption actions
                        # loop until we reach at a state that there is no interruption
                        while 1:
                            self.expectedSignals['interruptionEnd']=1
                            if not self.canDeliverOnInterruption:
                                receivedEvent=yield self.interruptionEnd         # interruptionEnd to be triggered by ObjectInterruption
                            # if the object canDeliverOnInterruption then it has to wait also for canDispose
                            else:
                                self.expectedSignals['canDispose']=1
                                receivedEvent=yield self.env.any_of([self.canDispose , self.interruptionEnd])
                            # if we have interruption end
                            if (self.interruptionEnd in receivedEvent) or (not self.canDeliverOnInterruption):    
                                transmitter, eventTime=self.interruptionEnd.value
                                assert eventTime==self.env.now, 'the victim of the failure is not the object that received it'
                                self.interruptionEnd=self.env.event()
                                # if there is no other interruption
                                if self.Up and self.onShift:
                                    # Machine is back to blocked state
                                    self.isBlocked=True
                                    break
                            # else signalReceiver and continue
                            elif (self.canDispose in receivedEvent) and self.canDeliverOnInterruption:
                                transmitter, eventTime=self.canDispose.value
                                if eventTime!=self.env.now:
                                    self.canDispose=self.env.event()
                                    continue
                                assert eventTime==self.env.now,'canDispose signal is late'
                                self.canDispose=self.env.event()
                                self.signalReceiver()
                                continue
                        self.postInterruptionActions()
                        if self.signalReceiver():
                            self.timeLastBlockageStarted=self.env.now
                            break
                        else:
                            continue
                    if self.canDispose in receivedEvent:
                        transmitter, eventTime=self.canDispose.value
                        if eventTime!=self.env.now:
                            self.canDispose=self.env.event()
                            continue
                        assert eventTime==self.env.now,'canDispose signal is late'
                        self.canDispose=self.env.event()
                        # try to signal a receiver, if successful then proceed to get an other entity
                        if self.signalReceiver():
                            break
                    # TODO: router most probably should signal givers and not receivers in order to avoid this hold,self,0
                    #       As the receiver (e.g.) a machine that follows the machine receives an loadOperatorAvailable event,
                    #       signals the preceding station (e.g. self.machine) and immediately after that gets the entity.
                    #       the preceding machine gets the canDispose signal which is actually useless, is emptied by the following station
                    #       and then cannot exit an infinite loop.
                    # notify that the station waits the entity to be removed
                    activeObjectQueue=self.getActiveObjectQueue()
                    if len(activeObjectQueue): 
                        self.waitEntityRemoval=True
                        self.printTrace(self.id, waitEvent='(entityRemoved)')
                        
                        self.expectedSignals['entityRemoved']=1
                        yield self.entityRemoved
                        transmitter, eventTime=self.entityRemoved.value
                        self.printTrace(self.id, entityRemoved=eventTime)
                        assert eventTime==self.env.now,'entityRemoved event activated earlier than received'
                        self.waitEntityRemoval=False
                        self.entityRemoved=self.env.event()
                        # if while waiting (for a canDispose event) became free as the machines that follows emptied it, then proceed
                        if not self.haveToDispose():
                            break
    
    #===========================================================================
    # actions to be performed after an operation (setup or processing)
    #===========================================================================
    def endOperationActions(self,type):
        activeObjectQueue=self.Res.users
        activeEntity=activeObjectQueue[0]
        # set isProcessing to False
        self.isProcessing=False
        # the machine is currently performing no operation
        self.currentlyPerforming=None
        # add working time
        self.totalOperationTime+=self.env.now-self.timeLastOperationStarted
        if type=='Processing':
            self.totalWorkingTime=self.totalOperationTime
        elif type=='Setup':
            self.totalSetupTime=self.totalOperationTime
        # reseting variables used by operation() process
        self.totalOperationTime=None
        self.timeLastOperationStarted=None
        # reseting flags
        self.shouldPreempt=False
        # reset the variables used to handle the interruptions timing 
        self.breakTime=0
        # update totalWorking time for operator and also print trace
        if self.currentOperator:
            operator=self.currentOperator
            self.outputTrace(operator.name, "ended a process in "+ self.objName)
            operator.totalWorkingTime+=self.env.now-operator.timeLastOperationStarted  
        # if the station has just concluded a processing turn then
        if type=='Processing':
            # blocking starts
            self.isBlocked=True
            self.timeLastBlockageStarted=self.env.now
            self.printTrace(self.getActiveObjectQueue()[0].name, processEnd=self.objName)
            # output to trace that the processing in the Machine self.objName ended 
            try:
                self.outputTrace(activeObjectQueue[0].name,"ended processing in "+self.objName)
            except IndexError:
                pass
            from Globals import G
            if G.Router:
                # the just processed entity is added to the list of entities 
                # pending for the next processing
                G.pendingEntities.append(activeObjectQueue[0])
            # set the variable that flags an Entity is ready to be disposed 
            self.waitToDispose=True
            # update the variables keeping track of Entity related attributes of the machine    
            self.timeLastEntityEnded=self.env.now                          # this holds the time that the last entity ended processing in Machine 
            self.nameLastEntityEnded=self.currentEntity.name        # this holds the name of the last entity that ended processing in Machine
            self.completedJobs+=1                                   # Machine completed one more Job# it will be used
            self.isProcessingInitialWIP=False
            # if there is a failure that depends on the working time of the Machine
            # send it the victimEndsProcess signal                                  
            for oi in self.objectInterruptions:
                if oi.type=='Failure':
                    if oi.deteriorationType=='working':
                        if oi.expectedSignals['victimEndsProcess']:
                            self.sendSignal(receiver=oi, signal=oi.victimEndsProcess)
            # in case Machine just performed the last work before the scheduled maintenance signal the corresponding object
            if self.isWorkingOnTheLast:
                # for the scheduled Object interruptions
                # XXX add the SkilledOperatorRouter to this list and perform the signalling only once
                for interruption in (G.ObjectInterruptionList):
                    # if the objectInterruption is waiting for a a signal
                    if interruption.victim==self and interruption.expectedSignals['endedLastProcessing']:
                        self.sendSignal(receiver=self, signal=self.endedLastProcessing)
                        interruption.waitingSignal=False
                        self.isWorkingOnTheLast=False
                # set timeLastShiftEnded attribute so that if it is overtime working it is not counted as off-shift time
                if self.interruptedBy=='ShiftScheduler':
                    self.timeLastShiftEnded=self.env.now

    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def interruptionActions(self, type='Processing'):
        # if object was processing add the working time
        # only if object is not preempting though
        # in case of preemption endProcessingActions will be called
        if self.isProcessing and not self.shouldPreempt:
            self.totalOperationTime+=self.env.now-self.timeLastOperationStarted
            if type=='Processing':
                self.totalWorkingTime=self.totalOperationTime
            elif type=='Setup':
                self.totalSetupTime=self.totalOperationTime
        # if object was blocked add the working time
        if self.isBlocked:
            self.addBlockage()
        # the machine is currently performing nothing
        self.currentlyPerforming=None
        activeObjectQueue=self.Res.users
        if len(activeObjectQueue):
            activeEntity=activeObjectQueue[0]
            self.printTrace(activeEntity.name, interrupted=self.objName)                                    
            self.outputTrace(activeObjectQueue[0].name, "Interrupted at "+self.objName)
            # recalculate the processing time left tinM
            if self.timeLastOperationStarted>=0:
                self.tinM=self.tinM-(self.env.now-self.timeLastOperationStarted)
                self.timeToEndCurrentOperation=self.env.now+self.tinM
                if(self.tinM==0):       # sometimes the failure may happen exactly at the time that the processing would finish
                                        # this may produce disagreement with the simul8 because in both SimPy and Simul8
                                        # it seems to be random which happens 1st
                                        # this should not appear often to stochastic models though where times are random
                    self.interruption=True
        # start counting the down time at breatTime dummy variable
        self.breakTime=self.env.now        # dummy variable that the interruption happened
        # set isProcessing to False          
        self.isProcessing=False
        # set isBlocked to False          
        self.isBlocked=False
    
    #===========================================================================
    # returns true if the station is interrupted
    #===========================================================================
    def isInterrupted(self):
        return self.interruption
    
    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # =======================================================================    
    def postInterruptionActions(self):
        activeObjectQueue=self.Res.users
        if len(activeObjectQueue):
            activeEntity=activeObjectQueue[0]
        # if the machine is empty signal giver
        else:
            self.signalGiver()
        # if the machine returns from an failure while processing an entity
        if not self.waitToDispose:
            # use the timers to count the time that Machine is down and related
            self.timeLastFailureEnded=self.env.now                                 # set the timeLastFailureEnded
            # output to trace that the Machine self.objName was passivated for the current failure time
            if len(activeObjectQueue):
                self.outputTrace(activeObjectQueue[0].name, "passivated in "+self.objName+" for "+str(self.env.now-self.breakTime))
        # when a machine returns from failure while trying to deliver an entity
        else:
            # calculate the time the Machine was down while trying to dispose the current Entity,
            # and the total down time while on current Entity
            self.downTimeInTryingToReleaseCurrentEntity+=self.env.now-self.breakTime
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
        if self.isLocked:
            return False
        activeObjectQueue=self.Res.users
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        if (self.operatorPool!='None' and (any(type=='Load' for type in self.multOperationTypeList)\
                                                or any(type=='Setup' for type in self.multOperationTypeList))):
            return self.operatorPool.checkIfResourceIsAvailable()\
                and self.checkIfMachineIsUp()\
                and len(activeObjectQueue)<self.capacity\
                and self.isInRouteOf(thecaller)\
                and not self.entryIsAssignedTo()
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            return self.checkIfMachineIsUp()\
                and len(activeObjectQueue)<self.capacity\
                and self.isInRouteOf(thecaller)\
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
                    # if the exit of the object is already assigned somewhere else, return false
                    if giverObject.exitIsAssignedTo() and giverObject.exitIsAssignedTo()!=self:
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
                # if the exit of the object is already assigned somewhere else, return false
                if giverObject.exitIsAssignedTo() and giverObject.exitIsAssignedTo()!=self:
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
        if(callerObject==None):
            return len(activeObjectQueue)>0\
               and self.waitToDispose\
               and (self.canDeliverOnInterruption
                    or self.timeLastEntityEnded==self.env.now
                    or self.checkIfActive())
        thecaller=callerObject
        return len(activeObjectQueue)>0\
             and self.waitToDispose\
             and thecaller.isInRouteOf(self)\
             and (self.canDeliverOnInterruption
                  or self.timeLastEntityEnded==self.env.now
                  or self.checkIfActive())
    
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
        # this checks if the operator is working on the last element. 
        # If yes the time that he was set off-shift should be updated
        operator=self.currentOperator
        operator.schedule[-1].append(self.env.now)
        if not self.currentOperator.onShift:
            operator.timeLastShiftEnded=self.env.now      
            operator.unAssign()     # set the flag operatorAssignedTo to None     
            operator.workingStation=None  
            self.outputTrace(operator.name, "released from "+ self.objName)
        # XXX in case of skilled operators which stay at the same station should that change
        elif not operator.operatorDedicatedTo==self:
            operator.unAssign()     # set the flag operatorAssignedTo to None
            operator.workingStation=None
            self.outputTrace(operator.name, "released from "+ self.objName)
            # if the Router is expecting for signal send it
            from Globals import G
            from SkilledOperatorRouter import SkilledRouter
            if G.Router.__class__ is SkilledRouter:
                if G.Router.expectedFinishSignals:
                    if self.id in G.Router.expectedFinishSignalsDict:
                        signal=G.Router.expectedFinishSignalsDict[self.id]
                        self.sendSignal(receiver=G.Router, signal=signal)
        self.broker.invoke()
        self.toBeOperated = False
        
    # =======================================================================
    #       check if the machine is currently operated by an operator
    # =======================================================================
    def isOperated(self):
        return self.toBeOperated
    
    # =======================================================================    
    # outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        json = {'_class': 'Dream.%s' % self.__class__.__name__,
                'id': self.id,
                'family': self.family,
                'results': {}}
        json['results']['failure_ratio'] = self.Failure
        json['results']['working_ratio'] = self.Working
        json['results']['blockage_ratio'] = self.Blockage
        json['results']['waiting_ratio'] = self.Waiting
        json['results']['off_shift_ratio'] = self.OffShift
        json['results']['setup_ratio'] = self.SettingUp
        json['results']['loading_ratio'] = self.Loading

        G.outputJSON['elementList'].append(json)

