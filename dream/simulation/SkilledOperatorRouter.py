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
    def __init__(self,sorting=False, outputSolutions=False):
        Router.__init__(self)
        # Flag used to notify the need for re-allocation of skilled operators to operatorPools
        self.allocation=False
        # Flag used to notify the need to wait for endedLastProcessing signal
        waitEndProcess=False
        self.outputSolutions=outputSolutions
        
    #===========================================================================
    #                         the initialize method
    #===========================================================================
    def initialize(self):
        Router.initialize(self)        
        self.allocation=False
        self.waitEndProcess=False
        self.pendingQueues=[]
        self.pendingMachines=[]
        self.previousSolution={}
        self.solutionList=[]
        
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
            
            self.expectedSignals['isCalled']=1
            
            yield self.isCalled
            
            transmitter, eventTime=self.isCalled.value
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
                    station.wip=1+(len(station.getActiveObjectQueue())/station.capacity)
                    for predecessor in station.previous:
                        try:
                            station.wip+=float(len(predecessor.getActiveObjectQueue())/float(predecessor.capacity))
                        except:
                            # XXX what happens in the case of sources or infinite-capacity-queues
                            pass

                #===================================================================
                # # stations of the line and their corresponding WIP
                # TODO: the WIP of the stations must be normalised to the max WIP possible on that station
                #===================================================================
                self.availableStationsDict={}
                for station in self.availableStations:
                    self.availableStationsDict[str(station.id)]={'stationID':str(station.id),'WIP':station.wip, 'lastAssignment':self.env.now}
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
                    if operator.available and operator.onShift:
                        self.availableOperatorList.append(operator.id)
                #===================================================================
                # # XXX run the LP assignment algorithm
                # #     should return a list of correspondences
                # # XXX signal the stations that the assignment is complete
                # TODO: a constant integer must be added to all WIP before provided to the opAss_LP
                #     as it doesn't support zero WIP levels
                #===================================================================
                solution=opAss_LP(self.availableStationsDict, self.availableOperatorList, 
                                  self.operators, previousAssignment=self.previousSolution)
#                 print '-------'
#                 print self.env.now, solution
                
                if self.outputSolutions:
                    self.solutionList.append({
                        "time":self.env.now,
                        "allocation":solution
                    })
                
                # XXX assign the operators to operatorPools
                # pendingStations/ available stations not yet given operator
                self.pendingStations=[]
                from Globals import findObjectById
                # apply the solution
                # loop through the entries in the solution dictionary
                for operatorID in solution.keys():
                    # obtain the operator and the station
                    operator=findObjectById(operatorID)
                    station=findObjectById(solution[operatorID])
                    if operatorID in self.previousSolution:
                        # if the solution returned the operator that is already in the station
                        # then no signal is needed
                        if not self.previousSolution[operatorID] == solution[operatorID]:
                            self.toBeSignalled.append(station)
                    else:
                        self.toBeSignalled.append(station)
                    # update the operatorPool of the station
                    station.operatorPool.operators=[operator]
                    # assign the operator to the station
                    operator.assignTo(station)
                    # set that the operator is dedicated to the station
                    operator.operatorDedicatedTo=station
                    # set in every station the operator that it is to get
                    station.operatorToGet=operator
                    # remove the operator id from availableOperatorList
                    self.availableOperatorList.remove(operatorID)

                #===================================================================
                # # XXX signal the stations that the assignment is complete
                #===================================================================             
                # if the operator is free the station can be signalled right away
                stationsProcessingLast=[]
                toBeSignalled=list(self.toBeSignalled)
                for station in toBeSignalled:
                    # check if the operator that the station waits for is free
                    operator=station.operatorToGet
                    if operator.workingStation:
                        if operator.workingStation.isProcessing:
                            stationsProcessingLast.append(operator.workingStation)
                            continue
                    # signal the station so that it gets the operator
                    self.signalStation(station, operator)
                
                # else wait for signals that operator became available and signal the stations
                self.expectedFinishSignalsDict={}
                self.expectedFinishSignals=[]
                for station in stationsProcessingLast:
                    signal=self.env.event()
                    self.expectedFinishSignalsDict[station.id]=signal
                    self.expectedFinishSignals.append(signal)
                while self.expectedFinishSignals:
                    receivedEvent = yield self.env.any_of(self.expectedFinishSignals)
                    for signal in self.expectedFinishSignals:
                        if signal in receivedEvent:
                            transmitter, eventTime=signal.value
                            assert eventTime==self.env.now, 'the station finished signal must be received on the time of request'
                            self.expectedFinishSignals.remove(signal)                   
                            del self.expectedFinishSignalsDict[transmitter.id]
                            for id in solution.keys():
                                operator=findObjectById(id)
                                station=findObjectById(solution[id])
                                if station in self.toBeSignalled:
                                    # signal the station so that it gets the operator
                                    self.signalStation(station, operator)
          
            
            #===================================================================
            # default behaviour
            #===================================================================
            else:
                # entry actions
                self.entryActions()
                # run the routine that allocates operators to machines
                self.allocateOperators()
                # assign operators to stations
                self.assignOperators()
                # unAssign exits
                self.unAssignExits()
                # signal the stations that ought to be signalled
                self.signalOperatedStations()
            
            
            self.previousSolution=solution
            self.printTrace('', 'router exiting')
            self.printTrace('','=-'*20)
            self.exitActions()
    
    # =======================================================================
    #                 signal the station or the Queue to impose the assignment
    # =======================================================================
    def signalStation(self, station, operator):
        # signal this station's broker that the resource is available
        if station.broker.waitForOperator:
            if station.broker.expectedSignals['resourceAvailable']:
                self.sendSignal(receiver=station.broker, signal=station.broker.resourceAvailable)
                self.printTrace('router', 'signalling broker of'+' '*50+station.id)
                self.toBeSignalled.remove(station)
        # signal the queue proceeding the station
        else:         
            if station.canAccept()\
                    and any(type=='Load' for type in station.multOperationTypeList):
                if station.expectedSignals['loadOperatorAvailable']:
                    self.sendSignal(receiver=station, signal=station.loadOperatorAvailable)
                    self.printTrace('router', 'signalling'+' '*50+station.id)
                    self.toBeSignalled.remove(station)      
                    
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exitActions(self):
        Router.exitActions(self)
        self.allocation=False
        self.waitEndProcess=False
    
    def postProcessing(self):
        if self.outputSolutions:
            self.solutionList.append({
                    "time":self.env.now,
                    "allocation":{}
                })
    
    def outputResultsJSON(self):
        if self.outputSolutions:
            from Globals import G
            json = {'_class': 'Dream.%s' % self.__class__.__name__,
                    'id': self.id,
                    'results': {}}
            json['results']['solutionList'] = self.solutionList
            G.outputJSON['elementList'].append(json)
    
    
    