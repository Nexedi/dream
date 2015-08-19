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
Created on 6 June 2013

@author: George
'''
'''
event generator that controls the capacity station objects
'''

import simpy
from dream.simulation.EventGenerator import EventGenerator
from dream.simulation.applications.CapacityStations.CapacityEntity import CapacityEntity
from dream.simulation.Globals import G

class CapacityStationController(EventGenerator):
    def __init__(self, id=id, name=None, start=0, stop=float('inf'), interval=1,
                 duration=0, method=None, argumentDict={}, dueDateThreshold=float('inf'), 
                 prioritizeIfCanFinish=False,**kw):
        EventGenerator.__init__(self, id, name, start, stop, interval,
                 duration, method, argumentDict)
        # attribute used by optimization in calculateWhatIsToBeProcessed
        # only the projects that are within this threshold from the one with EDD in the same bufffer 
        # will be considered to move at first
        self.dueDateThreshold=float(dueDateThreshold)
        # attribute that shows if we prioritize entities that can finish work in this station in the next interval
        self.prioritizeIfCanFinish=bool(int(prioritizeIfCanFinish))
        # the total assemblySpace in the system
        if hasattr(G, 'extraPropertyDict'):
            self.assemblySpace=float(G.extraPropertyDict.get('assemblySpace', float('inf')))
        else:
            self.assemblySpace=float('inf')
        self.method=self.steps
        
    def initialize(self):
        EventGenerator.initialize(self)
        # sort the buffers so if they have shared resources the ones with highest priority will go in front
        self.sortBuffers()

    # the main loop that is carried in every interval  
    def steps(self):
        # loop through the stations
        for station in G.CapacityStationList:
            exit=station.next[0]  # take the exit
            exit.isLocked=False   # unlock the exit
            # loop though the entities
            entitiesToCheck=list(station.getActiveObjectQueue())
            for entity in entitiesToCheck:
                if not exit.isRequested.triggered:            # this is needed because the signal can be triggered also by the buffer
                    if exit.expectedSignals['isRequested']:
                        self.sendSignal(receiver=exit, signal=exit.isRequested)
                # wait until the entity is removed
                station.waitEntityRemoval=True
                
                station.expectedSignals['entityRemoved']=1
                
                yield station.entityRemoved
                                
                transmitter, eventTime=station.entityRemoved.value
                station.waitEntityRemoval=False
                exit.currentlyObtainedEntities.append(entity)
                station.entityRemoved=self.env.event()
                project=entity.capacityProject
                # output the finish time of the project. This will updated every time, so in the end it should be correct
                for entry in project.projectSchedule:
                    if entry['stationId']==station.id:
                        entry['exitTime']=self.env.now
            # lock the exit again
            exit.isLocked=True
        
        
        # create the entities in the following stations
        self.createInCapacityStationBuffers()

        # if the last exits led to an empty system then the simulation must be stopped
        # step returns and the generator never yields the stepsAreComplete signal
        if self.checkIfSystemEmpty():
            # if the system is empty set stop to now so that the generator stops and return
            self.stop=self.env.now
            return
        
        # if there is need to merge entities in a buffer
        self.mergeEntities()

        # Calculate from the last moves in Station->StationExits 
        # what should be created in StationBuffers and create it
        self.createInCapacityStationBuffers()
        # Calculate what should be given in every Station 
        # and set the flags to the entities of StationBuffers 
        self.calculateWhatIsToBeProcessed()
    
        # move the entities into the stations
        # loop through the stations
        for station in G.CapacityStationList:
            station.isLocked=False      # unlock the station
            buffer=station.previous[0]  # take the buffer
            buffer.sortEntities()       # sort the entities of the buffer so the ones to move go in front
            periodDict={}
            periodDict['period']=self.env.now
            # loop though the entities
            entitiesToCheck=list(buffer.getActiveObjectQueue())
            #capacityAvailable=station.intervalCapacity[int(self.env.now)]
            capacityAvailable=station.remainingIntervalCapacity[0]
            capacityAllocated=0
            for entity in entitiesToCheck:
                if not entity.shouldMove:   # when the first entity that should not move is reached break
                    break
                # ToDo, here we do not check if station.expectedSignals['isRequested']==1
                # consistency problem?
                self.sendSignal(receiver=station, signal=station.isRequested)
                buffer.waitEntityRemoval=True
                
                buffer.expectedSignals['entityRemoved']=1
                
                yield buffer.entityRemoved

                transmitter, eventTime=buffer.entityRemoved.value
                buffer.waitEntityRemoval=False
                buffer.entityRemoved=self.env.event()
                project=entity.capacityProject
                periodDict[project.id]=entity.requiredCapacity  # dict to be appended in the utilization list
                # append the move in the detailedWorkPlan of the station
                station.detailedWorkPlan.append({'time':self.env.now,
                                                'operation':station.id,
                                                'project':project.id,
                                                'allocation':entity.requiredCapacity})
                capacityAllocated+=entity.requiredCapacity
                if self.checkIfProjectJustStartsInStation(project, station):
                    project.projectSchedule.append({
                      "stationId": station.id,
                      "entranceTime": self.env.now})

            # lock the station
            station.isLocked=True
            # calculate the utilization
            if capacityAvailable:
                periodDict['utilization']=capacityAllocated/float(capacityAvailable)
            else:
                # TODO check how the utilization and mean utilization should be calculated if it is 0
                periodDict['utilization']=0
            # update the utilisationDict of the station
            station.utilisationDict.append(periodDict)             

        # for every station update the remaining interval capacity so that it is ready for next loop
        for station in G.CapacityStationList:
            station.remainingIntervalCapacity.pop(0)
            # if remainingIntervalCapacity is empty reset it (to obtain rolling capacity)
            if len(station.remainingIntervalCapacity)==0:
                station.remainingIntervalCapacity=list(station.intervalCapacity)
            # ig the next interval is in the exceptions update the capacity accordingly
            if str((self.env.now)+1.0) in station.intervalCapacityExceptions.keys():
                station.remainingIntervalCapacity[0]=station.intervalCapacityExceptions[str((self.env.now)+1)]
            
    # invoked after entities have exited one station to create 
    # the corresponding entities to the following buffer     
    def createInCapacityStationBuffers(self): 
        # loop through the exits   
        for exit in G.CapacityStationExitList:
            # if the exit received nothing currently there is nothing to do
            if exit.currentlyObtainedEntities==[]:
                continue
            buffer=exit.nextCapacityStationBuffer   # the next buffer
            # if it is the end of the system there is nothing to do
            if not buffer:
                exit.currentlyObtainedEntities=[]
                continue
            previousStation=exit.previous[0]  # the station the the entity just finished from
            previousBuffer=previousStation.previous[0]  # the buffer of the station
            nextStation=buffer.next[0]        # the next processing station
            # for every entity calculate the new entity to be created in the next station and create it  
            for entity in exit.currentlyObtainedEntities:
                project=entity.capacityProject
                # if the entity exits from an assembly station 
                # and not all project is finished there, then do not create anything in the next
                if previousBuffer.requireFullProject:
                    projectFinishedFromLast=True
                    for e in previousBuffer.getActiveObjectQueue():
                        if e.capacityProject==project:
                            projectFinishedFromLast=False
                            break
                    if not projectFinishedFromLast:
                        continue
                    
                entityCapacity=entity.requiredCapacity
                previousRequirement=float(project.capacityRequirementDict[previousStation.id])
                nextRequirement=float(project.capacityRequirementDict[nextStation.id])
                # if the previous station was assembly then in the next the full project arrives
                # so requires whatever the project requires
                if previousBuffer.requireFullProject:
                    nextStationCapacityRequirement=nextRequirement
                # else calculate proportionally
                else:
                    proportion=nextRequirement/previousRequirement
                    nextStationCapacityRequirement=proportion*entityCapacity
                entityToCreateName=entity.capacityProjectId+'_'+nextStation.objName+'_'+str(nextStationCapacityRequirement)
                entityToCreate=CapacityEntity(name=entityToCreateName, capacityProjectId=entity.capacityProjectId, 
                                              requiredCapacity=nextStationCapacityRequirement)
                entityToCreate.currentStation=buffer
                entityToCreate.initialize()
                import dream.simulation.Globals as Globals
                Globals.setWIP([entityToCreate])     #set the new components as wip                
            # reset the currently obtained entities list to empty
            exit.currentlyObtainedEntities=[]

    def calculateWhatIsToBeProcessed(self):
        import dream.simulation.Globals as Globals
       
        # calculate what space is available
        availableSpace=self.assemblySpace-self.calculateConsumedSpace()
        assert availableSpace>=0, 'negative available space'
        # list to hold the buffers that are already considered (due to shared resources)
        alreadyConsideredBuffers = []      
        
        # loop through the capacity station buffers
        for buffer in G.CapacityStationBufferList:
            # if the buffer was considered before (due to shared resources) continue
            if buffer in alreadyConsideredBuffers:
                continue
            alreadyConsideredBuffers.append(buffer)
            sharedBuffers = []
            station=buffer.next[0]  # get the station
            
            # find the stations that share resources with the one considered now
            if station.sharedResources:
                sharedStations = station.sharedResources.get('stationIds',[])
                for element in sharedStations:
                    s = Globals.findObjectById(element)
                    b = s.previous[0]
                    sharedBuffers.append(b)
            activeObjectQueue=buffer.getActiveObjectQueue()
            # the entities considered should be the entities in the current buffer plus the ones in buffers
            # of stations that share resources with the current one
            entitiesConsidered=list(activeObjectQueue)
            for b in sharedBuffers:
                entitiesConsidered+=b.getActiveObjectQueue() 
                alreadyConsideredBuffers.append(b)
            # sort entities according to due date of the project that each belongs to
            entitiesConsidered.sort(key=lambda x: x.capacityProject.dueDate)

            totalAvailableCapacity=station.remainingIntervalCapacity[0]     # get the available capacity of the station
                                                                            # for this interval

            # list to keep entities that have not been already allocated
            entitiesNotAllocated=list(entitiesConsidered)                                                                             
            allCapacityConsumed=False    
            # if there is no available capacity no need to do anything
            if totalAvailableCapacity==0:
                continue
            while not allCapacityConsumed: 
                # list to keep entities that are within a threshold from the EDD
                entitiesWithinThreshold=[]
                # list to keep entities that are outside a threshold from the EDD
                entitiesOutsideThreshold=[]   
                # get the EDD
                EDD=float('inf')
                for entity in entitiesNotAllocated:
                    entityBuffer=entity.currentStation
                    entityStation=entity.currentStation.next[0]
                    # consider only projects that can get into station
                    if self.checkIfProjectCanStartInStation(entity.capacityProject, entityStation) and\
                                (not self.checkIfProjectNeedsToBeAssembled(entity.capacityProject, entityBuffer))\
                                 and self.checkIfThereIsEnoughSpace(entity, entityBuffer, availableSpace):
                        if EDD>entity.capacityProject.dueDate:
                            EDD=entity.capacityProject.dueDate 
                # put the entities in the corresponding list according to their due date
                for entity in entitiesNotAllocated: 
                    if entity.capacityProject.dueDate-EDD<=self.dueDateThreshold:
                        entitiesWithinThreshold.append(entity)
                    else:
                        entitiesOutsideThreshold.append(entity)   

                # calculate the total capacity that is requested
                totalRequestedCapacity=0
                # do not to count projects that cannot move due to space limitations
                # so check according to considered capacity
                consideredSpace=float(availableSpace)
                for entity in entitiesWithinThreshold:
                    # get buffer where the entity is and the station it requests to get in
                    entityBuffer=entity.currentStation
                    entityStation=entity.currentStation.next[0]           
                                    
                    if self.checkIfProjectCanStartInStation(entity.capacityProject, entityStation) and\
                                (not self.checkIfProjectNeedsToBeAssembled(entity.capacityProject, entityBuffer))\
                                 and self.checkIfThereIsEnoughSpace(entity, entityBuffer, consideredSpace):         
                        if not self.checkIfProjectConsumesAssemblySpace(entity, entityBuffer):
                            consideredSpace-=entity.capacityProject.assemblySpaceRequirement
                        totalRequestedCapacity+=entity.requiredCapacity
                                    
                # if there is enough capacity for all the entities set them that they all should move
                if totalRequestedCapacity<=totalAvailableCapacity:
                    availableCapacity=float(totalAvailableCapacity)
                    for entity in entitiesWithinThreshold:
                        # get buffer where the entity is and the station it requests to get in
                        entityBuffer=entity.currentStation
                        entityStation=entity.currentStation.next[0]
                        if self.checkIfProjectCanStartInStation(entity.capacityProject, entityStation) and\
                                    (not self.checkIfProjectNeedsToBeAssembled(entity.capacityProject, entityBuffer))\
                                     and self.checkIfThereIsEnoughSpace(entity, entityBuffer, availableSpace) and\
                                     entity.requiredCapacity<=availableCapacity:
                            entity.shouldMove=True  
                            availableCapacity-=entity.requiredCapacity
                            assert availableCapacity>=0, 'negative available capacity'
                            # reduce the available space if there is need to
                            if entityBuffer.requireFullProject and \
                                    (not self.checkIfProjectConsumesAssemblySpace(entity, entityBuffer)):                                    
                                availableSpace-=entity.capacityProject.assemblySpaceRequirement  
                                assert availableSpace>=0, 'negative available space'
                      
                        # remove the entity from the none allocated ones
                        entitiesNotAllocated.remove(entity)
                    # check if all the capacity is consumed to update the flag and break the loop
                    if totalRequestedCapacity==totalAvailableCapacity:
                        # the capacity will be 0 since we consumed it all 
                        totalAvailableCapacity=0
                        allCapacityConsumed=True
                    # if we still have available capacity   
                    else:
                        # check in the entities outside the threshold if there is one or more that can be moved
                        haveMoreEntitiesToAllocate=False
                        for entity in entitiesOutsideThreshold:
                            # get buffer where the entity is and the station it requests to get in
                            entityBuffer=entity.currentStation
                            entityStation=entity.currentStation.next[0]
                            if self.checkIfProjectCanStartInStation(entity.capacityProject, entityStation) and\
                                        (not self.checkIfProjectNeedsToBeAssembled(entity.capacityProject, entityBuffer))\
                                         and self.checkIfThereIsEnoughSpace(entity, entityBuffer, availableSpace):
                                haveMoreEntitiesToAllocate=True
                                break
                            
                        # otherwise we have to calculate the capacity for next loop
                        # the remaining capacity will be decreased by the one that was originally requested
                        totalAvailableCapacity-=totalRequestedCapacity           

                        # if we have more entities break
                        if not haveMoreEntitiesToAllocate:
                            break       
                        if station.notProcessOutsideThreshold:
                            break                   
                        
                # else calculate the capacity for every entity and create the entities
                else:
                    allCapacityConsumed=True
                    entitiesToBeBroken=list(entitiesWithinThreshold)
                    leftCapacity=totalAvailableCapacity
                    leftSpace=availableSpace
                    # with the below we calculate the projects that can finish in the current period
                    # and sort the entities so the ones that can finish in current period (if any) go in front
                    for e in entitiesToBeBroken:
                        e.willFinishNow=False
                        if self.checkIfAProjectCanBeFinishedInStation(e,e.currentStation.next[0],leftCapacity) and\
                              (not self.checkIfProjectNeedsToBeAssembled(e.capacityProject, e.currentStation)) and\
                              self.checkIfProjectCanStartInStation(e.capacityProject, e.currentStation.next[0]) and\
                              self.checkIfThereIsEnoughSpace(entity, entityBuffer, leftSpace):
                            leftCapacity-=e.requiredCapacity
                            if e.currentStation.requireFullProject and \
                                    (not self.checkIfProjectConsumesAssemblySpace(e, e.currentStation)):                                    
                                leftSpace-=e.capacityProject.assemblySpaceRequirement  
                            e.willFinishNow=True
                    entitiesToBeBroken.sort(key=lambda \
                                            x: x.willFinishNow and self.prioritizeIfCanFinish, reverse=True)  
                      
                    # loop through the entities
                    for entity in entitiesToBeBroken:    
                        # get buffer where the entity is and the station it requests to get in
                        entityBuffer=entity.currentStation
                        entityStation=entity.currentStation.next[0]
                        # consider only entities that can move - not those waiting for assembly or earliest start
                        if self.checkIfProjectCanStartInStation(entity.capacityProject, entityStation) and\
                            (not self.checkIfProjectNeedsToBeAssembled(entity.capacityProject, entityBuffer)) and\
                            self.checkIfThereIsEnoughSpace(entity, entityBuffer, availableSpace):
                            # if we prioritize an entity that can completely finish then check for this
                            if self.checkIfAProjectCanBeFinishedInStation(entity, entityStation, totalAvailableCapacity)\
                                 and self.prioritizeIfCanFinish:
                                # set that the entity can move
                                entity.shouldMove=True
                                # reduce the available space if there is need to
                                if entityBuffer.requireFullProject and \
                                        (not self.checkIfProjectConsumesAssemblySpace(entity, entityBuffer)):                                    
                                    availableSpace-=entity.capacityProject.assemblySpaceRequirement  
                                    assert availableSpace>=0, 'negative available space'
                                # update the values
                                totalAvailableCapacity-=entity.requiredCapacity
                                totalRequestedCapacity-=entity.requiredCapacity

                            # else break the entity according to rule    
                            else:
                                if self.breakEntity(entity, entityBuffer, entityStation, 
                                                 totalAvailableCapacity, totalRequestedCapacity):
                                    # reduce the available space if there is need to
                                    if entityBuffer.requireFullProject and \
                                            (not self.checkIfProjectConsumesAssemblySpace(entity, entityBuffer)):
                                        availableSpace-=entity.capacityProject.assemblySpaceRequirement  
                                        assert availableSpace>=0, 'negative available space'
                           
    # breaks an entity in the part that should move and the one that should stay
    def breakEntity(self, entity, buffer, station, totalAvailableCapacity, totalRequestedCapacity):
        # calculate what is the capacity that should proceed and what that should remain
        capacityToMove=totalAvailableCapacity*(entity.requiredCapacity)/float(totalRequestedCapacity)
        capacityToStay=entity.requiredCapacity-capacityToMove
        # if capacityToMove is equal to 0 no need to break. Return false.
        if capacityToMove==0:
            return False
        else:
            # remove the capacity entity by the buffer so that the broken ones are created
            buffer.getActiveObjectQueue().remove(entity)
            entityToMoveName=entity.capacityProjectId+'_'+station.objName+'_'+str(capacityToMove)
            entityToMove=CapacityEntity(name=entityToMoveName, capacityProjectId=entity.capacityProjectId, requiredCapacity=capacityToMove)
            entityToMove.initialize()
            entityToMove.currentStation=buffer
            entityToMove.shouldMove=True
            entityToStayName=entity.capacityProjectId+'_'+station.objName+'_'+str(capacityToStay)
            entityToStay=CapacityEntity(name=entityToStayName, capacityProjectId=entity.capacityProjectId, requiredCapacity=capacityToStay)
            entityToStay.initialize()
            entityToStay.currentStation=buffer
            import dream.simulation.Globals as Globals
            Globals.setWIP([entityToMove,entityToStay])     #set the new components as wip    
            return True   

    # merges the capacity entities if they belong to the same project
    def mergeEntities(self):
        # loop through the capacity station buffers
        for buffer in G.CapacityStationBufferList:
            nextStation=buffer.next[0]
            projectList=[]
            # loop through the entities to see what projects lie in the buffer
            for entity in buffer.getActiveObjectQueue():
                if entity.capacityProject not in projectList:
                    projectList.append(entity.capacityProject)
            for project in projectList:
                entitiesToBeMerged=[]
                for entity in buffer.getActiveObjectQueue():
                    if entity.capacityProject==project:
                        entitiesToBeMerged.append(entity)
                totalCapacityRequirement=0
                # if the buffer acts as assembly there is no need to calculate the total capacity requirement, 
                # it will be the one that the project has as a total for this station
                if buffer.requireFullProject:
                    # find what has been already processed
                    alreadyProcessed=0     
                    for record in nextStation.detailedWorkPlan:
                        if record['project']==project.id:
                            alreadyProcessed+=float(record['allocation'])
                    totalCapacityRequirement=project.capacityRequirementDict[nextStation.id]-alreadyProcessed
                # else calculate the total capacity requirement by adding the one each entity requires
                else:
                    for entity in entitiesToBeMerged:
                        totalCapacityRequirement+=entity.requiredCapacity
                # erase the Entities to create the merged one
                for entity in entitiesToBeMerged:
                    buffer.getActiveObjectQueue().remove(entity)
                # create the merged entity
                entityToCreateName=entity.capacityProjectId+'_'+nextStation.objName+'_'+str(totalCapacityRequirement)
                entityToCreate=CapacityEntity(name=entityToCreateName, capacityProjectId=project.id, 
                                              requiredCapacity=totalCapacityRequirement)
                entityToCreate.currentStation=buffer
                entityToCreate.initialize()
                import dream.simulation.Globals as Globals
                Globals.setWIP([entityToCreate])     #set the new components as wip                                            
    
    # checks if the system is empty so that the simulation can be stopped
    def checkIfSystemEmpty(self):
        for object in G.CapacityStationList+G.CapacityStationBufferList+G.CapacityStationExitList:
            if len(object.getActiveObjectQueue()):
                return False
        return True
    
    # checks if a project is just starting in station
    def checkIfProjectJustStartsInStation(self, project, station):
        for entry in project.projectSchedule:
            if entry['stationId']==station.id:
                return False
        return True
    
    # checks if a project cannot move because it needs to be assembled first
    def checkIfProjectNeedsToBeAssembled(self, project, buffer):
        # if we are not in assembly return false
        if not buffer.requireFullProject:
            return False
        # if project is already assembled return false
        if self.checkIfProjectAssembledInBuffer(project, buffer):
            return False
        # at any other case return true
        return True
        
    # checks if the given project is all in the buffer
    def checkIfProjectAssembledInBuffer(self, project, buffer):
        for object in G.CapacityStationList+G.CapacityStationBufferList+G.CapacityStationExitList:
            # skip the given buffer
            if object is buffer:
                continue
            # skip not required operations
            if object.id in buffer.notRequiredOperations:
                continue
            # if there is one entity from the same project which we check somewhere else return false
            for entity in object.getActiveObjectQueue():
                if entity.capacityProject==project:
                    return False
        # if nothing was found return true
        return True 

    # checks if the given project can start in the station or not because there is an earliest start defined           
    def checkIfProjectCanStartInStation(self, project, station):
        earliestStartInStation=project.earliestStartDict.get(station.id, 0)
        if self.env.now<earliestStartInStation:
            return False
        return True
    
    # checks if the whole project can be finished in one station in the next time period
    def checkIfAProjectCanBeFinishedInStation(self, entity, station, availableCapacity):
        required=entity.requiredCapacity
        alreadyWorked=entity.capacityProject.alreadyWorkedDict[station.id]
        total=entity.capacityProject.capacityRequirementDict[station.id]
        # return true if all the work can be finished and if there is available capacity
        if total-(alreadyWorked+required)<0.001 and availableCapacity>=required:  # a small value to avoid mistakes due to rounding
            return True
        return False
    
    # returns true if there is enough space for the entity to move
    def checkIfThereIsEnoughSpace(self, entity, buffer, availableSpace):
        if buffer.requireFullProject:
            # if the project already consumes assembly space then there is enough space for it
            if self.checkIfProjectConsumesAssemblySpace(entity, buffer):
                return True
            # else check if there is enough space            
            return entity.capacityProject.assemblySpaceRequirement<=availableSpace
        # if the station is not assembly then return true
        return True
            
    # sorts the buffers so if they have shared resources the ones with highest priority will go in front
    def sortBuffers(self):
        for buffer in G.CapacityStationBufferList:
            station=buffer.next[0]
            buffer.sharedPriority=station.sharedResources.get('priority', -float('inf'))
        G.CapacityStationBufferList.sort(key=lambda x: x.sharedPriority, reverse=True)      
    
    # calculates the space that is already consumed before the allocation for current period    
    def calculateConsumedSpace(self):
        consumedSpace=0
        # loop in the buffers and find projects that have started assembly without having been finished
        # add what they consume
        for buffer in G.CapacityStationBufferList:
            station=buffer.next[0]
            for entity in buffer.getActiveObjectQueue():
                if self.checkIfProjectConsumesAssemblySpace(entity, buffer):
                    consumedSpace+=entity.capacityProject.assemblySpaceRequirement
        return consumedSpace
    
    # checks if a project already consumes assembly space because assembly work started in a previous period 
    # and was not completed
    def checkIfProjectConsumesAssemblySpace(self, entity, buffer):
        if buffer.requireFullProject:
            station=buffer.next[0]
            project=entity.capacityProject
            projectRequirement=project.capacityRequirementDict[station.id]
            if projectRequirement>entity.requiredCapacity:
                return True
        return False
            
            
        
        