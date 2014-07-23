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
import simpy

from OperatorRouter import Router
from opAss_LPmethod import opAss_LP

# ===========================================================================
#               Class that handles the Operator Behavior
# ===========================================================================
class SkilledRouter(Router):
    
    # =======================================================================
    #   according to this implementation one machine per broker is allowed
    #     The Broker is initiated within the Machine and considered as 
    #                black box for the ManPy end Developer
    # TODO: we should maybe define a global schedulingRule criterion that will be 
    #         chosen in case of multiple criteria for different Operators
    # ======================================================================= 
    def __init__(self,sorting=False):
        Router.__init__(self)
        # Flag used to notify the need for re-allocation of skilled operators to operatorPools
        self.allocation=False
        # Flag used to notify the need to wait for endedLastProcessing signal
        waitEndProcess=False
        
    #===========================================================================
    #                         the initialize method
    #===========================================================================
    def initialize(self):
        Router.initialize(self)        
        self.allocation=False
        self.waitEndProcess=False
        self.pendingQueues=[]
        self.pendingMachines=[]
        self.pendingObjects=[]
        
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
            yield self.isCalled
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
            
            from Globals import G
            
            if self.allocation:
                #===================================================================
                # # XXX wait for the interval time to finish (10 minutes between reassignments
                #===================================================================
                '''not implemented yet'''
                
                #===================================================================
                # # find stations that are in position to process
                #===================================================================
                self.availableStations=[]
                for station in G.MachineList:
                    if station.checkIfActive():
                        self.availableStations.append(station)
                
                
                
                
                if self.waitEndProcess:
                    #===================================================================
                    # # XXX wait till all the stations have finished their current WIP
                    # # XXX find all the machines that are currently busy
                    #===================================================================
                    self.busyStations=[]
                    for station in self.availableStations:
                        if station.getActiveObjectQueue() and not station.waitToDispose:
                            self.busyStations.append(station)
                    #===================================================================
                    # # XXX create a list of all the events (endLastProcessing)
                    #===================================================================
                    self.endProcessingSignals=[]
                    for station in self.busyStations:
                        self.endProcessingSignals.append(station.endedLastProcessing)
                        station.isWorkingOnTheLast=True
                        # FIX this will fail as the first machine sends the signal (router.waitingSingnal-> False)
                        self.waitingSignal=True
                    #===================================================================
                    # # XXX wait till all the stations have finished their current WIP
                    #===================================================================
                    # TODO: fix that, add flags, reset the signals
                    receivedEvent=yield self.env.all_of(self.endProcessingSignals)
                    for station in self.busyStations:
                        if station.endedLastProcessing in receivedEvent:
                            station.endedLastProcessing=self.env.event()
                
                
                #===================================================================
                # # XXX if the resources are still assigned then un-assign them from the machines they are currently assigned
                # #     the same for all the objects exits 
                #===================================================================
                for operator in [x for x in G.OperatorsList if x.isAssignedTo()]:
                    operator.unAssign()
                for object in [x for x in G.ObjList if x.exitIsAssignedTo()]:
                    object.unAssignExit()
                #===================================================================
                # # XXX un-assign all the PBs from their operatorPools
                #===================================================================
                for station in G.MachineList:
                    station.operatorPool.operators=[]
                
                #===================================================================
                # # XXX calculate the WIP of each station
                #===================================================================
                for station in self.availableStations:
                    station.wip=0
                    for predecessor in station.previous:
                        predecessor.remainingWip=0
                        if len(predecessor.next)>1:
                            nextNo=len(predecessor.next)
                            for obj in predecessor.next:
                                if not obj in self.availableStations:
                                    nextNo-=1
                            station.wip=int(round(len(predecessor.getActiveObjectQueue())/nextNo))
                            predecessor.remainingWip=len(predecessor.getActiveObjectQueue()) % nextNo
                for buffer in G.QueueList:
                    if buffer.remainingWip:
                        nextObj=next(x for x in buffer.next if x in self.availableStations) # pick the first of the list available
                        nextObj.wip+=buffer.remainingWip
                        buffer.remainingWip=0
                #===================================================================
                # # stations of the line and their corresponding WIP
                # TODO: the WIP of the stations must be normalised to the max WIP possible on that station
                #===================================================================
                self.availableStationsDict={}
                for station in self.availableStations:
                    self.availableStationsDict[str(station.id)]={'stationID':str(station.id),'WIP':station.wip}
                #===================================================================
                # # operators and their skills set
                #===================================================================
                self.operators={}
                for operator in G.OperatorsList:
                    self.operators[str(operator.id)]=operator.skillsList
                #===================================================================
                # # available operators
                #===================================================================
                self.availableOperatorList=[]
                for operator in G.OperatorsList:
                    if operator.available:
                        self.availableOperatorList.append(operator.id)
                #===================================================================
                # # XXX run the LP assignment algorithm
                # #     should return a list of correspondences
                # # XXX signal the stations that the assignment is complete
                # TODO: a constant integer must be added to all WIP before provided to the opAss_LP
                #     as it doesn't support zero WIP levels
                #===================================================================
                solution=opAss_LP(self.availableStationsDict, self.availableOperatorList, self.operators)
                # XXX assign the operators to operatorPools
                # pendingStations/ available stations not yet given operator
                self.pendingStations=[]
                for operator in solution.keys():
                    for resource in G.OperatorsList:
                        if resource.id==operator:
                            station=findObjectById(solution[operator])
                            station.operatorPool.operators=[resource]
                            resource.assignTo(station)
                            self.toBeSignalled.append(station)
                            self.availableOperatorList.pop(resource)
                            break
                if len(solution)!=len(self.availableStations):
                    from Globals import findObjectById
                    for station in self.availableStations:
                        if not station.id in solution.keys():
                            for i in range(len(self.availableOperatorList)):
                                for resource in G.OperatorsList:
                                    if resource.id==self.availableOperatorList[i]:
                                        candidate=resource
                                if station.id in candidate.skillsList:
                                    operatorID=self.availableOperatorList.pop(i)
                                    break
                            #operator=findObjectById(operatorID)
                            for resource in G.OperatorsList:
                                if resource.id==operatorID:
                                    operator=resource
                            station.operatorPool.operators=[operator]
                            operator.assignTo(station)
                            self.toBeSignalled.append(station)
                #===================================================================
                # # XXX signal the stations that the assignment is complete
                #===================================================================
                for station in self.toBeSignalled:
                    if station.broker.waitForOperator:
                        # signal this station's broker that the resource is available
                        self.printTrace('router', 'signalling broker of'+' '*50+station.id)
                        station.broker.resourceAvailable.succeed(self.env.now)
                    else:
                        # signal the queue proceeding the station
                        if station.canAccept()\
                                and any(type=='Load' for type in station.multOperationTypeList):
                            self.printTrace('router', 'signalling'+' '*50+station.id)
                            station.loadOperatorAvailable.succeed(self.env.now)
            
            #===================================================================
            # default behaviour
            #===================================================================
            else:
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
                self.sortCandidateEntities()
                # find the entity that will occupy the resource, and the station that will receive it (if any available)
                #  entities that are already in stations have already a receiver
                self.findCandidateReceivers()
                # assign operators to stations
                self.assignOperators()
    
                for operator in [x for x in self.candidateOperators if x.isAssignedTo()]:
                    if not operator.isAssignedTo() in self.pendingObjects:
                        for object in [x for x in operator.isAssignedTo().previous if x.exitIsAssignedTo()]:
                            if object.exitIsAssignedTo()!=operator.isAssignedTo():
                                object.unAssignExit()
                # if an object cannot proceed with getEntity, unAssign the exit of its giver
                for object in self.pendingQueues:
                    if not object in self.toBeSignalled:
                        object.unAssignExit()
                # signal the stations that ought to be signalled
                self.signalOperatedStations()
            
            self.printTrace('', 'router exiting')
            self.printTrace('','=-'*20)
            self.exit()
    
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exit(self):
        Router.exit(self)
        self.allocation=False
        self.waitEndProcess=False
    