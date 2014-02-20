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
        while 1:
            yield waituntil,self,self.routerIsCalled # wait until the router is called
#             # TESTING
#             print 'Router got called'
            from Globals import G
            for object in G.MachineList:
                if object.inPositionToGet:
                    object.canProceedWithGetEntity=True
                    self.inPositionToGet=False
                    
            
            
            
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
        pass
    
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
        
    

                    
        