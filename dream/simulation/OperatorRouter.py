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
            
            for object in G.MachineList:
                if object.inPositionToGet:
                    object.canProceedWithGetEntity=True
                    self.inPositionToGet=False
            
            # have to check also the activeCallersList of each machine about to receive something
            
#                 # TESTING
#                 import Globals
#                 giversList=[]
#                 for object in objList:
#                     for receiver in objList:
#                         if object.haveToDispose(receiver):
#                             giversList.append(object)

#                     # set the variable operatorAssignedTo to activeObject, the operator is then blocked
#                     activeObject.operatorPool.operators[0].operatorAssignedTo=activeObject
#                     # TESTING
#                     print now(), activeObject.operatorPool.operators[0].objName, 'got assigned to', activeObject.id
            
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
                        return True
                    else:
                        return False
                elif entity.currentStation in G.OrderDecompositionList:
                    return False
                # TODO: this list can check all the available object in G.objList
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
        
    

                    
        