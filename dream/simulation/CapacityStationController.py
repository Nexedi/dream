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
from EventGenerator import EventGenerator
from CapacityEntity import CapacityEntity
from Globals import G

class CapacityStationController(EventGenerator):
    def __init__(self, id=id, name=None, start=None, stop=None, interval=None,
                 duration=None, method=None, argumentDict=None):
        EventGenerator.__init__(self, id, name, start, stop, interval,
                 duration, method, argumentDict)

    def initialize(self):
        EventGenerator.initialize(self)
        self.stepsAreComplete=self.env.event()

    def run(self):
        yield self.env.timeout(self.start)              #wait until the start time
        #loop until the end of the simulation
        while 1:
            #if the stop time is exceeded then break the loop
            if self.stop:
                if self.env.now>self.stop:
                    break
            self.env.process(self.steps())
            yield self.stepsAreComplete
            self.stepsAreComplete=self.env.event()
            yield self.env.timeout(self.interval)       #wait for the predetermined interval
  
    def steps(self):

        # loop through the stations
        for station in G.CapacityStationList:
            exit=station.next[0]  # take the exit
            exit.isLocked=False   # unlock the exit
            # loop though the entities
            entitiesToCheck=list(station.getActiveObjectQueue())
            for entity in entitiesToCheck:
                if not exit.isRequested.triggered:            # this is needed because the signal can be triggered also by the buffer
                    exit.isRequested.succeed(station)         # send is requested to station
                # wait until the entity is removed
                yield station.entityRemoved
                exit.currentlyObtainedEntities.append(entity)
                station.entityRemoved=self.env.event()
            # lock the exit again
            exit.isLocked=True
        
        # create the entities in the following stations
        self.createInCapacityStationBuffers()
        # if there is need to merge entities in a buffer
        self.mergeEntities()

        # Calculate from the last moves in Station->StationExits 
        # what should be created in StationBuffers and create it
        self.createInCapacityStationBuffers()
        # Calculate what should be given in every Station 
        # and set the flags to the entities of StationBuffers 
        self.calculateWhatIsToBeProcessed()
    
        # loop through the stations
        for station in G.CapacityStationList:
            station.isLocked=False      # unlock the station
            buffer=station.previous[0]  # take the buffer
            buffer.sortEntities()       # sort the entities of the buffer so the ones to move go in front
            # loop though the entities
            entitiesToCheck=list(buffer.getActiveObjectQueue())
            for entity in entitiesToCheck:
                if not entity.shouldMove:   # when the first entity that should not move is reached break
                    break
                station.isRequested.succeed(buffer)         # send is requested to station
                # wait until the entity is removed
                yield buffer.entityRemoved
                buffer.entityRemoved=self.env.event()
            # lock the station
            station.isLocked=True             

        # for every station update the remaining interval capacity so that it is ready for next loop
        for station in G.CapacityStationList:
            station.remainingIntervalCapacity.pop(0)                       
        self.stepsAreComplete.succeed()    
    
    def checkIfStationsEmpty(self):
        for station in G.CapacityStationList:
            if len(station.getActiveObjectQueue()):
                return False
        return True        

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
            nextStation=buffer.next[0]        # the next processing station
            # for every entity calculate the new entity to be created in the next station and create it  
            for entity in exit.currentlyObtainedEntities:
                project=entity.capacityProject
                entityCapacity=entity.requiredCapacity
                previousRequirement=float(project.capacityRequirementDict[previousStation.id])
                nextRequirement=float(project.capacityRequirementDict[nextStation.id])
                proportion=nextRequirement/previousRequirement
                nextStationCapacityRequirement=proportion*entityCapacity
                entityToCreateName=entity.capacityProjectId+'_'+nextStation.objName+'_'+str(nextStationCapacityRequirement)
                entityToCreate=CapacityEntity(name=entityToCreateName, capacityProjectId=entity.capacityProjectId, 
                                              requiredCapacity=nextStationCapacityRequirement)
                entityToCreate.currentStation=buffer
                entityToCreate.initialize()
                import Globals
                Globals.setWIP([entityToCreate])     #set the new components as wip                
            # reset the currently obtained entities list to empty
            exit.currentlyObtainedEntities=[]

    def calculateWhatIsToBeProcessed(self):
        # loop through the capacity station buffers
        for buffer in G.CapacityStationBufferList:
            station=buffer.next[0]  # get the station
            totalAvailableCapacity=station.remainingIntervalCapacity[0]     # get the available capacity of the station
                                                                            # for this interval            
            # if there is no capacity continue with the next buffer
            if totalAvailableCapacity<=0:
                continue
            # calculate the total capacity that is requested
            totalRequestedCapacity=0    
            for entity in buffer.getActiveObjectQueue():
                totalRequestedCapacity+=entity.requiredCapacity
            # if there is enough capacity for all the entities set them that they all should move
            if totalRequestedCapacity<=totalAvailableCapacity:
                for entity in buffer.getActiveObjectQueue():
                    entity.shouldMove=True              
            # else calculate the capacity for every entity and create the entities
            else:
                entitiesInBuffer=list(buffer.getActiveObjectQueue())
                # loop through the entities
                for entity in entitiesInBuffer:
                    # calculate what is the capacity that should proceed and what that should remain
                    capacityToMove=totalAvailableCapacity*(entity.requiredCapacity)/float(totalRequestedCapacity)
                    capacityToStay=entity.requiredCapacity-capacityToMove
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
                    import Globals
                    Globals.setWIP([entityToMove,entityToStay])     #set the new components as wip

    # merges the capacity entities if they belong to the same project
    def mergeEntities(self):
        # loop through the capacity station buffers
        for buffer in G.CapacityStationBufferList:
            nextStation=buffer.next[0]
            projectList=[]
            # loop through the entities
            for entity in buffer.getActiveObjectQueue():
                if entity.capacityProject not in projectList:
                    projectList.append(entity.capacityProject)
            for project in projectList:
                entitiesToBeMerged=[]
                for entity in buffer.getActiveObjectQueue():
                    if entity.capacityProject==project:
                        entitiesToBeMerged.append(entity)
                if len(entitiesToBeMerged)<2:
                    continue
                totalCapacityRequirement=0
                for entity in entitiesToBeMerged:
                    totalCapacityRequirement+=entity.requiredCapacity
                    buffer.getActiveObjectQueue().remove(entity)
                entityToCreateName=entity.capacityProjectId+'_'+nextStation.objName+'_'+str(totalCapacityRequirement)
                entityToCreate=CapacityEntity(name=entityToCreateName, capacityProjectId=project.id, 
                                              requiredCapacity=totalCapacityRequirement)
                entityToCreate.currentStation=buffer
                entityToCreate.initialize()
                import Globals
                Globals.setWIP([entityToCreate])     #set the new components as wip                                   
                    
                    
    def checkIfBufferFinished(self, buffer):
        if buffer.getActiveObjectQueue():
            return False
        return True               
     