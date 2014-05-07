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
from SimPy.Globals import sim
from SimPy.Simulation import Simulation
from SimPy.Simulation import Process, Resource, SimEvent
from ObjectInterruption import ObjectInterruption
from SimPy.Simulation import waituntil, now, hold, request, release, waitevent


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
        # signal used to initiate the generator of the Router
        self.isCalled=SimEvent('RouterIsCalled')
        self.isInitialized=False
        self.candidateOperators=[]
        self.multipleCriterionList=[]
        self.schedulingRule='WT'
        # boolean flag to check whether the Router should perform sorting on operators and on pendingEntities
        self.sorting=sorting
        self.conflictingOperators=[]
        # list of objects to be signalled by the Router
        self.toBeSignalled=[]
        # flag to notify whether the router is already invoked
        self.invoked=False
        # flag to notify whether the router is dealing with managed or simple entities
        self.managed=False
        
    #===========================================================================
    #                         the initialize method
    #===========================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        # list that holds all the objects that can receive
        self.pendingObjects=[]
        self.calledOperator=[]
        # list of the operators that may handle a machine at the current simulation time
        self.candidateOperators=[]
        # list of criteria
        self.multipleCriterionList=[]
        # TODO: find out which must be the default for the scheduling Rule
        self.schedulingRule='WT'
        # flag used to check if the Router is initialised
        self.isInitialized=True
        self.conflictingOperators=[]
        self.toBeSignalled=[]
        self.invoked=False
        self.managed=False
        
    # =======================================================================
    #                          the run method
    # =======================================================================
    '''
    all the pendingEntities that are hot should be examined if they can proceed to the next
    step of their route as they may not be first in the activeQueue of their currentStations (QueueManagedJob).
    If they can be disposed to the next object then the router should wait again till the machine to receive them
    returns canAcceptAndIsRequested (inPositionToGet is True)
    '''
    def run(self):
        from Globals import G
        # find out whether we are dealing with managed entities
        if G.EntityList:
            for entity in G.EntityList:
                if entity.manager:
                    self.managed=True
                    break
        while 1:
            # wait until the router is called
            yield waitevent, self, self.isCalled
#             print '=-'*15
#             print 'router received event'
            # wait till there are no more events, the machines must be blocked
            while 1:
#                 print Simulation.allEventNotices(sim)
                if now() in Simulation.allEventTimes(sim):
#                     print 'there are MORE events for now'
                    yield hold, self, 0
                else:
#                     print 'there are NO more events for now'
                    break
#             print '=-'*15
            # after the events are over, assign the operators to machines for loading or simple processing
            # read the pendingEntities currentStations, these are the stations (queues) that may be signalled
            # the activeCallers list is updated each time the canAcceptAndIsRequested returns true even if the machine is not signalled
            
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
            self.findCandidateEntities()
            # find the entity that will occupy the resource, and the station that will receive it (if any available)
            #  entities that are already in stations have already a receiver
            self.findCandidateReceivers()
            # assign operators to stations
            self.assignOperators()

            
            # if an exit of an object is assigned to one station, while the operator to operate 
            #     the moving entity is assigned to a different, unAssign the exit
            #------------------------------------------------------------------------------
            if not self.managed:
                for operator in [x for x in self.candidateOperators if x.isAssignedTo()]:
                    if not operator.isAssignedTo() in self.pendingObjects:
                        for object in [x for x in operator.isAssignedTo().previous if x.exitIsAssignedTo()]:
                            if object.exitIsAssignedTo()!=operator.isAssignedTo():
                                object.unAssignExit()
            #------------------------------------------------------------------------------
            else: 
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
            #===================================================================
#             # testing
#             print 'router exiting'
#             print '=-'*20
            #===================================================================
            self.exit()
     
    #===========================================================================
    # assigning operators to machines
    #===========================================================================
    def assignOperators(self):
        #------------------------------------------------------------------------------ 
        # for all the operators that are requested
        for operator in self.candidateOperators:
            # check if the candidateOperators are available, if the are requested and reside in the pendingObjects list
            if operator.checkIfResourceIsAvailable():
                # if the router deals with managed entities
                #------------------------------------------------------------------------------ 
                if not self.managed:
                    # if the operator is not conflicting
                    if not operator in self.conflictingOperators:
                        # assign an operator to the priorityObject
                        #=======================================================
#                         # testing
#                         print 'router will assign', operator.id, 'to', operator.candidateStation.id
                        #=======================================================
                        operator.assignTo(operator.candidateStation)
                        self.toBeSignalled.append(operator.candidateStation)
                #------------------------------------------------------------------------------
                else:
                    # and if the priorityObject is indeed pending
                    if (operator.candidateEntity.currentStation in self.pendingObjects) and (not operator in self.conflictingOperators):
                        # assign an operator to the priorityObject
                        #=======================================================
#                         # testing
#                         print 'router will assign', operator.id, 'to', operator.candidateEntity.candidateReceiver.id
                        #=======================================================
                        operator.assignTo(operator.candidateEntity.candidateReceiver)
                        self.toBeSignalled.append(operator.candidateEntity.currentStation)
        #===================================================================
#         # testing
#         print 'router found objects to be signalled'
#         print [str(object.id) for object in self.toBeSignalled] 
#         print [str(object.exitIsAssignedTo().id) for object in self.toBeSignalled if object.exitIsAssignedTo()]
        #===================================================================
    
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
            entity.canProceed=False
            entity.candidateReceivers=[]
            entity.candidateReceiver=None    
        del self.candidateOperators[:]
        del self.pendingObjects[:]
        del self.pendingMachines[:]
        del self.pendingQueues[:]
        del self.toBeSignalled[:]
        del self.multipleCriterionList[:]
        del self.conflictingOperators[:]
        self.schedulingRule='WT'
        self.invoked=False
    
    
    #===========================================================================
    # signal stations that wait for load operators
    #===========================================================================
    def signalOperatedStations(self):
#         print 'router trying to signal pendingObjects'
        from Globals import G
        for operator in self.candidateOperators:
            station=operator.isAssignedTo()
            if station:
                # if the router deals with simple entities
                #------------------------------------------------------------------------------ 
                if not self.managed:
                    assert station in self.toBeSignalled, 'the station must be in toBeSignalled list'
                    if station.broker.waitForOperator:
                        # signal this station's broker that the resource is available
                        #===========================================================
#                         # testing
#                         print now(), 'router signalling broker of', operator.isAssignedTo().id
                        #===========================================================
                        station.broker.resourceAvailable.signal(now())
                    else:
                        # signal the queue proceeding the station
                        if station.canAccept()\
                             and any(type=='Load' for type in station.multOperationTypeList):
                            #=======================================================
#                             # testing
#                             print now(), 'router signalling', operator.isAssignedTo().id
                            #=======================================================
                            station.loadOperatorAvailable.signal(now())
                # in case the router deals with managed entities
                #------------------------------------------------------------------------------ 
                else:
                    if station in self.pendingMachines and station in self.toBeSignalled:
                        # signal this station's broker that the resource is available
                        #===========================================================
#                         # testing
#                         print now(), 'router signalling broker of', operator.isAssignedTo().id
                        #===========================================================
                        operator.isAssignedTo().broker.resourceAvailable.signal(now())
                    elif (not station in self.pendingMachines) or (not station in self.toBeSignalled):
                        # signal the queue proceeding the station
                        assert operator.candidateEntity.currentStation in self.toBeSignalled, 'the candidateEntity currentStation is not picked by the Router'
                        assert operator.candidateEntity.currentStation in G.QueueList, 'the candidateEntity currentStation to receive signal from Router is not a queue'
                        if operator.candidateEntity.candidateReceiver.canAccept()\
                             and any(type=='Load' for type in operator.candidateEntity.candidateReceiver.multOperationTypeList):
                            #=======================================================
#                             # testing
#                             print now(), 'router signalling queue', operator.candidateEntity.currentStation.id
                            #=======================================================
                            operator.candidateEntity.currentStation.loadOperatorAvailable.signal(now())
    
    #===========================================================================
    # clear the pending lists of the router
    #===========================================================================
    def clearPending(self):
        self.pendingQueues=[]
        self.pendingMachines=[]
        self.pendingObjects=[]
    
    
    #===========================================================================
    # find the stations that can be signalled by the router
    #===========================================================================
    def findPendingObjects(self):
        from Globals import G
        self.clearPending()
        for entity in G.pendingEntities:
            for machine in entity.currentStation.next:
                if any(type=='Load' for type in machine.multOperationTypeList):
                    self.pendingQueues.append(entity.currentStation)
                    self.pendingObjects.append(entity.currentStation)
                    break
        self.pendingMachines=[machine for machine in G.MachineList if machine.broker.waitForOperator]
        self.pendingObjects=self.pendingQueues+self.pendingMachines
        #=======================================================================
#         # testing
#         print 'router found pending objects'
#         print [object.id for object in self.pendingObjects]
        #=======================================================================
    
    #===========================================================================
    # finding the entities that require manager now
    #===========================================================================
    def findPendingEntities(self):
        from Globals import G
        self.pending=[]             # list of entities that are pending
        for machine in self.pendingMachines:
            self.pending.append(machine.currentEntity)
        for entity in G.pendingEntities:
            for machine in entity.currentStation.next:
                if any(type=='Load' for type in machine.multOperationTypeList):
                    self.pending.append(entity)
                    break
        # find out which type of entities are we dealing with, managed entities or not
        if self.pending:
            if self.pending[0].manager:
                self.managed=True
        #=======================================================================
#         # testing
#         print 'found pending entities'
#         print [entity.id for entity in self.pending if not entity.type=='Part']
        #=======================================================================
        
    #========================================================================
    # Find candidate Operators
    # find the operators that can start working now even if they are not called
    #     to be found:
    #     .    the candidate operators
    #     .    their candidate entities (the entities they will process)
    #     .    the candidate receivers of the entities (the stations the operators will be working at)
    #========================================================================
    def findCandidateOperators(self):
        #TODO: here check the case of no managed entities (normal machines)
        from Globals import G
        # if we are not dealing with managed entities
        #------------------------------------------------------------------------------ 
        if not self.managed:
            # if there are pendingEntities
            if self.pendingObjects:
                for object in self.pendingObjects:
                    if object in self.pendingMachines:
                        if object.operatorPool.checkIfResourceIsAvailable():
                            candidateOperator=object.operatorPool.findAvailableOperator()
                            # TODO: this way no sorting is performed
                            if not candidateOperator in self.candidateOperators:
                                self.candidateOperators.append(candidateOperator)
                            candidateOperator.candidateStations.append(object)
                    elif object in self.pendingQueues:
                        for nextobject in object.next:
                            if nextobject.canAccept(object):
                                candidateOperator=nextobject.operatorPool.findAvailableOperator()
                                if not candidateOperator in self.candidateOperators:
                                    self.candidateOperators.append(candidateOperator)
                                candidateOperator.candidateStations.append(object)
                # update the schedulingRule/multipleCriterionList of the Router
                if self.sorting:
                    self.updateSchedulingRule()
        # in case the router deals with managed entities
        #------------------------------------------------------------------------------ 
        else:
            # if there are pendingEntities
            if len(self.pending):
            # for those pending entities that require a manager (MachineManagedJob case)
                for entity in [x for x in self.pending if x.manager]:
            # if the entity is ready to move to a machine and its manager is available
                    if entity.manager.checkIfResourceIsAvailable():
                    # for entities of type OrderComponent, if they reside at a conditionalBuffer, 
                    #     they must wait till their basicsEnded flag is raised
                        if entity.type=='OrderComponent':
                            from ConditionalBuffer import ConditionalBuffer
                            if (entity.componentType=='Secondary'\
                                and type(entity.currentStation) is ConditionalBuffer\
                                and entity.order.basicsEnded==False):
                                continue
                    # unassembled components of a mould must wait at a MouldAssemblyBuffer till the componentsReadyForAssembly flag is raised 
                        from MouldAssemblyBuffer import MouldAssemblyBuffer
                        if type(entity.currentStation) is MouldAssemblyBuffer:
                            if not entity.order.componentsReadyForAssembly:
                                continue
                # for all the possible receivers of an entity check whether they can accept and then set accordingly the canProceed flag of the entity 
                        for nextObject in [object for object in entity.currentStation.next if object.canAcceptEntity(entity)]:
                            entity.canProceed=True
                            entity.candidateReceivers.append(nextObject)
                    # if the entity is in a machines who's broker waits for operator then
                        if entity.currentStation in self.pendingMachines:
                            entity.canProceed=True
                # if the entity can proceed, add its manager to the candidateOperators list
                        if entity.canProceed and not entity.manager in self.candidateOperators:
                            self.candidateOperators.append(entity.manager)
                # update the schedulingRule/multipleCriterionList of the Router
                if self.sorting:
                    self.updateSchedulingRule()
        #=======================================================================
#         # testing
#         print 'router found candidate operators'
#         print [operator.id for operator in self.candidateOperators]
        #=======================================================================
    
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
    def findCandidateEntities(self):
        from Globals import G
        # if the moving entities are not managed
        #------------------------------------------------------------------------------ 
        if not self.managed:
            # TODO: the operator finds no entities in this case
            # initialise operatorsWithOneCandidateStation lists
            operatorsWithOneCandidateStation=[]
            # for all the candidateOperators
            for operator in self.candidateOperators:
            # sort the candidate operators so that those who have only one option be served first
                if len(operator.candidateStations)==1:
                    operatorsWithOneCandidateStation.append(operator)
             
            # TODO: the operator here actually chooses entity. This may pose a problem as two entities may be equivalent
            #       and as the operators chooses the sorting of the queue (if they do reside in the same queue is not taken into account)
            # sort the candidateEntities list of each operator according to its schedulingRule
            # TODO: rename the sorting method, the simple operator is not sorting entities but candidateStations
            for operator in [x for x in self.candidateOperators if x.candidateStations]:
                operator.sortCandidateEntities()
                 
            # if there operators that have only one option then sort the candidateOperators according to the first one of these
            # TODO: find out what happens if there are many operators with one option
            # TODO: incorporate that to 
            # self.sortOperators() 
             
            if self.sorting:
                # sort the operators according to their waiting time
                self.candidateOperators.sort(key=lambda x: x.totalWorkingTime)
                # sort according to the number of options
                if operatorsWithOneCandidateStation:
                    self.candidateOperators.sort(key=lambda x: x in operatorsWithOneCandidateStation, reverse=True)
        # if the entities are managed
        #------------------------------------------------------------------------------
        else:
            # TODO: sort according to the number of pending Jobs
            # TODO Have to sort again according to the priority used by the operators
             
            # initialise the operatorsWithOneOption and operatorsWithOneCandidateEntity lists
            operatorsWithOneOption=[]
            operatorsWithOneCandidateEntity=[]
            # for all the candidateOperators
            for operator in self.candidateOperators:
                # find which pendingEntities that can move to machines is the operator managing
                for entity in [x for x in self.pending if x.canProceed and x.manager==operator]:
                    operator.candidateEntities.append(entity)
            # sort the candidate operators so that those who have only one option be served first
                if len(operator.candidateEntities)==1:
                    operatorsWithOneCandidateEntity.append(operator)
                    # if the candidate entity has only one receiver then append the operator to operatorsWithOneOption list
                    if len(operator.candidateEntities[0].candidateReceivers)==1:
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
        #=======================================================================
#         # testing
#         print 'router found the candidate entities for each operator'
#         print [(str(operator.id),\
#                  [str(x.id) for x in operator.candidateEntities])
#                  for operator in self.candidateOperators]
        #=======================================================================

    #=======================================================================
    #                          Sort pendingEntities
    # TODO: sorting them according to the operators schedulingRule
    #=======================================================================
    def sortPendingEntities(self):
        # TODO: to be used for sorting of operators
        #    there must be also a schedulingRule property for the Router
        #    there must also be a way to have multiple criteria for the operators (eg MC-Priority-WT)
        #    WT may be needed to be applied everywhere 
        # TODO: move that piece of code elsewhere, it doesn't look nice here. and there is not point in doing it here
        #    maybe it's better in findCandidateOperators method
        if self.candidateOperators:
            from Globals import G
            candidateList=self.pending
            self.activeQSorter(criterion=self.schedulingRule,candList=candidateList)
        #=======================================================================
#         # testing
#         print 'router sorted pending entities'
        #=======================================================================
         
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
        if not self.managed:
            # initialise local variables occupiedReceivers and entitiesWithOccupiedReceivers
            conflictingStations=[]                 # list with the operators that have candidateEntity with conflicting candidateReceivers
            conflictingOperators=[]
             
            # finally we have to sort before giving the entities to the operators
            # If there is an entity which must have priority then it should be assigned first
             
            #local method that finds a candidate entity for an operator
            def findCandidateStation():
                candidateStation=next(x for x in operator.candidateStations if not x in conflictingStations)
                if not self.sorting:
                    if not candidateStation:
                        candidateStation=next(x for x in operator.candidateStations)
                        conflictingStations.append(candidateStation)
                return candidateStation
             
                 
            # TODO: sorting again after choosing candidateEntity
            if self.sorting:
                self.sortOperators()
             
            # for the candidateOperators that do have candidateEntities pick a candidateEntity
            for operator in [x for x in self.candidateOperators if x.candidateStations]:
                # find the first available entity that has no occupied receivers
                operator.candidateStation=findCandidateStation()
             
            # find the resources that are 'competing' for the same station
            if not self.sorting:
                # if there are entities that have conflicting receivers
                if len(conflictingStations):
                    for operator in self.candidateOperators:
                        if operator.candidateStation in conflictingStations:
                            conflictingOperators.append(operator)
                self.conflictingOperators=conflictingOperators 
            # keep the sorting provided by the queues if there is conflict between operators
            conflictingGroup=[]                     # list that holds the operators that have the same recipient
            if not self.sorting and self.conflictingOperators:
                # for each of the candidateReceivers
                for station in conflictingStations:
                    # find the group of operators that compete for this station
                    conflictingGroup=[operator for operator in self.conflictingOperators if operator.candidateStation==station]
                    # the operator that can proceed is the manager of the entity as sorted by the queue that holds them
                    conflictingGroup.sort()
                # the operators that are not first in the list cannot proceed
                for operator in conflitingGroup:
                    if conflictingGroup.index(operator)!=0:
                        self.candidateOperators.remove(operator)
                        self.calledOperators.remove(operator)
        
        # if the moving entities are managed
        #------------------------------------------------------------------------------
        else:
            # initialise local variables occupiedReceivers and entitiesWithOccupiedReceivers
            conflictingOperators=[]                 # list with the operators that have candidateEntity with conflicting candidateReceivers
            conflictingEntities=[]                  # entities with conflictingReceivers
            occupiedReceivers=[]                    # occupied candidateReceivers of a candidateEntity
            entitiesWithOccupiedReceivers=[]        # list of entities that have no available receivers
             
            # finally we have to sort before giving the entities to the operators
            # If there is an entity which must have priority then it should be assigned first
             
            #local method that finds a candidate entity for an operator
            def findCandidateEntity():
                candidateEntity=next(x for x in operator.candidateEntities if not x in entitiesWithOccupiedReceivers)
                if not self.sorting:
                    if not candidateEntity:
                        candidateEntity=next(x for x in operator.candidateEntities)
                        conflictingEntities.append(candidateEntity)
                return candidateEntity
             
            #local method that finds a receiver for a candidate entity
            def findCandidateReceiver():
                # find the receiver that waits the most
                def chooseReceiverFrom(list):
                    maxTimeWaiting=0
                    for object in list:
                        timeWaiting=now()-object.timeLastEntityLeft
                        if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                            maxTimeWaiting=timeWaiting
                            receiver=object
                    return receiver
                # initiate the local list variable available receivers
                availableReceivers=[x for x in operator.candidateEntity.candidateReceivers\
                                                if not x in occupiedReceivers]
                # and pick the object that is waiting for the most time
                if availableReceivers:
                    # TODO: must find the receiver that waits the most
                    availableReceiver=chooseReceiverFrom(availableReceivers)
                    occupiedReceivers.append(availableReceiver)
                # if there is no available receiver add the entity to the entitiesWithOccupiedReceivers list
                else:
                    entitiesWithOccupiedReceivers.append(operator.candidateEntity)
                    availableReceiver=None
                # if the sorting flag is not set then the sorting of each queue must prevail in case of operators conflict
                if not self.sorting and not availableReceiver and availableReceivers:
                    availableReceiver=chooseReceiverFrom(operator.candidateEntity.candidateReceivers)
                return availableReceiver
             
                 
            # TODO: sorting again after choosing candidateEntity
            if self.sorting:
                self.sortOperators()
             
            # for the candidateOperators that do have candidateEntities pick a candidateEntity
            for operator in [x for x in self.candidateOperators if x.candidateEntities]:
                # find the first available entity that has no occupied receivers
                operator.candidateEntity=findCandidateEntity()
                if operator.candidateEntity:
                    if operator.candidateEntity.currentStation in self.pendingMachines:
                        operator.candidateEntity.candidateReceiver=operator.candidateEntity.currentStation
                    else:
                        operator.candidateEntity.candidateReceiver=findCandidateReceiver()
             
            # find the resources that are 'competing' for the same station
            if not self.sorting:
                # if there are entities that have conflicting receivers
                if len(conflictingEntities):
                    for operator in self.candidateOperators:
                        if operator.candidateEntity in conflictingEntities:
                            conflictingOperators.append(operator)
                        elif operator.candidateEntity.candidateReceiver in [x.candidateReceiver for x in conflinctingEntities]:
                            conflictingOperators.append(operator)
                self.conflictingOperators=conflictingOperators 
            # keep the sorting provided by the queues if there is conflict between operators
            conflictingGroup=[]                     # list that holds the operators that have the same recipient
            if not self.sorting and self.conflictingOperators:
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
                for operator in conflitingGroup:
                    if conflictingGroup.index(operator)!=0:
                        self.candidateOperators.remove(operator)
                        self.calledOperators.remove(operator)
            
        #=======================================================================
#         # testing
#         print 'router found candidate receivers for each entity'
#         print [(str(entity.id),\
#                  str(entity.candidateReceiver.id))
#                  for entity in self.pending if entity.candidateReceiver]
        #=======================================================================     
         
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