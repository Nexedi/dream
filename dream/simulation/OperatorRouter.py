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
            #===================================================================
#             # TESTING
#             print now(), self.type, '        entities finished moving'
            #===================================================================
            
            # update the objects to be served list (pendingObjects)
            for object in G.MachineList:
                if object.inPositionToGet:
                    self.pendingObjects.append(object)
            #===================================================================
#             # TESTING
#             print '        the pending objects are'
#             for entity in self.pendingObjects:
#                 print '        ', entity.id
            #===================================================================
            
            # update the called operators list
            for operator in G.OperatorsList:
                if len(operator.activeCallersList):
                    self.calledOperators.append(operator)
            #===================================================================
#             # TESTING
#             print '        the called operators are'
#             for operator in self.calledOperators:
#                 print '        ', operator.id
#             #===================================================================
            
            # for all the called operators find those available
            #     sort the objects for each one of them
            #     and assign the operator to those with the highest priority
            
            # for all the operators that are requested
            for operator in self.calledOperators:
                priorityObject=None
                
                # check if they are available
                if operator.checkIfResourceIsAvailable():
                    #===========================================================
#                     # TESTING
#                     print now(), 'the active callers of', operator.objName, 'before sorting are'
#                     for caller in operator.activeCallersList:
#                         print '                        ', caller.id
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
#                     # TESTING
#                     print '                the PRIORITY object is', priorityObject.id
                    #===========================================================
                    
                    # and if the priorityObject is indeed pending
                    if priorityObject in self.pendingObjects:
                        # assign an operator to it
                        operator.operatorAssignedTo=priorityObject
                        #=======================================================
#                         # TESTING
#                         print now(), operator.objName, 'got assigned to', priorityObject.id
                        #=======================================================
                        
                        # and let it proceed withGetEntity
                        priorityObject.canProceedWithGetEntity=True
                        priorityObject.inPositionToGet=False
            # if an object cannot proceed with getEntity, unAssign the exit of its giver
            for object in self.pendingObjects:
                if not object.canProceedWithGetEntity:
                    object.giver.unAssignExit()
            #===================================================================
#             # TESTING
#             print '        these objects will proceed with getting entities'
#             for object in self.pendingObjects:
#                 if object.canProceedWithGetEntity:
#                     print '        ', object.id
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
        #=======================================================================
#         # TESTING
#         print '            the length of the pendingEntities is', len(G.pendingEntities)
#         for entity in G.pendingEntities:
#             print '                ', entity.id,'in', entity.currentStation.id
        #=======================================================================
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
        self.call=False
        
    

                    
        