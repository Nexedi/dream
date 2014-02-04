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
Created on 27 Nov 2013

@author: Ioannis
'''
'''
Models an Interruption that handles the operating of a Station by an ObjectResource
'''

from SimPy.Simulation import Process, Resource
from ObjectInterruption import ObjectInterruption
from SimPy.Simulation import waituntil, now, hold, request, release

# ===========================================================================
#               Class that handles the Operator Behavior
# ===========================================================================
class Broker(ObjectInterruption):
    
    # =======================================================================
    #   according to this implementation one machine per broker is allowed
    #     The Broker is initiated within the Machine and considered as 
    #                black box for the ManPy end Developer
    # ======================================================================= 
    def __init__(self, operatedMachine):
        ObjectInterruption.__init__(self,operatedMachine)
        self.type = "Broker"
        # variable used to hand in control to the Broker
        self.call=False
        # variables that have to do with timing
        self.timeOperationStarted = 0
        self.timeLastOperationEnded = 0
        self.timeWaitForOperatorStarted=0
        
    # =======================================================================
    #                          the run method
    # =======================================================================    
    def run(self):
        while 1:
            yield waituntil,self,self.brokerIsCalled # wait until the broker is called
    # ======= request a resource
            if self.victim.isOperated()\
                and any(type=="Load" or type=="Setup" or type=="Processing"\
                         for type in self.victim.multOperationTypeList):
                # update the time that the station is waiting for the operator
                self.timeWaitForOperatorStarted=now()
#                 # update the currentObject of the operatorPool
#                 self.victim.operatorPool.currentObject = self.victim
                # wait until a resource is available
                yield waituntil, self, self.victim.operatorPool.checkIfResourceIsAvailable
                # set the available resource as the currentOperator
                self.victim.currentOperator=self.victim.operatorPool.findAvailableOperator()
                yield request,self,self.victim.operatorPool.getResource(self.victim.currentOperator)
#                 self.victim.totalTimeWaitingForOperator+=now()-self.timeWaitForOperatorStarted
                # clear the timeWaitForOperatorStarted variable
                self.timeWaitForOperatorStarted = 0
                # update the time that the operation started
                self.timeOperationStarted = now()
                #self.victim.outputTrace(self.victim.currentOperator.objName, "started work "+self.victim.objName)
                self.victim.currentOperator.timeLastOperationStarted=now()
    # ======= release a resource        
            elif not self.victim.isOperated():
                self.victim.currentOperator.totalWorkingTime+=now()-self.victim.currentOperator.timeLastOperationStarted
                #self.victim.outputTrace(self.victim.currentOperator.objName, "finished work "+self.victim.objName)
                yield release,self,self.victim.operatorPool.getResource(self.victim.currentOperator)
                # the victim current operator must be cleared after the operator is released
                self.timeLastOperationEnded = now()
                self.victim.currentOperator = None
            else:
                pass
            # return the control the machine.run
            self.exitBroker()
        
        
    # =======================================================================
    #                        call the broker 
    #        filter for Broker - yield waituntil brokerIsCalled
    # =======================================================================
    def brokerIsCalled(self):
        return self.call 
    
    # =======================================================================
    #         the broker returns control to OperatedMachine.Run
    #        filter for Machine - yield request/release operator
    # =======================================================================
    def brokerIsSet(self):
        return not self.call
    
    # =======================================================================
    #               hand in the control to the Broker.run
    #                   to be called by the machine
    # =======================================================================
    def invokeBroker(self):
        self.call=True
        
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exitBroker(self):
        self.call=False
        
    

                    
        