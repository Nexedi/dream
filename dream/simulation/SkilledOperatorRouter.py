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
import Globals

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
    def __init__(self,id='SkilledRouter01',name='SkilledRouter01',sorting=False,outputSolutions=True,
                 weightFactors=[2, 1, 0, 2, 0, 1], tool={},checkCondition=False,twoPhaseSearch=False,**kw):
        Router.__init__(self)
        # Flag used to notify the need for re-allocation of skilled operators to operatorPools
        self.allocation=False
        # Flag used to notify the need to wait for endedLastProcessing signal
        waitEndProcess=False
        self.outputSolutions=outputSolutions
        self.id=id
        self.name=name
        self.weightFactors=weightFactors
        self.tool=tool
        self.checkCondition=checkCondition
        self.twoPhaseSearch=twoPhaseSearch
                
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
                
                # identify the last time that there was an assignment
                maxLastAssignment=0
                for record in self.solutionList:
                    if record:
                        maxLastAssignment=record["time"]

                self.availableStationsDict={}
                for station in self.availableStations:
                    lastAssignmentTime=0
                    for record in self.solutionList:
                        if station.id in record["allocation"].values():
                            lastAssignmentTime=record["time"]
                    
                    # normalise the lastAssignmentTime based on the maxLastAssignment. 
                    if maxLastAssignment:
                        lastAssignmentTime=1.0-float(lastAssignmentTime/float(maxLastAssignment))
                    
                    # it there is definition of 'technology' to group machines add this
                    if station.technology:
                        self.availableStationsDict[str(station.id)]={'stationID':station.technology,'machineID':station.id, 
                                                                'WIP':station.wip,'lastAssignment':lastAssignmentTime}
                    # otherwise add just the id
                    else:
                        self.availableStationsDict[str(station.id)]={'stationID':station.id, 
                                                                'WIP':station.wip,'lastAssignment':lastAssignmentTime}                       
                        
                #===================================================================
                # # operators and their skills set
                #===================================================================
                self.operators={}
                import Globals
                for operator in G.OperatorsList:
                    newSkillsList=[]
                    for skill in operator.skillsList:
                        newSkill=skill
                        mach=Globals.findObjectById(skill)
                        # if there is 'technology' defined for the stations send this to the LP solver
                        if mach.technology: 
                            newSkill=mach.technology
                        if newSkill not in newSkillsList:
                            newSkillsList.append(newSkill)
                    self.operators[str(operator.id)]=newSkillsList
                #===================================================================
                # # available operators
                #===================================================================
                self.availableOperatorList=[]
                for operator in G.OperatorsList:
                    if operator.available and operator.onShift and not operator.onBreak:
                        self.availableOperatorList.append(operator.id)
                        
                        
                LPFlag=True
                if self.checkCondition:
                    LPFlag=self.checkIfAllocationShouldBeCalled() 
                        
                #===================================================================
                # # XXX run the LP assignment algorithm
                # #     should return a list of correspondences
                # # XXX signal the stations that the assignment is complete
                # TODO: a constant integer must be added to all WIP before provided to the opAss_LP
                #     as it doesn't support zero WIP levels
                #===================================================================
                import time
                startLP=time.time()
                if LPFlag:
                    if self.twoPhaseSearch:
                        # remove all the blocked machines from the available stations
                        # and create another dict only with them
                        machinesForSecondPhaseDict={}
                        for stationId in self.availableStationsDict.keys():
                            machine = Globals.findObjectById(stationId)
                            nextObject = machine.next[0]
                            nextObjectClassName = nextObject.__class__.__name__
                            reassemblyBlocksMachine = False
                            if 'Reassembly' in nextObjectClassName:
                                if nextObject.getActiveObjectQueue():
                                    if nextObject.getActiveObjectQueue()[0].type == 'Batch': 
                                        reassemblyBlocksMachine = True
                            if machine.isBlocked or reassemblyBlocksMachine:
                                if not len(machine.getActiveObjectQueue()) and (not reassemblyBlocksMachine):
                                    raise ValueError('empty machine considered as blocked')
                                if machine.timeLastEntityEnded < machine.timeLastEntityEntered:
                                    raise ValueError('machine considered as blocked, while it has Entity that has not finished')
                                if "Queue" in nextObjectClassName:
                                    if len(nextObject.getActiveObjectQueue()) != nextObject.capacity:
                                        raise ValueError('Machine considered as blocked while Queue has space') 
                                if "Clearance" in nextObjectClassName:
                                    if not nextObject.getActiveObjectQueue():
                                        raise ValueError('Machine considered as blocked while Clearance is empty')
                                    else:
                                        subBatchMachineHolds = machine.getActiveObjectQueue()[0]
                                        subBatchLineClearanceHolds = nextObject.getActiveObjectQueue()[0]
                                        if subBatchMachineHolds.parentBatch == subBatchLineClearanceHolds.parentBatch and\
                                                (len(nextObject.getActiveObjectQueue()) != nextObject.capacity):
                                            raise ValueError('Machine considered as blocked while Line Clearance holds same batch and has space')
                                machinesForSecondPhaseDict[stationId] = self.availableStationsDict[stationId]
                                del self.availableStationsDict[stationId]
                            else:
                                if len(machine.getActiveObjectQueue()) and (not machine.isProcessing) and\
                                         machine.onShift and machine.currentOperator:
                                    raise ValueError('machine should be considered blocked')
                                
                        
                        # run the LP method only for the machines that are not blocked
                        solution=opAss_LP(self.availableStationsDict, self.availableOperatorList, 
                                          self.operators, previousAssignment=self.previousSolution,
                                          weightFactors=self.weightFactors,Tool=self.tool)
                        # create a list with the operators that were sent to the LP but did not get allocated
                        operatorsForSecondPhaseList=[]
                        for operatorId in self.availableOperatorList:
                            if operatorId not in solution.keys():
                                operatorsForSecondPhaseList.append(operatorId)
                        # in case there is some station that did not get operator even if it was not blocked
                        # add them alos for the second fail (XXX do not think there is such case)
                        for stationId in self.availableStationsDict.keys():
                            if stationId not in solution.values():
                                machinesForSecondPhaseDict[stationId] = self.availableStationsDict[stationId]
                        # if there are machines and operators for the second phase
                        # run again the LP for machines and operators that are not in the former solution
                        if machinesForSecondPhaseDict and operatorsForSecondPhaseList:
                            secondPhaseSolution=opAss_LP(machinesForSecondPhaseDict, operatorsForSecondPhaseList, 
                                              self.operators, previousAssignment=self.previousSolution,
                                              weightFactors=self.weightFactors,Tool=self.tool)
                            # update the solution with the new LP results
                            solution.update(secondPhaseSolution)
                    else:
                        solution=opAss_LP(self.availableStationsDict, self.availableOperatorList, 
                                          self.operators, previousAssignment=self.previousSolution,
                                          weightFactors=self.weightFactors,Tool=self.tool)
                else:
                    # if the LP is not called keep the previous solution
                    # if there are no available operators though, remove those
                    solution=self.previousSolution
                    for operatorID in solution.keys():
                        if not operatorID in self.availableOperatorList:
                            del solution[operatorID]
                    
#                 print '-------'
#                 print self.env.now, solution
#                 print 'time needed',time.time()-startLP
                
                self.solutionList.append({
                    "time":self.env.now,
                    "allocation":solution
                })
                
                # XXX assign the operators to operatorPools
                # pendingStations/ available stations not yet given operator
                self.pendingStations=[]
                from Globals import findObjectById
                # apply the solution
                
                # loop through the stations. If there is a station that should change operator
                # set the operator dedicated to None and also release operator
                for station in G.MachineList:
                    # obtain the operator and the station
                    if station.currentOperator:
                        operator=station.currentOperator
                        previousAssignment=self.previousSolution.get(operator.id,None)
                        currentAssignment=solution.get(operator.id,None)
                        if (not previousAssignment == currentAssignment):
                            operator.operatorDedicatedTo=None
                            if not station.isProcessing:
                                station.releaseOperator()
                
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
                        # if the operator is in a station that is processing or just starts processing then he/she is not free
                        if operator.workingStation.isProcessing or (not (operator.workingStation.timeLastEntityEntered==self.env.now)):
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
                            # signal also the other stations that should be signalled
                            for id in solution.keys():
                                operator=findObjectById(id)
                                station=findObjectById(solution[id])
                                signal=True                                       
                                # signal only the stations in the original list
                                if station not in self.toBeSignalled:
                                    signal=False
                                # signal only if the operator is free 
                                if operator.workingStation:
                                    if operator.workingStation.isProcessing\
                                             or (not (operator.workingStation.timeLastEntityEntered==self.env.now)):
                                        signal=False
                                if signal:
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
        
    def checkIfAllocationShouldBeCalled(self):
        from Globals import G
        # loop through the operators and the machines. 
        # If for one the shift ended or started right now allocation is needed
        for obj in G.OperatorsList+G.MachineList:
            
            if (obj.timeLastShiftEnded==self.env.now) or (obj.timeLastShiftStarted==self.env.now):
                return True
        # loop through the machines
        for machine in G.MachineList:
            # if one machine is starved more than 30 then allocation is needed
            if (self.env.now-machine.timeLastEntityLeft>=30) and (not machine.getActiveObjectQueue()):
                return True
            # check for the previous buffer. If it is more than 80% full allocation is needed 
            previousQueue=self.getPreviousQueue(machine)
            if previousQueue:
                if float(len(previousQueue.getActiveObjectQueue()))/float(previousQueue.capacity)>=0.8:
                    return True
        return False   
    
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
    
    # for a machine gets the decomposition and the buffer (if any)
    def getPreviousList(self, machine):
        previousList=[]
        predecessor=machine.previous[0]
        while 1:
            if "Reassembly" in str(predecessor.__class__) or "Source" in str(predecessor.__class__):
                break
            previousList.append(predecessor)
            predecessor=predecessor.previous[0]
        return previousList
    
    # for a machine gets the previous queue (if any)
    def getPreviousQueue(self, machine):
        predecessor=machine.previous[0]
        while 1:
            if "Source" in str(predecessor.__class__):
                return None
            if "Queue" in str(predecessor.__class__) or "Clearance" in str(predecessor.__class__):
                return predecessor
            predecessor=predecessor.previous[0]

    
    # for a machine gets a list with the parallel machines
    def getParallelMachinesList(self, machine):
        alreadyConsidered=[machine]
        parallelMachinesList=[]
        previousObject=machine.previous[0]
        while 1:
            if "Reassembly" in str(previousObject.__class__) or "Source" in str(previousObject.__class__)\
                        or "Queue" in str(previousObject.__class__) or "Clearance" in str(previousObject.__class__):
                break
            alreadyConsidered.append(previousObject)
            previousObject=previousObject.previous[0]
        for nextObject in previousObject.next:
            while 1:
                if nextObject in alreadyConsidered:
                    break
                if "Machine" in str(nextObject.__class__) or "M3" in str(nextObject.__class__):
                    parallelMachinesList.append(nextObject)
                    break
                nextObject=nextObject.next[0]
        return parallelMachinesList
    
    
    