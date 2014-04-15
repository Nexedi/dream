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

from SimPy.Simulation import Process, Resource, SimEvent
from ObjectInterruption import ObjectInterruption
from SimPy.Simulation import waituntil, now, hold, request, release, waitevent

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
        # variables that have to do with timing
        self.timeOperationStarted = 0
        self.timeLastOperationEnded = 0
        self.timeWaitForOperatorStarted=0
        # Broker events
        self.brokerIsCalled=SimEvent('brokerIsCalled')
        self.victimQueueIsEmpty=SimEvent('victimQueueIsEmpty')
        self.resourceAvailable=SimEvent('resourceAvailable')
        
    #===========================================================================
    #                           the initialize method
    #===========================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.timeLastOperationEnded=0
        self.timeOperationStarted=0
        self.timeWaitForOperatorStarted=0
        
    # =======================================================================
    #                          the run method
    # =======================================================================    
    def run(self):
        while 1:
            # TODO: add new broker event - brokerIsCalled
            yield waitevent, self, self.brokerIsCalled
            assert self.brokerIsCalled.signalparam==now(), 'the broker should be granted control instantly'
    # ======= request a resource
            if self.victim.isOperated()\
                and any(type=='Load' or type=='Setup' or type=='Processing'\
                        for type in self.victim.multOperationTypeList):
                # update the time that the station is waiting for the operator
                self.timeWaitForOperatorStarted=now()
                # TODO: cannot wait till the operatorPool has available resources. 
                #     They are supposed to be available for the Broker to be called
                if not self.victim.operatorPool.checkIfResourceIsAvailable():
                    yield waitevent, self, self.resourceAvailable
                assert self.victim.operatorPool.checkIfResourceIsAvailable(), 'there is no available operator to request'
                # set the available resource as the currentOperator
                self.victim.currentOperator=self.victim.operatorPool.findAvailableOperator()
                yield request, self, self.victim.operatorPool.getResource(self.victim.currentOperator)
                #===============================================================
#                 # TESTING
#                 print now(), self.victim.currentOperator.objName, 'started work in ', self.victim.id
                #===============================================================
                # clear the timeWaitForOperatorStarted variable
                self.timeWaitForOperatorStarted = 0
                # update the time that the operation started
                self.timeOperationStarted = now()
                self.victim.outputTrace(self.victim.currentOperator.objName, "started work in "+ self.victim.objName)
                self.victim.currentOperator.timeLastOperationStarted=now()
    # ======= release a resource        
            elif not self.victim.isOperated():
                self.victim.currentOperator.totalWorkingTime+=now()-self.victim.currentOperator.timeLastOperationStarted                
                # TODO: cannot be implemented at the moment as the Machine first releases the operator and then 
                #       signals the receiver when the removeEntity signals the victimQueueIsEmpty
                # if the victim releasing the operator has receiver
#                 if self.victim.receiver:
#                     # if the following object is not of type Machine
#                     if self.victim.receiver.type!='Machine':
#                         # if the processingType is 'Processing' and not only 'Load' or 'Setup'
#                         if any(type=='Processing' for type in self.victim.multOperationTypeList):
#                             # wait until the victim has released the entity it was processing
#                             # TODO: add new event, to be signalled from the Machine removeEntity
#                             yield waitevent, self, self.victimQueueIsEmpty
#                             assert self.victimQueueIsEmpty.signalparam==now(), 'the broker should be granted control instantly'
                #self.victim.outputTrace(self.victim.currentOperator.objName, "left "+ self.victim.objName)
                yield release,self,self.victim.operatorPool.getResource(self.victim.currentOperator)
                # signal the other brokers waiting for the same operators that they are now free
                # also signal the stations that were not requested to receive because the operator was occupied
                #     but now must have the option to proceed
                from Globals import G
                candidateMachines=[]
                pendingMachines=[]
                # run through the operatorPools
                for operatorpool in G.OperatorPoolsList:
                    # and find the machines the share the currentOperator with the Broker.victim
                    if self.victim.currentOperator in operatorpool.operators:
                        for machine in operatorpool.coreObjects:
                            # if the machine waits to get an operator add it to the candidateMachines local list
                            if machine.broker.timeWaitForOperatorStarted:
                                candidateMachines.append(machine)
                            # cause an loadOperatorAvailable event if any of this machines can accept and has Load operation type defined
                            if machine.canAccept() and any(type=='Load' for type in machine.multOperationTypeList):
                                #===============================================
#                                 # TESTING
#                                 print now(), self.victim.id, 'broker signalling', machine.id, 'loadOperatorAvailable'
                                #===============================================
                                machine.loadOperatorAvailable.signal(now())
                # for the candidateMachines
                if candidateMachines:
                    maxTimeWaiting=0
                    receiver=None
                # choose the one that waits the most time and assign give it the chance to grasp the resource
                    for machine in candidateMachines:
                        timeWaiting=now()-machine.broker.timeWaitForOperatorStarted
                        if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                            maxTimeWaiting=timeWaiting
                            receiver=machine
                    #===========================================================
#                     # TESTING
#                     print now(), self.victim.id, 'broker signalling', machine.id, 'resourceAvailable'
                    #===========================================================
                    # finally signal the machine to receive the operator
                    receiver.broker.resourceAvailable.signal(now())
                
                #===============================================================
#                 # TESTING
#                 print now(), self.victim.currentOperator.objName, 'released', self.victim.id
                #===============================================================
                # the victim current operator must be cleared after the operator is released
                self.timeLastOperationEnded = now()
                self.victim.currentOperator = None
            else:
                pass
            # TODO: exit method can perform the signalling 
            # TODO: the victim must have a new event brokerIsSet
            self.victim.brokerIsSet.signal(now())
            