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
Created on 01 Oct 2013

@author: George
'''
'''
Job is an Entity that implements the logic of a job shop. Job carries attributes for its route 
in the system and also in the processing times at each station
'''

from Globals import G
from Entity import Entity

# =======================================================================
# The job object 
# =======================================================================
class Job(Entity):                                  # inherits from the Entity class   
    type='Job'
    family='Job'
    
    def __init__(self, id=None, name=None, route=[], priority=0, dueDate=0, orderDate=0, 
                 extraPropertyDict=None,remainingProcessingTime={}, remainingSetupTime={},currentStation=None, isCritical=False,**kw):
        Entity.__init__(self, id=id,name=name, priority=priority, dueDate=dueDate,
                        remainingProcessingTime=remainingProcessingTime, remainingSetupTime=remainingSetupTime,
                        currentStation=currentStation, orderDate=orderDate, isCritical=isCritical)
        # instance specific attributes 
        # information on the routing and the stops of the entity
        self.route=route          # the route that the job follows, 
                                                    # also contains the processing times in each station
        self.remainingRoute=list(route)             # the remaining route. in the beginning 
                                                    # this should be the same as the full route
        self.extraPropertyDict = extraPropertyDict
        # variable used to differentiate entities with and entities without routes
        self.family='Job'
        # append to G.JobList
        G.JobList.append(self)
        # used by printRoute
        self.alias='J'+str(len(G.JobList))
        # added for testing - flag that shows if the order and component routes are defined in the BOM
        self.routeInBOM=False
        # initialOperationTypes dictionary that shows if there are any manual operations to be performed if the Job is initial WIP at a machine
        if self.remainingRoute:
            # the setupType of the first step
            initialSetupType=self.remainingRoute[0].get('operationType',{}).get('Setup',0)       
            initialProcessingType=self.remainingRoute[0].get('operationType',{}).get('Processing',0)          
#             initialSetupType=0
#             if initialSetup:
#                 initialSetupType=initialSetup.get('operationType',0)
#             initialProcessing=self.remainingRoute[0].get('processingTime',{})    # the processingTime dict of the first step
#             initialProcessingType=0
#             if initialProcessing:
#                 initialProcessingType=initialProcessing.get('operationType',0)
            self.initialOperationTypes={"Setup":initialSetupType,
                                        "Processing":initialProcessingType}

    # =======================================================================
    # outputs results to JSON File 
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1):              #if we had just one replication output the results to excel
            json = { '_class': 'Dream.%s' % self.__class__.__name__,
                  'id': self.id,
                  'family': self.family,
                  'results': {} }
            #json['extraPropertyDict'] = self.extraPropertyDict
            # if there is schedule
            if self.schedule:
                #if the Job has reached an exit, input completion time in the results
                if self.schedule[-1][0].type=='Exit':
                    json['results']['completionTime']=self.schedule[-1][1]  
                    completionTime=self.schedule[-1][1]  
                # TODO
                # if the entity is of type Mould and the last object holding it is orderDecomposition
                # XXX now Orders do not run through the system but OrderDesigns do
                elif self.type=='OrderDesign' and self.schedule[-1][0].type=='OrderDecomposition': #
                    json['results']['completionTime']=self.schedule[-1][1]  
                    completionTime=self.schedule[-1][1]  
                # TODO : check if there is a need for setting a different 'type' for the MouldAssembly than 'Machine'
                #    ask Georgios if the method __class__.__name__ of finding the class type of the last step is correct
                # if the entity is of type orderComponent and the last step in it's schedule is Assembly
                elif self.type=='OrderComponent' and self.schedule[-1][0].__class__.__name__ in set(['MouldAssemblyManaged','MouldAssembly']):
                    json['results']['completionTime']=self.schedule[-1][1]  
                    completionTime=self.schedule[-1][1]  
                #else input "still in progress"
                else:
                    json['results']['completionTime']="still in progress"  
                    completionTime=None
                
                if completionTime and self.dueDate:
                    delay=completionTime-self.dueDate
                    json['results']['delay']=delay
                    
                json['results']['schedule']=[]
                i=0
                for record in self.schedule:               
                    json['results']['schedule'].append({})                              # dictionary holding time and 
                    json['results']['schedule'][i]['stationId']=record[0].id            # id of the Object
                    json['results']['schedule'][i]['entranceTime']=record[1]            # time entering the Object
                    i+=1             
                G.outputJSON['elementList'].append(json)
    
    # =======================================================================
    # initializes all the Entity for a new simulation replication 
    # =======================================================================
    def initialize(self):
        currentStationWellDefined=False
        # if the currentStation is defined and the route is given in the BOM
        if self.currentStation and self.routeInBOM:
            # find the current sequence given in the WIP in the entity's route
            for step in self.route:
                stepObjectIds=step.get('stationIdsList',[])
                if self.currentStation.id in stepObjectIds:
                    # find the corresponding station to the sequence 
                    ind=self.route.index(step)
                    # copy the route from that sequence on to the remainingRoute 
                    self.remainingRoute = self.route[ind:]
                    # correct the first step of the remainingRoute (only one station (currentStation) 
                    #     should be present in the stationIdsList of the firstStep) 
                    firstStep=self.remainingRoute[0]
                    firstStepStationIdsList=firstStep.get('stationIdsList',[])
                    assert self.currentStation.id in firstStepStationIdsList, 'the initialStation is not in the first step\'s stationIdsList'
                    firstStepStationIdsList=[str(self.currentStation.id)]
                    firstStep.pop('stationIdsList')
                    firstStep['stationIdsList']=firstStepStationIdsList
                    self.remainingRoute.pop(0)
                    self.remainingRoute.insert(0, firstStep)
                    currentStationWellDefined=True
                    break
            
        if not currentStationWellDefined:
            # has to be re-initialized each time a new Job is added
            self.remainingRoute=list(self.route)
            # check the number of stations in the stationIdsList for the current step (0)
            # if it is greater than 1 then there is a problem definition
            objectIds = self.route[0].get('stationIdsList',[])
            try:
                if len(objectIds)==1:
                    from Globals import findObjectById
                    self.currentStation=findObjectById(objectIds[0])
                else:
                    from Globals import SetWipTypeError
                    raise SetWipTypeError('The starting station of the the entity is not defined uniquely')
            except SetWipTypeError as setWipError:
                print 'WIP definition error: {0}'.format(setWipError)
    
    #===========================================================================
    # check if the requireParts of the entity next step sequence (route) have
    # have concluded the steps with sequence numbers smaller than the sequence
    # of the entity's next step in its route
    #===========================================================================
    def checkIfRequiredPartsReady(self):
        # if the entity is in a queue (currentSeq==0) then return false
        if self.currentStepSequence():
            return False
        # find the sequence of the next step in the route of the activeEntity
        nextSequence=self.nextStepSequence()
        # if no sequence is provided then return true
        if nextSequence==None:
            return True
        # flag that decides if the entity can proceed to the next station in its route
        mayProceed=False
        # find the required parts for the next step in the route (if any)
        requiredParts=self.getRequiredParts()
        # if there are required parts
        if requiredParts:
            # for each requested part
            for part in requiredParts:
                # retrieve the current step sequence of the requiredPart
                partCurrentSeq=part.currentStepSequence()
                # retrieve the next step sequence of the requiredParts
                partNextSeq=part.nextStepSequence()
                # if there is no next step sequence (route finished)
                # it means that the part has exhausted its route 
                # if the sequence of the required part next step is smaller than the sequence of activeEntity's next step
                # the activeEntity cannot proceed
                if partNextSeq>nextSequence or not partNextSeq:
                    # if the sequence of the requiredPart's currentStation is not zero then the 
                    # required part is currently being processed and thus the activeEntity cannot proceed
                    if not partCurrentSeq:
                        mayProceed=True
                    else:
                        mayProceed=False
                        break
                else:
                    mayProceed=False
                    break
        # if there are no requestedParts defined, then entity can proceed to the next step of its route
        else:
            mayProceed=True
        # if the local flag mayProceed is true then return true
        return mayProceed
    
    #===========================================================================
    # method that returns the requiredParts 
    # of a blocked entity at its current step sequence 
    #===========================================================================
    def getRequiredParts(self):
        # retrieve the IDs of the required parts in the next step sequence
        requiredParts=[]
        if self.remainingRoute:
            requiredPartsIDs=self.remainingRoute[0].get('requiredParts',[])
            # if there are requested parts
            if requiredPartsIDs:
                from Globals import findObjectById
                for partID in requiredPartsIDs:
                    # find the objects with the corresponding IDs
                    part=findObjectById(partID)
                    if not part in requiredParts:
                        requiredParts.append(part)
        return requiredParts
    
    #===========================================================================
    # method that returns the sequence of the entity's next step
    #===========================================================================
    def nextStepSequence(self):
        # find the sequence of the next step in the route of the activeEntity
        sequence=self.remainingRoute[0].get('sequence',None)
        return sequence
    
    #===========================================================================
    # method that returns the sequence of the entity's current step (returns zero if the entity is in a queue or orderDecomposition)
    #===========================================================================
    def currentStepSequence(self):
        currentStation=self.currentStation  # the current station of the part
        curStepSeq=0                        # the sequence of the current process in the parts route
        # if the part is being currently processed in a Station
        from Machine import Machine
        if issubclass(currentStation.__class__, Machine):
            for routeStep in self.route:
                stepSeq=routeStep.get('sequence',0)
                stepIDs=routeStep.get('stationIdsList',[])
                if currentStation.id in stepIDs:
                    curStepSeq=stepSeq
                    break
        return curStepSeq
    
    #===========================================================================
    # return the responsible operator for the current step
    #===========================================================================
    def responsibleForCurrentStep(self):
        ''' The route is supposed to provide information on the responsible personnel for
            the current (or next) station step in the sequence of the route
            E.g. 
            {
                "stepNumber": "6",
                "sequence": "4",
                "requiredParts": ["OC1", "OC2"],
                "operator": "OP1",
                "stationIdsList": [
                    "EDM"
                ],
                "processingTime": {
                    "distributionType": "Fixed",
                    "operationType": "",
                    "mea n": "2"
                }
            },
    
        '''
        currentStation=self.currentStation
        from Machine import Machine
        if issubclass(currentStation.__class__, Machine):
            for routeStep in self.route:
                stepResponsible=routeStep.get('operator',None)
                stepIDs=routeStep.get('stationIdsList',[])
                if currentStation.id in stepIDs:
                    responsibleID=stepResponsible
                    break
        else:
            responsibleID=self.remainingRoute[0].get('operator',None)
        from Globals import findObjectById
        responsible=findObjectById(responsibleID)
        return responsible
    #===========================================================================
    # method that finds a receiver for a candidate entity
    #===========================================================================
    def findCandidateReceiver(self):
        from Globals import G
        router=G.RouterList[0]
        # initiate the local list variable available receivers
        availableReceivers=[x for x in self.candidateReceivers\
                                        if not x in router.occupiedReceivers]
        # and pick the object that is waiting for the most time
        if availableReceivers:
            # find the receiver that waits the most
            availableReceiver=self.currentStation.selectReceiver(availableReceivers)
            router.occupiedReceivers.append(availableReceiver)
        # if there is no available receiver add the entity to the entitiesWithOccupiedReceivers list
        else:
            router.entitiesWithOccupiedReceivers.append(self)
            availableReceiver=None
        # if the sorting flag is not set then the sorting of each queue must prevail in case of operators conflict
        if not availableReceiver and bool(availableReceivers):
            availableReceiver=self.currentStation.selectReceiver(self.candidateReceivers)
            if not self in router.conflictingEntities:
                router.conflictingEntities.append(self)
        return availableReceiver
    
    #===========================================================================
    # print the route (the different stations the entity moved through)
    #===========================================================================
    def printRoute(self):
        if self.schedule:
            for record in self.schedule:
                # find the station of this step
                station=record[0]               # XXX should also hold a list with all the machines G.MachineList?
                # find the column corresponding to the machine
                # XXX each machine should have at least 3 columns, 2 for the jobs and one for operators
                if station in G.MachineList:
                    machine_index=G.MachineList.index(station)
                    # find the entrance time of this step
                    entrance_time=record[1]         # the time entity entered station
                    # find the row corresponding to the event and start placing the name of the Job in the cells
                    entrance_time_index=G.events_list.index(entrance_time)
                    # find the exit time of this step
                    if len(record)==3:
                        exit_time=record[2]             # the time the entity exited the station
                        # find the row corresponding to the event and place the name of the Job in the cell, this is the last cell of this processing
                        exit_time_index=G.events_list.index(exit_time)
                    elif len(record)!=3:
                        exit_time_index=len(G.events_list)
                    # for the rows with indices entrance_time_index to exit_time_index print the id of the Job in the column of the machine_index
                    for step in range(entrance_time_index,exit_time_index+1, 1):
                        col_to_write=station.station_col_inds[0]                                                                        # XXX
                        stepDone=False
                        # check if the cell is already written, if yes, then modify it adding the new jobs but not overwrite it
                        if not G.cells_to_write:
                            G.cells_to_write.append({'row':step+1,
                                          'col':col_to_write,
                                          'job':self.alias})
                            G.routeTraceSheet.write(step+1, col_to_write, self.alias)
                            continue
                        for cell in G.cells_to_write:
                            if cell['row']==step+1 and cell['col']==col_to_write:
                                next_col=station.station_col_inds[1]                                                                    # XXX
                                if not next_col in [x['col'] for x in G.cells_to_write if x['row']==step+1]:                            # XXX
                                    G.cells_to_write.append({'row':step+1,                                                              # XXX
                                                  'col':next_col,                                                                       # XXX
                                                  'job':self.alias})                                                                    # XXX
                                    G.routeTraceSheet.write(step+1, next_col, self.alias)                                               # XXX
                                    stepDone=True                                                                                       # XXX
                                    break                                                                                               # XXX
                                cell['job']=cell['job']+','+self.alias
                                G.routeTraceSheet.write(cell['row'], cell['col'], cell['job'])
                                stepDone=True
                                break
                        if not stepDone:
                            G.cells_to_write.append({'row':step+1,
                                          'col':col_to_write,
                                          'job':self.alias})
                            G.routeTraceSheet.write(step+1, col_to_write, self.alias)

