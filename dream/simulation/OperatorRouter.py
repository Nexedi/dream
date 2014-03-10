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

from SimPy.Simulation import Process, Resource
from ObjectInterruption import ObjectInterruption
from SimPy.Simulation import waituntil, now, hold, request, release


# ===========================================================================
#               Class that handles the Operator Behavior
# ===========================================================================
class Router(ObjectInterruption):
    
    # =======================================================================
    #   according to this implementation one machine per broker is allowed
    #     The Broker is initiated within the Machine and considered as 
    #                black box for the ManPy end Developer
    # ======================================================================= 
    def __init__(self):
        ObjectInterruption.__init__(self)
        self.type = "Router"
        # variable used to hand in control to the Broker
        self.call=False
        # list that holds all the objects that can receive
        self.pendingObjects=[]
        self.calledOperators=[]
        # TODO: consider if there must be an argument set for the schedulingRules of the Router
        self.schedulingRule=''
        # list of the operators that may handle a machine at the current simulation time
        self.candidateOperators=[]
        
    # =======================================================================
    #                          the run method
    # =======================================================================    
    def run(self):
        from Globals import G
        while 1:
            # wait until the router is called
            yield waituntil,self,self.routerIsCalled
            # when the router is called for the first time wait till all the entities 
            #     finished all their moves in stations of non-Machine-type 
            #     before they can enter again a type-Machine object
            yield waituntil, self,self.entitiesFinishedMoving
            
            # update the objects to be served list (pendingObjects)
            self.pendingObjects=[object for object in G.MachineList if object.inPositionToGet]

            #===================================================================
#             # TESTING
#             print now(),'      the pending objects are        ', [str(object.id) for object in self.pendingObjects]
            #===================================================================
            
            # update the called operators list
            self.calledOperators=[operator for operator in G.OperatorsList if len(operator.activeCallersList)]

            #===================================================================
#             # TESTING
#             print '        the called operators are        ', [str(operator.id) for operator in self.calledOperators]
#             print '        from callers                    ', [[str(x.id) for x in operator.activeCallersList] for operator in self.calledOperators]
#             print '        for entity                      ', [[str(x.giver.getActiveObjectQueue()[0].id)for x in operator.activeCallersList] for operator in self.calledOperators]
            #===================================================================
            
            
            # find the operators that can start working now even if they are not called
            self.findCandidateOperators()
            
            #===================================================================
#             # TESTING
#             if G.pendingEntities:
#                 print '                {} the pending entities that can proceed are:                            ',
#                 print [str(entity.id) for entity in G.pendingEntities if entity.canProceed]
#             if self.candidateOperators:
#                 print '                {} the candidate operators are:                                          ',
#                 print [str(candidate.id) for candidate in self.candidateOperators]
            #===================================================================
            
            '''             all the pendingEntities that are hot should be examined if they can proceed to the next
            step of their route as they may not be first in the activeQueue of their currentStations (QueueManagedJob).
            If they can be disposed to the next object then the router should wait again till the machine to receive them
            returns canAcceptAndIsRequested (inPositionToGet is True)        '''
            
            # sort the candidateOperators list
            self.sortOperators()
            
            # find the entity that will occupy the resource, and the station that will receive it (if any available)
            self.findCandidateReceivers()

            
            # sort the givers for the operators that will process the entities
            self.sortGivers()
            

            '''        # now must sort the candidateEntities
            # and possibly choose one of the candidate receivers of the entities
            # we should also sort the queues were the chosen entities lie in order to bring them in front
            
            # then we must check if there is conflict among the choices of the operators
            #     if there is conflict we must sort the operators
            # if an chosen operator is not in the calledOperators list then no machine should proceed with get entity
            #     but wait till the chosen receiver returns True 
            # for all the called operators find those available
            #     sort the objects for each one of them
            #     and assign the operator to those with the highest priority    '''
            
            
            # for all the operators that are requested
            for operator in self.calledOperators:
                priorityObject=None
                #===============================================================
#                 # TESTING
#                 print '        calledOperator prioritising',operator.id
#                 if operator.candidateEntity:
#                     if operator.candidateEntity.candidateReceiver:
#                         print '        its candidateReceiver',operator.candidateEntity.candidateReceiver.id
#                 print '        its activeCallers',[str(x.id) for x in operator.activeCallersList]
                #===============================================================
                
                # check if the candidateReceivers are inPositionToGet and  if they are already called
                try:
                    candidateEntityHasActiveReceiver=(operator.candidateEntity.candidateReceiver in operator.activeCallersList\
                                                  and operator.candidateEntity.candidateReceiver in self.pendingObjects )
                except:
                    candidateEntityHasActiveReceiver=True
                # check if the candidateOperators are available, if the are requested and reside in the pendingObjects list 
                if operator.checkIfResourceIsAvailable() and \
                        candidateEntityHasActiveReceiver:
                    #===========================================================
#                     # TESTING
#                     print now(), 'the active callers of', operator.objName, 'before sorting are            ',
#                     print [str(caller.id) for caller in operator.activeCallersList]
                    #===========================================================
                    
                    # sort the activeCallersList of the operator
                    operator.sortEntities()
                    #===========================================================
#                     # TESTING
#                     print now(), 'the active callers of', operator.objName, 'after sorting are            ',
#                     print [str(caller.id) for caller in operator.activeCallersList]
                    #===========================================================
                    
                    # find the activeCaller that has priority 
                    priorityObject=next(x for x in operator.activeCallersList if x in self.pendingObjects)
                    #===========================================================
#                     # TESTING
#                     print '                the PRIORITY object is', priorityObject.id
                    #===========================================================
                    
                    # and if the priorityObject is indeed pending
                    if priorityObject in self.pendingObjects:
                        
                        # assign an operator to the priorityObject
                        operator.operatorAssignedTo=priorityObject
                        #=======================================================
#                         # TESTING
#                         print now(), operator.objName, 'got assigned to', priorityObject.id
                        #=======================================================
                        
                        # and let it proceed withGetEntity
                        priorityObject.canProceedWithGetEntity=True
                        priorityObject.inPositionToGet=False
                # if the are not called and they are not in the pendingObjects list clear their activeCallersList
                elif not candidateEntityHasActiveReceiver:
                    operator.activeCallersList=[]
            # if an object cannot proceed with getEntity, unAssign the exit of its giver
            for object in self.pendingObjects:
                if not object.canProceedWithGetEntity:
                    object.giver.unAssignExit()
            #===================================================================
#             # TESTING
#             print '        these objects will proceed with getting entities',
#             print [str(object.id) for object in self.pendingObjects if object.canProceedWithGetEntity]
            #===================================================================
            
            self.exitRouter()
    
    #===========================================================================
    #     have the entities that have ended their processing when the router
    #     got first called finished their moves through queues?
    #===========================================================================
    def entitiesFinishedMoving(self):
        # check if the entities waiting to be disposed from different Machines
        #     the first time the Router is called, have reached the last queue (if any)
        #     before the next Machine in their route
        from Globals import G
        # pending entities are entities about to enter an other machine, updated by endProcessingActions()
        # if there are any pending entities
        if len(G.pendingEntities):
            # local variable
            allEntitiesMoved=False
            # for each one of them
            for entity in G.pendingEntities:
                # if they are residing in a machine which waits to dispose and is functional
                if entity.currentStation in G.MachineList:
                    if entity.currentStation.checkIfMachineIsUp()\
                         and entity.currentStation.waitToDispose:
                        # if the next step in the entity's route is machine with Load operationType then continue 
                        if (not (entity.currentStation.receiver in G.MachineList)\
                             and entity.currentStation.receiver.canAccept()\
                             or\
                           ((entity.currentStation.receiver.type in G.MachineList)\
                             and not any(type=='Load' for type in entity.currentStation.receiver.multOperationTypeList))):
                            return False
                # if the entity is in a Queue
                elif entity.currentStation in G.QueueList:
                    # if the hot flag of the entity is raised
                    if entity.hot:
                        allEntitiesMoved=True
#                         return True
                    else:
                        return False
                elif entity.currentStation in G.OrderDecompositionList:
                    return False
                # TODO: this list can check all the available object in G.objList
            # if no entity returned False then return True
            if allEntitiesMoved:
                return True
        return True
    
    # =======================================================================
    #                        call the Scheduler 
    #        filter for Broker - yield waituntil brokerIsCalled
    # =======================================================================
    def routerIsCalled(self):
        return self.call 
    
    # =======================================================================
    #         the broker returns control to OperatedMachine.Run
    #        filter for Machine - yield request/release operator
    # =======================================================================
    def routerIsSet(self):
        return not self.call
    
    # =======================================================================
    #               hand in the control to the Broker.run
    #                   to be called by the machine
    # =======================================================================
    def invokeRouter(self):
        self.call=True
        
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exitRouter(self):
        from Globals import G
        # reset the variables that are used from the Router
        for operator in self.candidateOperators:
            operator.candidateEntities=[]
            operator.candidateEntity=None
        for entity in G.pendingEntities:
            entity.canProceed=False
            entity.candidateReceivers=[]
            entity.candidateReceiver=None    
        del self.candidateOperators[:]
        del self.calledOperators[:]
        del self.pendingObjects[:]
        self.call=False
        
    #========================================================================
    # Find candidate Operators
    #========================================================================
    def findCandidateOperators(self):
        # find the operators that can start working now even if they are not called
        #     to be found:
        #     .    the candidate operators
        #     .    their candidate entities (the entities they will process)
        #     .    the candidate receivers of the entities (the stations the operators will be working at)
        from Globals import G
        # if there are pendingEntities
        if len(G.pendingEntities):
        # for those pending entities that require a manager (MachineManagedJob case)
            for entity in [x for x in G.pendingEntities if x.manager]:
        # if the entity is ready to move to a machine and its manager is available
                if entity.hot and entity.manager.checkIfResourceIsAvailable():
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
            # if the entity can proceed, add its manager to the candidateOperators list
                    if entity.canProceed and not entity.manager in self.candidateOperators:
                        self.candidateOperators.append(entity.manager)
    
    #=======================================================================
    # Sort Candidate Operators
    # TODO: consider if there must be an argument set for the schedulingRules of the Router
    #=======================================================================
    def sortOperators(self):
        from Globals import G
        # TODO: sort accordting to the number of pending Jobs
        # sort the operators according to their waiting time
        self.candidateOperators.sort(key=lambda x: x.totalWorkingTime)                          # sort with total Working Time
        #===================================================================
#             # TESTING
#             if candidateOperators:
#                 print '        {} the candidate operators after sorting are:                      ',
#                 print [str(candidate.id) for candidate in candidateOperators]
        #===================================================================
            
        # find the candidateEntities of each candidateOperator and sort them according
        #     to the scheduling rules of the operator and choose an entity that will be served
        #     and by which machines
        
        # initialise the operatorsWithOneOption  
        operatorsWithOneOption=[]
        operatorsWithOneCandidateEntity=[]
        # for all the candidateOperators
        for operator in self.candidateOperators:
            # find which pendingEntities that can move to machines is the operator managing
            for entity in [x for x in G.pendingEntities if x.canProceed and x.manager==operator]:
                operator.candidateEntities.append(entity)
        # sort the candidate operators so that those who have only one option be served first
            if len(operator.candidateEntities)==1:
                operatorsWithOneCandidateEntity.append(operator)
                # if the candidate entity has only one receiver then append the operator to operatorsWithOneOption list
                if len(operator.candidateEntities[0].candidateReceivers)==1:
                    operatorsWithOneOption.append(operator)
        # if there operators that have only one option then sort the candidateOperators according to the first one of these
        # TODO: find out what happens if there are many operators with one option
        if operatorsWithOneOption:
#                 candidateOperators.sort(key=lambda x:x==operatorsWithOneOption[0],reverse=True)
            self.candidateOperators.sort(key=lambda x: x in operatorsWithOneOption, reverse=True)   # sort according to the number of options
            
        #===================================================================
#         # TESTING
#         if self.candidateOperators:
#             print '                {} the candidate operators after second sorting are:                      ',
#             print [str(candidate.id) for candidate in self.candidateOperators]
#             print '        operators with one Option            ', 
#             print [str(operator.id) for operator in operatorsWithOneOption]
#             for operator in self.candidateOperators:
#                 print '            operator', operator.id, 'has candidate entities        ',
#                 print [candidateEntity.id for candidateEntity in operator.candidateEntities]
        #===================================================================
            
    #=======================================================================
    # Find candidate entities and their receivers
    #=======================================================================
    def findCandidateReceivers(self):
        # TODO: if there is a critical entity, its manager should be served first
        
        # initialise local variables occupiedReceivers and entitiesWithOccupiedReceivers
        occupiedReceivers=[]                    # occupied candidateReceivers of a candidateEntity
        entitiesWithOccupiedReceivers=[]        # list of entities that have no available receivers
        # for the candidateOperators that do have candidateEntities pick a candidateEntity
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            operator.sortCandidateEntities(operator.candidateEntities)
            operator.noAvailableReceivers=False
            # find the first available entity that has no occupied receivers
            availableEntity=next(x for x in operator.candidateEntities if not x in entitiesWithOccupiedReceivers)
            if availableEntity:
                operator.candidateEntity=availableEntity
                #=======================================================
#                 # TESTING
#                 print '            the candidate receivers for', operator.candidateEntity.id, 'are',\
#                                  [str(x.id) for x in operator.candidateEntity.candidateReceivers]
                #=======================================================
                # initiate the local list variable available receivers
                availableReceivers=[x for x in operator.candidateEntity.candidateReceivers\
                                            if not x in occupiedReceivers]
                # and pick the object that is waiting for the most time
                if availableReceivers:
                    # TODO: must find the receiver that waits the most
                    maxTimeWaiting=0
                    for object in availableReceivers:
                        timeWaiting=now()-object.timeLastEntityLeft 
                        if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                            maxTimeWaiting=timeWaiting
                            availableReceiver=object
                        
                    operator.candidateEntity.candidateReceiver=availableReceiver
                    occupiedReceivers.append(availableReceiver)
                    operator.noAvailableReceivers=True
                # if there is no available receiver add the entity to the entitiesWithOccupiedReceivers list
                else:
                    entitiesWithOccupiedReceivers.append(availableEntity)
                    operator.candidateEntity.candidateReceiver=None
        #===================================================================
#         # TESTING
#         print '                    +{}+ candidate operators   :',
#         print [str(x.id) for x in self.candidateOperators if x.candidateEntity] 
#         print '                    +{}+ have entities         :',
#         print [str(x.candidateEntity.id) for x in self.candidateOperators if x.candidateEntity]
#         print '                    +{}+ with receivers        :',
#         print [str(x.candidateEntity.candidateReceiver.id) for x in self.candidateOperators if x.candidateEntity and not x.candidateEntity in entitiesWithOccupiedReceivers]
        #===================================================================
                    
    #=======================================================================
    # Sort Givers
    # TODO: the method currently checks only the first operator of the candidateOperators list
    #    consider populating the controls
    #=======================================================================
    def sortGivers(self):
        # local variable used for testing
        pendingObjectsMustBeSorted=False
        # for those operators that do have candidateEntity
        for operator in [x for x in self.candidateOperators if x.candidateEntity]:
            # check whether are called by objects that require the resource
            operator.called = (operator in self.calledOperators)
            # if they are not called or are not in the pendingObjects list sort the queues of the 
            #     of the requesting the operator entities.  
            if not operator.called:
                operator.candidateEntity.currentStation.sortEntitiesForOperator(operator)
                pendingObjectsMustBeSorted=True
            # TODO: if the first candidate is not called then must run again
            #     if the first is called then this one must proceed with get entity 
            elif not operator.candidateEntity.candidateReceiver in self.pendingObjects:
                operator.candidateEntity.currentStation.sortEntitiesForOperator(operator)
                pendingObjectsMustBeSorted=True
            else:
                break
            
        #===================================================================
#         # TESTING
#         print '======= can the machines proceed with getEntity? ',not pendingObjectsMustBeSorted, '==============='
        #===================================================================