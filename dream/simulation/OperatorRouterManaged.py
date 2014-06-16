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
Created on 01 Jun 2013

@author: Ioannis
'''
'''
Models an Interruption that schedules the operation of the machines by different managers
'''
# from SimPy.Globals import sim
# from SimPy.Simulation import Simulation
# from SimPy.Simulation import Process, Resource, SimEvent
import simpy

from OperatorRouter import Router
# from SimPy.Simulation import waituntil, now, hold, request, release, waitevent


# ===========================================================================
#               Class that handles the Operator Behavior
# ===========================================================================
class RouterManaged(Router):
    
    # =======================================================================
    #   according to this implementation one machine per broker is allowed
    #     The Broker is initiated within the Machine and considered as 
    #                black box for the ManPy end Developer
    # TODO: we should maybe define a global schedulingRule criterion that will be 
    #         chosen in case of multiple criteria for different Operators
    # ======================================================================= 
    def __init__(self,sorting=False):
        Router.__init__(self)
        self.multipleCriterionList=[]
        self.schedulingRule='WT'
        # boolean flag to check whether the Router should perform sorting on operators and on pendingEntities
        self.sorting=sorting
        
    #===========================================================================
    #                         the initialize method
    #===========================================================================
    def initialize(self):
        Router.initialize(self)
        # list that holds all the objects that can receive
        self.pendingObjects=[]
        self.calledOperator=[]
        # list of the operators that may handle a machine at the current simulation time
        self.candidateOperators=[]
        # list of criteria
        self.multipleCriterionList=[]
        # TODO: find out which must be the default for the scheduling Rule
        self.schedulingRule='WT'
        
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
            yield self.isCalled
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
            
            
            # find the pending objects
            self.findPendingObjects()
            # find the pending entities
            self.findPendingEntities()
            # find the operators that can start working now 
            self.findCandidateOperators()
            # sort the pendingEntities list
            if self.sorting:
                self.sortPendingEntities()
            # find the operators candidateEntities
            self.sortCandidateEntities()
            # find the entity that will occupy the resource, and the station that will receive it (if any available)
            #  entities that are already in stations have already a receiver
            self.findCandidateReceivers()
            # assign operators to stations
            self.assignOperators()

            for operator in [x for x in self.candidateOperators if x.isAssignedTo()]:
                if not operator.isAssignedTo() in self.pendingObjects:
                    if operator.candidateEntity.currentStation.exitIsAssignedTo():
                        if operator.isAssignedTo()!=operator.candidateEntity.currentStation.exitIsAssignedTo():
                            operator.candidateEntity.currentStation.unAssignExit()
            # if an object cannot proceed with getEntity, unAssign the exit of its giver
            for object in self.pendingQueues:
                if not object in self.toBeSignalled:
                    object.unAssignExit()
            # signal the stations that ought to be signalled
            self.signalOperatedStations()
            self.printTrace('', 'router exiting')
            self.printTrace('','=-'*20)
            self.exit()
     
    #===========================================================================
    # assigning operators to machines
    #===========================================================================
    def assignOperators(self):
        #------------------------------------------------------------------------------ 
        # for all the operators that are requested
        for operator in self.candidateOperators:
            # check if the candidateOperators are available, if the are requested and reside in the pendingObjects list
            #------------------------------------------------------------------------------
            if operator.checkIfResourceIsAvailable():
                if operator.candidateEntity:
                    # and if the priorityObject is indeed pending
                    if (operator.candidateEntity.currentStation in self.pendingObjects)\
                        and (not operator in self.conflictingOperators)\
                        and operator.candidateEntity.candidateReceiver:
                        # assign an operator to the priorityObject
                        self.printTrace('router', 'will assign '+operator.id+' to -->  '+operator.candidateEntity.candidateReceiver.id)
                        operator.assignTo(operator.candidateEntity.candidateReceiver)
                        if not operator.candidateEntity.currentStation in self.toBeSignalled:
                            self.toBeSignalled.append(operator.candidateEntity.currentStation)
        self.printTrace('objects to be signalled:'+' '*11, [str(object.id) for object in self.toBeSignalled])
    
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
            operator.candidateEntity=None
        for entity in G.pendingEntities:
            entity.proceed=False
            entity.candidateReceivers=[]
            entity.candidateReceiver=None    
        del self.candidateOperators[:]
        del self.criticalPending[:]
        del self.preemptiveOperators[:]
        del self.pendingObjects[:]
        del self.pendingMachines[:]
        del self.pendingQueues[:]
        del self.toBeSignalled[:]
        del self.multipleCriterionList[:]
        del self.conflictingOperators[:]
        del self.conflictingStations[:]
        del self.conflictingEntities[:]
        del self.occupiedReceivers[:]
        del self.entitiesWithOccupiedReceivers[:]
        self.schedulingRule='WT'
        self.invoked=False
    
    
    #===========================================================================
    # signal stations that wait for load operators
    #===========================================================================
    def signalOperatedStations(self):
        from Globals import G
        for operator in self.candidateOperators:
            station=operator.isAssignedTo()
            if station:
                # if the router deals with simple entities
                
                if station in self.pendingMachines and station in self.toBeSignalled:
                    # signal this station's broker that the resource is available
                    self.printTrace('router','signalling broker of'+' '*50+operator.isAssignedTo().id)
                    operator.isAssignedTo().broker.resourceAvailable.succeed(self.env.now)
                elif (not station in self.pendingMachines) or (not station in self.toBeSignalled):
                    # signal the queue proceeding the station
                    assert operator.candidateEntity.currentStation in self.toBeSignalled, 'the candidateEntity currentStation is not picked by the Router'
                    assert operator.candidateEntity.currentStation in G.QueueList, 'the candidateEntity currentStation to receive signal from Router is not a queue'
                    if operator.candidateEntity.candidateReceiver.canAccept()\
                        and any(type=='Load' for type in operator.candidateEntity.candidateReceiver.multOperationTypeList):
                        # if the station is already is already signalled then do not send event
                        if not operator.candidateEntity.currentStation.loadOperatorAvailable.triggered:
                            self.printTrace('router','signalling queue'+' '*50+operator.candidateEntity.currentStation.id)
                            operator.candidateEntity.currentStation.loadOperatorAvailable.succeed(self.env.now)
    
    #===========================================================================
    # clear the pending lists of the router
    #===========================================================================
    def clearPendingObjects(self):
        self.pendingQueues=[]
        self.pendingMachines=[]
        self.pendingObjects=[]
    
    
    #===========================================================================
    # find the stations that can be signalled by the router
    #===========================================================================
    def findPendingObjects(self):
        from Globals import G
        self.clearPendingObjects()
        for entity in G.pendingEntities:
            if entity.currentStation in G.MachineList:
                if entity.currentStation.broker.waitForOperator:
                    self.pendingMachines.append(entity.currentStation)
            for machine in entity.currentStation.next:
                if machine in G.MachineList:
                    if any(type=='Load' for type in machine.multOperationTypeList) and not entity.currentStation in self.pendingQueues:
                        self.pendingQueues.append(entity.currentStation)
                        self.pendingObjects.append(entity.currentStation)
                        break
#         self.pendingMachines=[machine for machine in G.MachineList if machine.broker.waitForOperator]
        self.pendingObjects=self.pendingQueues+self.pendingMachines
        self.printTrace('router found pending objects'+'-'*6+'>', [str(object.id) for object in self.pendingObjects])
        self.printTrace('pendingMachines'+'-'*19+'>', [str(object.id) for object in self.pendingMachines])
        self.printTrace('pendingQueues'+'-'*21+'>', [str(object.id) for object in self.pendingQueues])
    
    #===========================================================================
    # finding the entities that require manager now
    #===========================================================================
    def findPendingEntities(self):
        from Globals import G
        self.pending=[]             # list of entities that are pending
        for machine in self.pendingMachines:
            self.pending.append(machine.currentEntity)
        for entity in G.pendingEntities:
            if entity.currentStation in G.QueueList or entity.currentStation in G.SourceList:
                for machine in entity.currentStation.next:
                    if any(type=='Load' for type in machine.multOperationTypeList):
                        self.pending.append(entity)
                        # if the entity is critical add it to the criticalPending List
                        if entity.isCritical and not entity in self.criticalPending:
                            self.criticalPending.append(entity)
                        break
        self.printTrace('found pending entities'+'-'*12+'>', [str(entity.id) for entity in self.pending if not entity.type=='Part'])
        if self.criticalPending:
            self.printTrace('found pending critical'+'-'*12+'>', [str(entity.id) for entity in self.criticalPending if not entity.type=='Part'])
        
    #========================================================================
    # Find candidate Operators
    # find the operators that can start working now even if they are not called
    #     to be found:
    #     .    the candidate operators
    #     .    their candidate entities (the entities they will process)
    #     .    the candidate receivers of the entities (the stations the operators will be working at)
    #========================================================================
    def findCandidateOperators(self):
        # if there are pendingEntities
        if len(self.pending):
        # for those pending entities that require a manager (MachineManagedJob case)
            for entity in [x for x in self.pending if x.manager]:
        # if the entity is ready to move to a machine and its manager is available
                if entity.manager.checkIfResourceIsAvailable():
                    # check whether the entity canProceed and update the its candidateReceivers
                    if entity.canProceed()\
                        and not entity.manager in self.candidateOperators:
                        self.candidateOperators.append(entity.manager)
        # TODO: check if preemption can be implemented for the managed case
            # find the candidateEntities for each operator
            self.findCandidateEntities()      
         # update the schedulingRule/multipleCriterionList of the Router
        if self.sorting:
            self.updateSchedulingRule()  
        self.printTrace('router found candidate operators'+' '*3,
                        [(operator.id, [station.id for station in operator.candidateStations]) for operator in self.candidateOperators])
    
    #===========================================================================
    # find the candidate entities for each candidateOperator
    #===========================================================================
    def findCandidateEntities(self):
        for operator in self.candidateOperators:
            # find which pendingEntities that can move to machines is the operator managing
            operator.findCandidateEntities(self.pending)
    
    #=======================================================================
    # find the schedulingRules of the candidateOperators
    #=======================================================================
    def updateSchedulingRule(self):
        if self.candidateOperators:
            for operator in self.candidateOperators:
                if operator.multipleCriterionList:
                    for criterion in operator.multipleCriterionList:
                        if not criterion in self.multipleCriterionList:
                            self.multipleCriterionList.append(criterion)
                else: # if operator has only simple scheduling Rule
                    if not operator.schedulingRule in self.multipleCriterionList:
                        self.multipleCriterionList.append(operator.schedulingRule)
            # TODO: For the moment all operators should have only one scheduling rule and the same among them
            # added for testing
            assert len(self.multipleCriterionList)==1,'The operators must have the same (one) scheduling rule' 
            if len(self.multipleCriterionList)==1:
                    self.schedulingRule=self.multipleCriterionList[0]
                
    #=======================================================================
    #         Find the candidateEntities for each candidateOperator
    # find the candidateEntities of each candidateOperator and sort them according
    #     to the scheduling rules of the operator and choose an entity that will be served
    #     and by which machines
    #=======================================================================
    def sortCandidateEntities(self):
        from Globals import G
        # TODO: sort according to the number of pending Jobs
        # TODO Have to sort again according to the priority used by the operators
        
        # initialise the operatorsWithOneOption and operatorsWithOneCandidateEntity lists
        operatorsWithOneOption=[]
        # for all the candidateOperators
        for operator in self.candidateOperators:
        # sort the candidate operators so that those who have only one option be served first
        # if the candidate entity has only one receiver then append the operator to operatorsWithOneOption list
            if operator.hasOneOption():
                operatorsWithOneOption.append(operator)
        
        # TODO: the operator here actually chooses entity. This may pose a problem as two entities may be equivalent
        #       and as the operators chooses the sorting of the queue (if they do reside in the same queue is not taken into account)
        # sort the candidateEntities list of each operator according to its schedulingRule
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            operator.sortCandidateEntities()
            
        # if there operators that have only one option then sort the candidateOperators according to the first one of these
        # TODO: find out what happens if there are many operators with one option
        # TODO: incorporate that to 
        # self.sortOperators() 
        
        if self.sorting:
            # sort the operators according to their waiting time
            self.candidateOperators.sort(key=lambda x: x.totalWorkingTime)
            # sort according to the number of options
            if operatorsWithOneOption:
                self.candidateOperators.sort(key=lambda x: x in operatorsWithOneOption, reverse=True)
        
        self.printTrace('candidateEntities for each operator',\
                        [(str(operator.id),[str(x.id) for x in operator.candidateEntities])
                        for operator in self.candidateOperators])

    #=======================================================================
    #                          Sort pendingEntities
    # TODO: sorting them according to the operators schedulingRule
    #=======================================================================
    def sortPendingEntities(self):
        if self.candidateOperators:
            from Globals import G
            candidateList=self.pending
            self.activeQSorter(criterion=self.schedulingRule,candList=candidateList)
            self.printTrace('router', ' sorted pending entities')
         
    #=======================================================================
    #                             Sort candidateOperators
    # TODO: consider if there must be an argument set for the schedulingRules of the Router
    # TODO: consider if the scheduling rule for the operators must be global for all of them
    #=======================================================================
    def sortOperators(self):
        # TODO: there must be criteria for sorting the cadidateOperators
        #if we have sorting according to multiple criteria we have to call the sorter many times
        # TODO: find out what happens in case of multiple criteria 
        if self.candidateOperators:
            candidateList=self.candidateOperators
            self.activeQSorter(criterion=self.schedulingRule,candList=candidateList)
         
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
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            # find the first available entity that has no occupied receivers
            operator.candidateEntity=operator.findCandidateEntity()
            if operator.candidateEntity:
                if operator.candidateEntity.currentStation in self.pendingMachines:
                    operator.candidateEntity.candidateReceiver=operator.candidateEntity.currentStation
                else:
                    operator.candidateEntity.candidateReceiver=operator.candidateEntity.findCandidateReceiver()
                        
        # find the resources that are 'competing' for the same station
        if not self.sorting:
            # if there are entities that have conflicting receivers
            if len(self.conflictingEntities):
                # find the conflictingOperators
                self.conflictingOperators=[operator for operator in self.candidateOperators\
                                            if operator.candidateEntity in self.conflictingEntities or\
                                                operator.candidateEntity.candidateReceiver in [x.candidateReceiver for x in self.conflictingEntities]]
                # keep the sorting provided by the queues if there is conflict between operators
                conflictingGroup=[]                     # list that holds the operators that have the same recipient
            if len(self.conflictingOperators):
                # for each of the candidateReceivers
                for receiver in [x.candidateEntity.candidateReceiver for x in self.conflictingOperators]:
                    # find the group of operators that compete for this station
                    conflictingGroup=[operator for operator in self.conflictingOperators if operator.candidateEntity.candidateReceiver==receiver]
                    assert len([station for station in [x.candidateEntity.currentStation for x in conflictingGroup]]),\
                                'the conflicting entities must reside in the same queue'
                    # for each of the competing for the same station operators 
                    for operator in conflictingGroup:
                    #     find the index of entities to be operated by them in the queue that holds them
                        operator.ind=operator.candidateEntity.currentStation.getActiveObjectQueue().index(operator.candidateEntity)
                    # the operator that can proceed is the manager of the entity as sorted by the queue that holds them
                    conflictingGroup.sort(key=lambda x: x.ind)
                    # the operators that are not first in the list cannot proceed
                    for operator in conflictingGroup:
                        if conflictingGroup.index(operator)!=0:
                            self.candidateOperators.remove(operator)
            
        self.printTrace('candidateReceivers for each entity ',[(str(entity.id),\
                                                                            str(entity.candidateReceiver.id))
                                                                            for entity in self.pending if entity.candidateReceiver])