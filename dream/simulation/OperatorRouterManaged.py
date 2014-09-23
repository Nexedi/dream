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
    # ======================================================================= 
    def __init__(self):
        Router.__init__(self)
        # boolean flag to check whether the Router should perform sorting on operators and on pendingEntities
        self.entitiesWithOccupiedReceivers=[]        # list of entities that have no available receivers
        self.conflictingEntities=[]                  # entities with conflictingReceivers
        self.conflictingOperators=[]                 # list with the operators that have candidateEntity with conflicting candidateReceivers
        self.occupiedReceivers=[]                    # occupied candidateReceivers of a candidateEntity
        
    #===========================================================================
    #                         the initialize method
    #===========================================================================
    def initialize(self):
        Router.initialize(self)
        # list that holds all the objects that can receive
        self.pendingObjects=[]
        self.entitiesWithOccupiedReceivers=[]
        self.conflictingEntities=[]                  # entities with conflictingReceivers
        self.conflictingOperators=[]                 # list with the operators that have candidateEntity with conflicting candidateReceivers
        self.occupiedReceivers=[]                    # occupied candidateReceivers of a candidateEntity
        
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
            self.entryActions()
            # run the routine that allocates operators to machines
            self.allocateOperators()
            # assign operators to stations
            self.assignOperators()
            # unAssign exits
            self.unAssignExits()
            # signal the stations that ought to be signalled
            self.signalOperatedStations()
            self.printTrace('', 'router exiting')
            self.printTrace('','=-'*20)
            # exit actions
            self.exitActions()
    
    #===========================================================================
    # entry actions on Router call
    #===========================================================================
    def entryActions(self):
        pass
    
    #===========================================================================
    # routine to allocate the operators to the stations
    #===========================================================================
    def allocateOperators(self):
        # find the pending objects
        self.findPendingObjects()
        # find the pending entities
        self.findPendingEntities()
        # find the operators that can start working now 
        self.findCandidateOperators()
        # find the operators candidateEntities
        self.sortCandidateEntities()
        # find the entity that will occupy the resource, and the station that will receive it (if any available)
        #  entities that are already in stations have already a receiver
        self.findCandidateReceivers()
    
    #===========================================================================
    # un-assign the exit of the objects that are not to be signalled
    #===========================================================================
    def unAssignExits(self):
        for operator in [x for x in self.candidateOperators if x.isAssignedTo()]:
            if not operator.isAssignedTo() in self.pendingObjects:
                if operator.candidateEntity.currentStation.exitIsAssignedTo():
                    if operator.isAssignedTo()!=operator.candidateEntity.currentStation.exitIsAssignedTo():
                        operator.candidateEntity.currentStation.unAssignExit()
        # if an object cannot proceed with getEntity, unAssign the exit of its giver
        for object in self.pendingQueues:
            if not object in self.toBeSignalled:
                object.unAssignExit()
    
    # =======================================================================
    #                 Exit actions return control to the Machine.run
    # =======================================================================
    def exitActions(self):
        # reset the candidateEntities of the operators
        for operator in self.candidateOperators:
            operator.candidateEntity=None
        del self.pendingObjects[:]
        del self.conflictingOperators[:]
        del self.conflictingEntities[:]
        del self.occupiedReceivers[:]
        del self.entitiesWithOccupiedReceivers[:]
        Router.exitActions(self)
    
    #===========================================================================
    # assigning operators to machines
    #===========================================================================
    def assignOperators(self):
        # for all the operators that are requested
        for operator in self.candidateOperators:
            # check if the candidateOperators are available, if the are requested and reside in the pendingObjects list
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
                    if operator.isAssignedTo().broker.expectedSignals['resourceAvailable']:
                        self.sendSignal(receiver=operator.isAssignedTo().broker, signal=operator.isAssignedTo().broker.resourceAvailable)
                elif (not station in self.pendingMachines) or (not station in self.toBeSignalled):
                    # signal the queue proceeding the station
                    assert operator.candidateEntity.currentStation in self.toBeSignalled, 'the candidateEntity currentStation is not picked by the Router'
                    assert operator.candidateEntity.currentStation in G.QueueList, 'the candidateEntity currentStation to receive signal from Router is not a queue'
                    if operator.candidateEntity.candidateReceiver.canAccept()\
                        and any(type=='Load' for type in operator.candidateEntity.candidateReceiver.multOperationTypeList):
                        # if the station is already is already signalled then do not send event
                        if not operator.candidateEntity.currentStation.loadOperatorAvailable.triggered:
                            self.printTrace('router','signalling queue'+' '*50+operator.candidateEntity.currentStation.id)
                            if operator.candidateEntity.currentStation.expectedSignals['loadOperatorAvailable']:
                                self.sendSignal(receiver=operator.candidateEntity.currentStation, signal=operator.candidateEntity.currentStation.loadOperatorAvailable)
    
    #===========================================================================
    # find the stations that can be signalled by the router
    #===========================================================================
    def findPendingObjects(self):
        from Globals import G
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
                        break
        self.printTrace('found pending entities'+'-'*12+'>', [str(entity.id) for entity in self.pending if not entity.type=='Part'])
        
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
                    if entity.currentStation.canDeliver(entity)\
                        and not entity.manager in self.candidateOperators:
                        self.candidateOperators.append(entity.manager)
        # TODO: check if preemption can be implemented for the managed case
            # find the candidateEntities for each operator
            self.findCandidateEntities()
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
    #         Find the candidateEntities for each candidateOperator
    # find the candidateEntities of each candidateOperator and sort them according
    #     to the scheduling rules of the operator and choose an entity that will be served
    #     and by which machines
    #=======================================================================
    def sortCandidateEntities(self):
        from Globals import G
        
        # TODO: the operator here actually chooses entity. This may pose a problem as two entities may be equivalent
        #       and as the operators chooses the sorting of the queue (if they do reside in the same queue is not taken into account)
        # sort the candidateEntities list of each operator according to its schedulingRule
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            operator.sortEntities()
        
        self.printTrace('candidateEntities for each operator',\
                        [(str(operator.id),[str(x.id) for x in operator.candidateEntities])
                        for operator in self.candidateOperators])
         
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
        