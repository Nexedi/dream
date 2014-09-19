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
Created on 19 Feb 2013

@author: Ioannis
'''
'''
Models an Interruption that schedules the operation of the machines by different managers
'''
import simpy

from ObjectInterruption import ObjectInterruption

# ===========================================================================
#               Class that handles the Operator Behavior
# ===========================================================================
class Router(ObjectInterruption):
    
    # =======================================================================
    #   according to this implementation one machine per broker is allowed
    #     The Broker is initiated within the Machine and considered as 
    #                black box for the ManPy end Developer
    # TODO: we should maybe define a global schedulingRule criterion that will be 
    #         chosen in case of multiple criteria for different Operators
    # ======================================================================= 
    def __init__(self,sorting=False):
        ObjectInterruption.__init__(self)
        self.type = "Router"
        self.isInitialized=False
        self.isActivated=False
        self.candidateOperators=[]
        # boolean flag to check whether the Router should perform sorting on operators and on pendingEntities
        self.sorting=sorting
        # list of objects to be signalled by the Router
        self.toBeSignalled=[]
        # flag to notify whether the router is already invoked
        self.invoked=False
        
        self.preemptiveOperators=[]                  # list of preemptiveOperators that should preempt their machines
        
        self.conflictingOperators=[]                 # list with the operators that have candidateEntity with conflicting candidateReceivers
        self.conflictingEntities=[]                  # entities with conflictingReceivers
        self.conflictingStations=[]                  # stations with conflicting operators
        self.occupiedReceivers=[]                    # occupied candidateReceivers of a candidateEntity
        
        self.criticalQueues=[]
        
    #===========================================================================
    #                         the initialize method
    #===========================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        # signal used to initiate the generator of the Router
        self.isCalled=self.env.event()
        # list that holds all the objects that can receive
#         self.pendingObjects=[]
        self.pendingMachines=[]
        self.pendingQueues=[]
#         self.calledOperator=[]
        # list of the operators that may handle a machine at the current simulation time
        self.candidateOperators=[]
        # flag used to check if the Router is initialised
        self.isInitialized=True
        
        self.invoked=False
        
        self.preemptiveOperators=[]
        
        self.toBeSignalled=[]
        self.conflictingOperators=[]
        self.conflictingEntities=[]
        self.conflictingStations=[]
        self.occupiedReceivers=[]
        
        self.criticalQueues=[]
        
    # =======================================================================
    #                          the run method
    # =======================================================================
    '''
    after the events are over, assign the operators to machines for loading or simple processing
    read the pendingEntities currentStations, these are the stations (queues) that may be signalled
    '''
    def run(self):
        while 1:
            # wait until the router is called
            
            self.expectedSignals['isCalled']=1
            
            yield self.isCalled

            transmitter, eventTime=self.isCalled.value
            self.isCalled=self.env.event()
            self.printTrace('','=-'*15)
            self.printTrace('','router received event')
            # wait till there are no more events, the machines must be blocked
            while 1:
                if self.env.now==self.env.peek():
                    self.printTrace('', 'there are MORE events for now')
                    yield self.env.timeout(0)
                else:
                    self.printTrace('','there are NO more events for now')
                    break
            self.printTrace('','=-'*15)
            # entry actions
            self.entry()
            # run the routine that allocates operators to machines
            self.allocateOperators()
            # assign operators to stations
            self.assignOperators()
            # unAssign exits
            self.unAssignExits()
            # signal the stations that ought to be signaled
            self.signalOperatedStations()
            self.printTrace('', 'router exiting')
            self.printTrace('','=-'*20)
            # exit actions
            self.exit()
    
    def allocateOperators(self):
        # find the pending objects
        self.findPending()
        # find the operators that can start working now 
        self.findCandidateOperators()
        # sort the operators according to their idle time
        self.sortOperators()
        # find working stations for the candidate operators
        self.findStationsForOperators()
        
#         # find the operators candidateEntities
#         self.sortCandidateEntities()
#         # find the entity that will occupy the resource, and the station that will receive it (if any available)
#         #  entities that are already in stations have already a receiver
#         self.findCandidateReceivers()
    
    #===========================================================================
    # unassigns exits of queues that are not to be signalled 
    #===========================================================================
    def unAssignExits(self):
        # un-assign exits of objects previous to objects to be operated by operators 
        #     while their exit is not assigned to the object the operator will operate 
        for operator in [x for x in self.candidateOperators if x.isAssignedTo()]:
            if not operator.isAssignedTo() in list(self.pendingMachines+self.pendingQueues):
                for object in [x for x in operator.isAssignedTo().previous if x.exitIsAssignedTo()]:
                    if object.exitIsAssignedTo()!=operator.isAssignedTo():
                        object.unAssignExit()
        # if an object cannot proceed with getEntity, unAssign the exit of its giver
        for object in self.pendingQueues:
            if not object in self.toBeSignalled:
                object.unAssignExit()
    
    #===========================================================================
    # assigning operators to machines
    #===========================================================================
    def assignOperators(self):
        # for all the operators that are requested
        for operator in self.candidateOperators:
            if operator.candidateStation:
                
                # check if the candidateOperators are available, if the are requested and reside in the pendingObjects list
                if operator.checkIfResourceIsAvailable():
                    # assign an operator to the priorityObject
                    self.printTrace('router', 'will assign '+operator.id+' to '+operator.candidateStation.id)
                    operator.assignTo(operator.candidateStation)
                    if not operator.candidateStation in self.toBeSignalled:
                        self.toBeSignalled.append(operator.candidateStation)
                # if there must be preemption performed
                elif operator in self.preemptiveOperators:
                    # if the operator is not currently working on the candidateStation then the entity he is
                    #     currently working on must be preempted, and he must be unassigned and assigned to the new station
                    if operator.workingStation!=operator.candidateStation:
                        operator.unAssign()
                        self.printTrace('router', ' will assign'+operator.id+'to'+operator.candidateStation.id)
                        operator.assignTo(operator.candidateStation)
                    if not operator.candidateStation in self.toBeSignalled:
                        self.toBeSignalled.append(operator.candidateStation)
        self.printTrace('objects to be signaled:'+' '*11, [str(object.id) for object in self.toBeSignalled])
    
    def entry(self):
        from Globals import G
        for operator in G.OperatorsList:
            operator.candidateEntity=None
    
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exit(self):
        from Globals import G
        # reset the variables that are used from the Router
        for operator in self.candidateOperators:
            operator.candidateEntities=[]
            operator.candidateStations=[]
            operator.candidateStation=None
#             operator.candidateEntity=None
        for entity in G.pendingEntities:
            entity.proceed=False
            entity.candidateReceivers=[]
            entity.candidateReceiver=None    
        del self.candidateOperators[:]
        del self.preemptiveOperators[:]
        del self.pendingMachines[:]
        del self.pendingQueues[:]
        del self.toBeSignalled[:]
        del self.conflictingOperators[:]
        del self.conflictingStations[:]
        del self.conflictingEntities[:]
        del self.occupiedReceivers[:]
        del self.criticalQueues[:]
        self.invoked=False
    
    
    #===========================================================================
    # signal stations that wait for load operators
    #===========================================================================
    def signalOperatedStations(self):
        from Globals import G
        for operator in self.candidateOperators:
            station=operator.isAssignedTo()
            if station:
                assert station in self.toBeSignalled, 'the station must be in toBeSignalled list'
                # if the operator is preemptive
                if operator in self.preemptiveOperators:
                    # if not assigned to the station currently working on, then preempt both stations
                    if station!=operator.workingStation:
                        # preempt operators currentStation
                        operator.workingStation.shouldPreempt=True
                        self.printTrace('router', 'preempting '+operator.workingStation.id+'.. '*6)
                        operator.workingStation.preempt()
                        operator.workingStation.timeLastEntityEnded=self.env.now     #required to count blockage correctly in the preemptied station
                    station.shouldPreempt=True
                    self.printTrace('router', 'preempting receiver '+station.id+'.. '*6)
                    station.preempt()
                    station.timeLastEntityEnded=self.env.now     #required to count blockage correctly in the preemptied station
                elif station.broker.waitForOperator:
                    # signal this station's broker that the resource is available
                    if station.broker.expectedSignals['resourceAvailable']:
                        self.sendSignal(receiver=station.broker, signal=station.broker.resourceAvailable)
                        self.printTrace('router', 'signalling broker of'+' '*50+operator.isAssignedTo().id)
                else:
                    # signal the queue proceeding the station
                    if station.canAccept()\
                            and any(type=='Load' for type in station.multOperationTypeList):
                        if station.expectedSignals['loadOperatorAvailable']:
                            self.sendSignal(receiver=station, signal=station.loadOperatorAvailable)
                            self.printTrace('router', 'signalling'+' '*50+operator.isAssignedTo().id)
    
    #===========================================================================
    # find the stations that can be signalled by the router and the entities that are requesting operators now
    #===========================================================================
    def findPending(self):
        from Globals import G
        self.pending=[]             # list of entities that require operators now
        for entity in G.pendingEntities:
            if entity.currentStation in G.MachineList:
                if entity.currentStation.broker.waitForOperator:
                    self.pendingMachines.append(entity.currentStation)
                    self.pending.append(entity)
            for machine in entity.currentStation.next:
                if machine in G.MachineList:
                    if any(type=='Load' for type in machine.multOperationTypeList) and not entity.currentStation in self.pendingQueues:
                        self.pendingQueues.append(entity.currentStation)
                        self.pending.append(entity)
                        break
        # figure out which queues are holding critical pending entities 
        self.findCriticalQueues()
        self.printTrace('pendingMachines'+'-'*19+'>', [str(object.id) for object in self.pendingMachines])
        self.printTrace('pendingQueues'+'-'*21+'>', [str(object.id) for object in self.pendingQueues])
        self.printTrace('found pending entities'+'-'*12+'>', [str(entity.id) for entity in self.pending if not entity.type=='Part'])
    
    #===========================================================================
    # find the pending queues that hold critical pending entities 
    #===========================================================================
    def findCriticalQueues(self):
        for queue in self.pendingQueues:
            for entity in queue.getActiveObjectQueue():
                if entity in self.pending and entity.isCritical:
                    self.criticalQueues.append(queue)
    
    #========================================================================
    # Find candidate Operators
    # find the operators that can start working now even if they are not called
    #     to be found:
    #     .    the candidate operators
    #     .    their candidate entities (the entities they will process)
    #     .    the candidate receivers of the entities (the stations the operators will be working at)
    #========================================================================
    def findCandidateOperators(self):
        # find stations that may be candidates
        candidateMachines = [next for queue in self.pendingQueues for next in queue.findReceiversFor(queue)]
        # for each pendingMachine
        for station in candidateMachines+self.pendingMachines:
            # find candidateOperators for each object 
            candidateOperators=station.operatorPool.availableOperators()
            if candidateOperators:	# if there was an operator found append the Machine on his candidateStations
                for candidateOperator in candidateOperators:
                    if not station in candidateOperator.candidateStations:
                        candidateOperator.candidateStations.append(station)
            # if there is candidateOperator that is not already in self.candidateOperators add him
            # TODO: this way no sorting is performed
                    if not candidateOperator in self.candidateOperators:
                        self.candidateOperators.append(candidateOperator)
        # if there are critical pending entities then populate the candidateOperators list with preemptiveOperators
        self.findPreemptiveOperators()

        # if there are candidate operators
        if self.candidateOperators:
            self.printTrace('router found candidate operators'+' '*3,
                            [(operator.id, [station.id for station in operator.candidateStations]) for operator in self.candidateOperators])
        else:    
            self.printTrace('router', 'found NO candidate operators')
            
    #===========================================================================
    # find operators that can perform preemption for a critical pending entity
    #===========================================================================
    def findPreemptiveOperators(self):
        # for every queue that holds critical pending entities
        for queue in self.criticalQueues:
            # if no receivers can be found
            if not queue.findReceiversFor(queue):
                # for each of the following objects
                for nextobject in queue.next:
                    # if an operator is occupied by a critical entity then that operator can preempt
                    # This way the first operator that is not currently on a critical entity is invoked
                    # TODO: consider picking an operator more wisely by sorting
                    for operator in nextobject.operatorPool.operators:
                        currentStation=operator.workingStation
                        if not currentStation.getActiveObjectQueue()[0].isCritical:
                            preemptiveOperator=operator
                            preemptiveOperator.candidateStations.append(nextobject)
                            if not preemptiveOperator in self.candidateOperators:
                                self.candidateOperators.append(preemptiveOperator)
                                self.preemptiveOperators.append(preemptiveOperator)
                            break
    
    #=======================================================================
    # Sort candidateOperators
    # sort the operators according to their idle time
    #=======================================================================
    def sortOperators(self): 
        if self.candidateOperators:
            for op in self.candidateOperators:
                op.criterion=0
                if op.schedule:
                    op.criterion=self.env.now-op.schedule[-1][-1]
            # sort according to the time they concluded their last operation
            self.candidateOperators.sort(key=lambda x: x.criterion, reverse=True)
            
            
    #===========================================================================
    # find working stations for the candidateOperators
    #===========================================================================
    def findStationsForOperators(self):
        occupiedEntities=[]
        occupiedStations=[]
        for operator in self.candidateOperators:
            # first sort the candidateStations according to their waiting time
            operator.sortStations()
            
            # then find all the candidateEntities
            operator.candidateEntities=[]
            for station in operator.candidateStations:
                if station in self.pendingMachines and not station in occupiedStations:
                    if station.currentEntity in self.pending and not station.currentEntity in occupiedEntities:
                        operator.candidateEntities.append(station.currentEntity)
                else:
                    for predecessor in station.previous:
                        if predecessor in self.pendingQueues and not station in occupiedStations:
                            operator.candidateEntities+=[x for x in predecessor.getActiveObjectQueue()
                                                       if x in self.pending and not x in occupiedEntities]
            
            # sort candidateEntities according to the scheduling rule of the operator
            operator.sortEntities()
            # if the operator is of the preemptives then there is a need to sort for critical orders
            if operator in self.preemptiveOperators:
                operator.candidateEntities.sort(key=lambda x: x.isCritical, reverse=False)
            
            # pick an entity and a station
            if operator.candidateEntities:
                operator.candidateEntity=operator.candidateEntities[0]
            
                # if the entities currentStation is machine
                if operator.candidateEntity.currentStation in self.pendingMachines:
                    operator.candidateStation=operator.candidateEntity.currentStation
                elif operator.candidateEntity.currentStation in self.pendingQueues:
                    for station in operator.candidateStations:
                        if station in operator.candidateEntity.currentStation.next:
                            operator.candidateStation=station
                            break
                occupiedStations.append(operator.candidateStation)
                occupiedEntities.append(operator.candidateEntity)
    
    #=======================================================================
    #         Find the candidateEntities for each candidateOperator
    # find the candidateEntities of each candidateOperator and sort them according
    #     to the scheduling rules of the operator and choose an entity that will be served
    #     and by which machines
    #=======================================================================
    def sortCandidateEntities(self):
        from Globals import G
        # sort the candidateEntities list of each operator according to its schedulingRule
        for operator in [x for x in self.candidateOperators if x.candidateStations]:
            operator.sortCandidateEntities()
         

    
    #===========================================================================
    # get all the candidate stations that have been chosen by an operator
    #===========================================================================
    def getReceivers(self):
        candidateStations=[]
        for operator in self.candidateOperators:
            if operator.candidateStation:
                if not operator.candidateStation in candidateStations:
                    candidateStations.append(operator.candidateStation)
        return candidateStations 
    
    #=======================================================================
    # Find candidate entities and their receivers
    # TODO: if there is a critical entity, its manager should be served first
    # TODO: have to sort again after choosing candidateEntity
    #=======================================================================
    def findCandidateReceivers(self):
        # finally we have to sort before giving the entities to the operators
        # If there is an entity which must have priority then it should be assigned first
        # TODO: sorting after choosing candidateEntity
        # for the candidateOperators that do have candidateEntities pick a candidateEntity
        for operator in [x for x in self.candidateOperators if x.candidateStations]:
            # find the first available entity that has no occupied receivers
            operator.candidateStation = operator.findCandidateStation()
        
        # find the resources that are 'competing' for the same station
        if not self.sorting:
            # if there are entities that have conflicting receivers
            if len(self.conflictingStations):
                self.conflictingOperators=[operator for operator in self.candidateOperators\
                                            if operator.candidateStation in self.conflictingStations]
            # keep the sorting provided by the queues if there is conflict between operators
            conflictingGroup=[]                     # list that holds the operators that have the same recipient
            removedOperators=[]
            if self.conflictingOperators:
                # for each of the candidateReceivers
                for station in self.conflictingStations:
                    # find the group of operators that compete for this station
                    conflictingGroup=[operator for operator in self.conflictingOperators if operator.candidateStation==station]
                    # the operator that can proceed is the manager of the entity as sorted by the queue that holds them
                    conflictingGroup.sort()
                    # the operators that are not first in the list cannot proceed
                    for operator in conflictingGroup:
                        if conflictingGroup.index(operator)!=0 and not operator in removedOperators:
                            self.candidateOperators.remove(operator)
                            removedOperators.append(operator)
         
    # =======================================================================
    #    sorts the Operators of the Queue according to the scheduling rule
    # =======================================================================
    def activeQSorter(self, criterion=None, candList=[]):
        activeObjectQ=candList
        if not activeObjectQ:
            assert False, "empty candidateOperators list"
        if criterion==None:
            criterion=self.multipleCriterionList[0]
        #if the schedulingRule is first in first out
        if criterion=="FIFO":
            # FIFO sorting has no meaning when sorting candidateEntities
            self.activeQSorter(criterion='WT',candList=activeObjectQ)
        #if the schedulingRule is based on a pre-defined priority
        elif criterion=="Priority":
            # if the activeObjectQ is a list of entities then perform the default sorting
            try:
                activeObjectQ.sort(key=lambda x: x.priority)
            # if the activeObjectQ is a list of operators then sort them according to their candidateEntities
            except:
                activeObjectQ.sort(key=lambda x: x.candidateEntity.priority)
        #if the scheduling rule is time waiting (time waiting of machine
        # TODO: consider that the timeLastEntityEnded is not a 
        #     indicative identifier of how long the station was waiting
        elif criterion=='WT':
            try:
                activeObjectQ.sort(key=lambda x: x.schedule[-1][1])
            except:
                activeObjectQ.sort(key=lambda x: x.candidateEntity.schedule[-1][1])
        #if the schedulingRule is earliest due date
        elif criterion=="EDD":
            try:
                activeObjectQ.sort(key=lambda x: x.dueDate)
            except:
                activeObjectQ.sort(key=lambda x: x.candidateEntity.dueDate)
        #if the schedulingRule is earliest order date
        elif criterion=="EOD":
            try:
                activeObjectQ.sort(key=lambda x: x.orderDate)
            except:
                activeObjectQ.sort(key=lambda x: x.candidateEntity.orderDate)
        #if the schedulingRule is to sort Entities according to the stations they have to visit
        elif criterion=="NumStages":
            try:
                activeObjectQ.sort(key=lambda x: len(x.remainingRoute), reverse=True)
            except:
                activeObjectQ.sort(key=lambda x: len(x.candidateEntity.remainingRoute), reverse=True)
        #if the schedulingRule is to sort Entities according to the their remaining processing time in the system
        elif criterion=="RPC":
            try:
                for entity in activeObjectQ:
                    RPT=0
                    for step in entity.remainingRoute:
                        processingTime=step.get('processingTime',None)
                        if processingTime:
                            RPT+=float(processingTime.get('mean',0))
                    entity.remainingProcessingTime=RPT
                activeObjectQ.sort(key=lambda x: x.remainingProcessingTime, reverse=True)
            except:
                for entity in [operator.candidateEntity for operator in activeObjectQ]:
                    RPT=0
                    for step in entity.remainingRoute:
                        processingTime=step.get('processingTime',None)
                        if processingTime:
                            RPT+=float(processingTime.get('mean',0))
                    entity.remainingProcessingTime=RPT
                activeObjectQ.sort(key=lambda x: x.candidateEntity.remainingProcessingTime, reverse=True)
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            try:
                for entity in activeObjectQ:
                    processingTime = entity.remainingRoute[0].get('processingTime',None)
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                    if processingTime:
                        entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                    else:
                        entity.processingTimeInNextStation=0
                activeObjectQ.sort(key=lambda x: x.processingTimeInNextStation, reverse=True)
            except:
                for entity in [operator.candidateEntity for operator in activeObjectQ]:
                    processingTime = entity.remainingRoute[0].get('processingTime',None)
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                    if processingTime:
                        entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                    else:
                        entity.processingTimeInNextStation=0
                activeObjectQ.sort(key=lambda x: x.candidateEntity.processingTimeInNextStation, reverse=True)
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        elif criterion=="SPT":
            try:
                for entity in activeObjectQ:
                    processingTime = entity.remainingRoute[0].get('processingTime',None)
                    if processingTime:
                        entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                    else:
                        entity.processingTimeInNextStation=0
                activeObjectQ.sort(key=lambda x: x.processingTimeInNextStation)
            except:
                for entity in [operator.candidateEntity for operator in activeObjectQ]:
                    processingTime = entity.remainingRoute[0].get('processingTime',None)
                    if processingTime:
                        entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                    else:
                        entity.processingTimeInNextStation=0
                activeObjectQ.sort(key=lambda x: x.candidateEntity.processingTimeInNextStation)
        #if the schedulingRule is to sort Entities based on the minimum slackness
        elif criterion=="MS":
            try:
                for entity in activeObjectQ:
                    RPT=0
                    for step in entity.remainingRoute:
                        processingTime=step.get('processingTime',None)
                        if processingTime:
                            RPT+=float(processingTime.get('mean',0))
                    entity.remainingProcessingTime=RPT
                activeObjectQ.sort(key=lambda x: (x.dueDate-x.remainingProcessingTime))
            except:
                for entity in [operator.candidateEntity for operator in activeObjectQ]:
                    RPT=0
                    for step in entity.remainingRoute:
                        processingTime=step.get('processingTime',None)
                        if processingTime:
                            RPT+=float(processingTime.get('mean',0))
                    entity.remainingProcessingTime=RPT
                activeObjectQ.sort(key=lambda x: (x.candidateEntity.dueDate-x.candidateEntity.remainingProcessingTime))
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        elif criterion=="WINQ":
            try:
                from Globals import G
                for entity in activeObjectQ:
                    nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                    for obj in G.ObjList:
                        if obj.id in nextObjIds:
                            nextObject=obj
                    entity.nextQueueLength=len(nextObject.getActiveObjectQueue())
                activeObjectQ.sort(key=lambda x: x.nextQueueLength)
            except:
                from Globals import G
                for entity in [operator.candidateEntity for operator in activeObjectQ]:
                    nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                    for obj in G.ObjList:
                        if obj.id in nextObjIds:
                            nextObject=obj
                    entity.nextQueueLength=len(nextObject.getActiveObjectQueue())
                activeObjectQ.sort(key=lambda x: x.candidateEntity.nextQueueLength)
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )