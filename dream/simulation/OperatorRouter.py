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
            for object in G.MachineList:
                if object.inPositionToGet:
                    self.pendingObjects.append(object)
            #===================================================================
#             # TESTING
#             print now(),'      the pending objects are',
#             for object in self.pendingObjects:
#                 print '        ', object.id,
#             print ''
            #===================================================================
            
            # update the called operators list
            for operator in G.OperatorsList:
                if len(operator.activeCallersList):
                    self.calledOperators.append(operator)
            #===================================================================
#             # TESTING
#             print '        the called operators are',
#             for operator in self.calledOperators:
#                 print '        ', operator.id, 'from', [str(x.id) for x in operator.activeCallersList],\
#                     'for entity ', [str(x.giver.getActiveObjectQueue()[0].id) for x in operator.activeCallersList],
#             print ''
            #===================================================================
            
            
            # find the operators that can start working now even if they are not called
            #     to be found:
            #     .    the candidate operators
            #     .    their candidate entities (the entities they will process)
            #     .    the candidate receivers of the entities (the stations the operators will be working at)
            
            # initiate the local candidateOperators list
            candidateOperators=[]
            # if there are pendingEntities
            if len(G.pendingEntities):
            # for those pending entities that require a manager (MachineManagedJob case)
                for entity in [x for x in G.pendingEntities if x.manager]:
                    # initiate local canProceed flag and candidateReceivers list of the entity 
                    entity.canProceed=False
                    entity.candidateReceivers=[]
            # if the entity is ready to move to a machine and its manager is available
                    if entity.hot and entity.manager.checkIfResourceIsAvailable():
                    # for entities of type OrderComponent, if they reside at a conditionalBuffer, they must wait till their basicsEnded flag is raised
                        if entity.type=='OrderComponent':
                            from ConditionalBuffer import ConditionalBuffer
                            if (entity.componentType=='Secondary'\
                                and type(entity.currentStation) is ConditionalBuffer\
                                and entity.order.basicsEnded==False):
                                continue
                        # TODO: have also to check whether the entity.currentStation canDispose the entity (mouldAssemblyBuffer problem)
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
                        if entity.canProceed and not entity.manager in candidateOperators:
                            candidateOperators.append(entity.manager)
            #===================================================================
#             # TESTING
#             if G.pendingEntities:
#                 print '        {} the pending entities that can proceed are:        ',
#                 print [str(entity.id) for entity in G.pendingEntities if entity.canProceed]
#             if candidateOperators:
#                 print '        {} the candidate operators are:                      ',
#                 print [str(candidate.id) for candidate in candidateOperators]
            #===================================================================
            '''             all the pendingEntities that are hot should be examined if they can proceed to the 
            step of their route as they may not be first in the activeQueue of their currentStations (QueueManagedJob).
            If they can be disposed to the next object then the router should wait again till the machine to receive them
            returns canAcceptAndIsRequested (inPositionToGet is True)        '''
            
            # sort the operators according to their waiting time
            if candidateOperators:
                self.sortOperators(candidateOperators)
            
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
            # for all the candidateOperators
            for operator in candidateOperators:
                # initialise the local candidateEntities list, candidateEntity and candidateReceiver of each operator
                operator.candidateEntities=[]
                operator.candidateEntity=None
                operator.candidateReceiver=None
                # find which pendingEntities that can move to machines is the operator managing
                for entity in [x for x in G.pendingEntities if x.canProceed and x.manager==operator]:
                    operator.candidateEntities.append(entity)                                                           # candidateOperator.candidateEntity
            # sort the candidate operators so that those who have only one option be served first
                if len(operator.candidateEntities)==1:
                    operatorsWithOneOption.append(operator)
            # if there operators that have only one option then sort the candidateOperators according to the first one of these
            # TODO: find out what happens if there are many operators with one option
            if operatorsWithOneOption:
                candidateOperators.sort(key=lambda x:x==operatorsWithOneOption[0],reverse=True)
            #===================================================================
#             # TESTING
#             if candidateOperators:
#                 print '        {} the candidate operators after second sorting are:                      ',
#                 print [str(candidate.id) for candidate in candidateOperators]
            #===================================================================
            
            # TODO: if there is a critical entity, its manager should be served first
            
            occupiedReceivers=[]
            entitiesWithOccupiedReceivers=[]
            for operator in [x for x in candidateOperators if x.candidateEntities]:
                operator.sortCandidateEntities(operator.candidateEntities)
                noAvailableReceivers=False
                while not noAvailableReceivers:
                    availableEntity=next(x for x in operator.candidateEntities if not x in entitiesWithOccupiedReceivers)
                    if availableEntity:
                        operator.candidateEntity=availableEntity
                        #=======================================================
#                         # TESTING
#                         print '            the candidate receivers for', operator.candidateEntity.id, 'are',\
#                                  [str(x.id) for x in operator.candidateEntity.candidateReceivers]
                        #=======================================================
                        
                        availableReceivers=[x for x in operator.candidateEntity.candidateReceivers\
                                                if not x in occupiedReceivers]
                        if availableReceivers:
                            # TODO: must find the receiver that waits the most
                            maxTimeWaiting=0
                            for object in availableReceivers:
                                timeWaiting=now()-object.timeLastEntityLeft 
                                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                                    maxTimeWaiting=timeWaiting
                                    availableReceiver=object
#                             availableReceiver=availableReceivers[0]
#                             print '    after',
#                             print availableReceiver.id
                            operator.candidateEntity.candidateReceiver=availableReceiver
                            occupiedReceivers.append(availableReceiver)
                            noAvailableReceivers=True
                        else:
                            entitiesWithOccupiedReceivers.append(availableEntity)
            #===================================================================
#             # TESTING
#             print '            +{}+ candidate operators   :',[str(x.id) for x in candidateOperators if x.candidateEntity] 
#             print '            +{}+ have entities         :',[str(x.candidateEntity.id) for x in candidateOperators if x.candidateEntity]
#             print '            +{}+ with receivers        :',[str(x.candidateEntity.candidateReceiver.id) for x in candidateOperators if x.candidateEntity]
            #===================================================================
            
            pendingObjectsMustBeSorted=False
            for operator in [x for x in candidateOperators if x.candidateEntity]:
                operator.called = (operator in self.calledOperators)
#                 print operator.id, 'is called?', operator.called
                if not operator.called:
                    operator.candidateEntity.currentStation.sortEntitiesForOperator(operator)
                    pendingObjectsMustBeSorted=True
                # TODO: if the first candidate is not called then must run again
                #     if the first is called then this one must proceed with get entity 
                else:
                    break    
            #===================================================================
#             # TESTING
#             print '!?!? can the machines proceed with getEntity? ',not pendingObjectsMustBeSorted, '==============='
            #===================================================================
            
            '''
                # now must sort the candidateEntities
                # and possibly choose one of the candidate receivers of the entities
                # we should also sort the queues were the chosen entities lie in order to bring them in front
            # then we must check if there is conflict among the choices of the operators
            #     if there is conflict we must sort the operators
            # if an chosen operator is not in the calledOperators list then no machine should proceed with get entity
            #     but wait till the chosen receiver returns True 
            # for all the called operators find those available
            #     sort the objects for each one of them
            #     and assign the operator to those with the highest priority
            '''
            
#             # if operators that can proceed are not called then the pending objects cannot proceed
#             if not pendingObjectsMustBeSorted:
            # for all the operators that are requested
            for operator in self.calledOperators:
                priorityObject=None
                #===============================================================
#                 # TESTING
#                 print '        calledOperator',operator.id
#                 print '        its candidateReceiver',operator.candidateEntity.candidateReceiver.id
#                 print '        its activeCallers',[str(x.id) for x in operator.activeCallersList]
#                 print '            pendingObjectsMustBeSorted', pendingObjectsMustBeSorted
                #===============================================================
                
                # check if they are available 
                try:
                    candidateEntityHasActiveReceiver=(operator.candidateEntity.candidateReceiver in operator.activeCallersList)
                except:
                    candidateEntityHasActiveReceiver=True
                
                if operator.checkIfResourceIsAvailable() and \
                        candidateEntityHasActiveReceiver:
                    #===========================================================
                    # TESTING
                    #print now(), 'the active callers of', operator.objName, 'before sorting are'
                    #for caller in operator.activeCallersList:
                    #    print '                        ', caller.id
                    #===========================================================
                    
                    # sort the activeCallersList of the operator
                    operator.sortEntities()
                    #===========================================================
#                     # TESTING
#                     print now(), 'the active callers of', operator.objName, 'after sorting are'
#                     for caller in operator.activeCallersList:
#                         print '                        ', caller.id
                    #===========================================================
                    
                    # find the activeCaller that has priority 
                    priorityObject=next(x for x in operator.activeCallersList if x in self.pendingObjects)
                    #===========================================================
                    # TESTING
                    #print '                the PRIORITY object is', priorityObject.id
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
                elif not candidateEntityHasActiveReceiver:
                    operator.activeCallersList=[]
#                     print '        activerCallersList of', operator.id, 'cleared'
            # if an object cannot proceed with getEntity, unAssign the exit of its giver
            for object in self.pendingObjects:
                if not object.canProceedWithGetEntity:
                    object.giver.unAssignExit()
            #===================================================================
#             # TESTING
#             print '        these objects will proceed with getting entities', 
#             for object in self.pendingObjects:
#                 if object.canProceedWithGetEntity:
#                     print '        ', object.id,
#             print ''
            #===================================================================
            
            del self.calledOperators[:]
            del self.pendingObjects[:]
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
    #       sort the candidateOperators according to their waiting time
    # =======================================================================
    def sortOperators(self, candidateOperators=[]):
        if not candidateOperators:
            assert False, "empty candidateOperators list"
        candidateOperators.sort(key=lambda x: x.totalWorkingTime)
    
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
        self.call=False
        
    

                    
        