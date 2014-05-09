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
        self.isCalled=SimEvent('brokerIsCalled')
        self.victimQueueIsEmpty=SimEvent('victimQueueIsEmpty')
        self.resourceAvailable=SimEvent('resourceAvailable')
        self.waitForOperator=False
        
    #===========================================================================
    #                           the initialize method
    #===========================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.timeLastOperationEnded=0
        self.timeOperationStarted=0
        self.timeWaitForOperatorStarted=0
        self.waitForOperator=False
        
    # =======================================================================
    #                          the run method
    # TODO: have to signal Router that broker is asking operator, and wait till the Router decides
    # =======================================================================    
    def run(self):
        while 1:
            # TODO: add new broker event - brokerIsCalled
            yield waitevent, self, self.isCalled
            assert self.isCalled.signalparam==now(), 'the broker should be granted control instantly'
    # ======= request a resource
            if self.victim.isOperated()\
                and any(type=='Load' or type=='Setup' or type=='Processing'\
                        for type in self.victim.multOperationTypeList):
#                 print now(), self.victim.id, 'broker is invoked'
                # update the time that the station is waiting for the operator
                self.timeWaitForOperatorStarted=now()                
                # if the resource is not available wait until a rousourceAvailable event
                if not self.victim.operatorPool.checkIfResourceIsAvailable():
                    self.waitForOperator=True
#                     print now(), self.victim.id, 'broker waits till resource is available1'
                    yield waitevent, self, self.resourceAvailable
                    self.waitForOperator=False
#                     print self.victim.id, 'received resourceAvailable event'
                # if there are machines waiting for the same resources (broker.waitForOperator==True) check if they wait for longer
                #     and if yes then wait also for the same event
                else:
                    from Globals import G
                    for machine in [station for station in G.MachineList if station.operatorPool is self.victim.operatorPool]:
                        if machine.broker.waitForOperator:
                            self.waitForOperator=True
#                             print now(), self.victim.id, 'broker waits till resource is available2'
                            yield waitevent, self, self.resourceAvailable
                            self.waitForOperator=False
#                             print self.victim.id, 'received resourceAvailable event'
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
                #===============================================================
                # TESTING
#                 print now(), self.victim.id, 'broker                                             signalling ROUTER'
                #===============================================================
                # TODO: signalling the router must be done more elegantly, router must be set as global variable
                # if the router is already invoked then do not signal it again
                if not self.victim.router.invoked:
                    self.victim.router.invoked=True
                    self.victim.router.isCalled.signal(now())
                # TODO: signalling the router will give the chance to it to take the control, but when will it eventually receive it. 
                #     after signalling the broker will signal it's victim that it has finished it's processes 
                # TODO: this wont work for the moment. The actions that follow must be performed by all operated brokers. 
#                 self.signalLoadStations()
                
                #===============================================================
#                 # TESTING
#                 print now(), self.victim.currentOperator.objName, 'released', self.victim.id
                #===============================================================
                # the victim current operator must be cleared after the operator is released
                self.timeLastOperationEnded = now()
                self.victim.currentOperator = None
            else:
                pass
            # TODO: the victim must have a new event brokerIsSet
            self.victim.brokerIsSet.signal(now())
            
#     #===========================================================================
#     # signal stations that wait for load operators
#     #===========================================================================
#     def signalLoadStations(self):
#         # signal the other brokers waiting for the same operators that they are now free
#         # also signal the stations that were not requested to receive because the operator was occupied
#         #     but now must have the option to proceed
#         from Globals import G
#         candidateMachines=[]
#         loadPendingMachines=[]
# #         print '        have to signal machines that are waiting for operator', self.victim.id, 'broker'
#         # run through the operatorPools
#         # TODO: MachineManagedJob operatorPool is not in the global OperatorPoolsList
#         for operatorpool in G.OperatorPoolsList:
# #             print operatorpool.id
#             # and find the machines the share the currentOperator with the Broker.victim
#             if self.victim.currentOperator in operatorpool.operators:
# #                 print '                current operator in other operatorPools', operatorpool.id
# #                 print '                            ', [str(x.id) for x in operatorpool.coreObjects]
#                 for machine in operatorpool.coreObjects:
#                     # if the machine waits to get an operator add it to the candidateMachines local list
#                     if machine.broker.waitForOperator:
#                         candidateMachines.append(machine)
#                     # cause an loadOperatorAvailable event if any of this machines can accept and has Load operation type defined
#                     if machine.canAccept() and any(type=='Load' for type in machine.multOperationTypeList):
#                         loadPendingMachines.append(machine)
#                         #===============================================
# #                         # TESTING
#                         print now(), self.victim.id, 'broker signalling', machine.id, 'loadOperatorAvailable1'
#                         #===============================================
#                         machine.loadOperatorAvailable.signal(now())
#                         
#         # if the machines are MachineManagedJobs their OperatorPool is empty while their canAcceptAndIsRequested has not returned True
#         #     In order to signal them that the loadOperator is free, find the entities that have that operator, search for the possible receivers that 
#         #     can accept signal them
#         for machine in G.MachineManagedJobList:
#             if self.victim.currentOperator in machine.operatorPool.operators:
#                 if machine.broker.waitForOperator:
#                     candidateMachines.append(machine)
#             for entity in G.pendingEntities:
#                 if machine.canAcceptEntity(entity) and any(type=='Load' for type in machine.multOperationTypeList):
#                     loadPendingMachines.append(machine)
#                     #===============================================
# #                     # TESTING
#                     print now(), self.victim.id, 'broker signalling                                ', machine.id, 'loadOperatorAvailable2'
#                     #===============================================
#                     machine.loadOperatorAvailable.signal(now())
#                         
# #         print 'machines waitingForLoadOperator',[str(x.id) for x in loadPendingMachines]
# #         print 'machines waitingForOperator',[str(x.id) for x in candidateMachines]
#         
#                 
#         # for the candidateMachines
#         if candidateMachines:
#             maxTimeWaiting=0
#             receiver=None
#         # choose the one that waits the most time and give it the chance to grasp the resource
#             for machine in candidateMachines:
#                 timeWaiting=now()-machine.broker.timeWaitForOperatorStarted
#                 if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
#                     maxTimeWaiting=timeWaiting
#                     receiver=machine
#             #===========================================================
# #             # TESTING
# #             print now(), self.victim.id, 'broker signalling', machine.id, 'resourceAvailable'
#             #===========================================================
#             # finally signal the machine to receive the operator
#             receiver.broker.resourceAvailable.signal(now())
            