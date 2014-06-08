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
        print 1
        # unlock all the capacity station exits
        for exit in G.CapacityStationExitList:
            exit.isLocked=False
        # Send canDispose to all the Stations  
        print 2
        for station in G.CapacityStationList:
            if len(station.getActiveObjectQueue())>0:
                station.canDispose.succeed()
        # give control until all the Stations become empty
        print 3
        while not self.checkIfStationsEmpty():
            yield self.env.timeout(0)
        print 4
        # Lock all StationExits canAccept
        for exit in G.CapacityStationExitList:
            exit.isLocked=True
        # Calculate from the last moves in Station->StationExits 
        # what should be created in StationBuffers and create it
        print 5
        self.createInCapacityStationBuffers()
        # Calculate what should be given in every Station 
        # and set the flags to the entities of StationBuffers 
        print 6
        self.calculateWhatIsToBeProcessed()
        # Unlock all Stations canAccept
        print 7
        for station in G.CapacityStationList:
            station.isLocked=False
    
        print 8, 9
        # loop through the stations
        for station in G.CapacityStationList:
            buffer=station.previous[0]  # take the buffer
            buffer.sortEntities()       # sort the entities of the buffer so the ones to move go in front
            # loop though the entities
            entitiesToCheck=list(buffer.getActiveObjectQueue())
            for entity in entitiesToCheck:
                print entity.name, entity.shouldMove             
                if not entity.shouldMove:   # when the first entity that should not move is reached break
                    break
                station.isRequested.succeed(buffer)         # send is requested to station
                # wait until the entity is removed
                yield buffer.entityRemoved
                buffer.entityRemoved=self.env.event()
                
                
                
    
        print 10
        # for every station update the remaining interval capacity so that it is ready for next loop
        for station in G.CapacityStationList:
            station.remainingIntervalCapacity.pop(0)                       
        self.stepsAreComplete.succeed()    
    
    def checkIfStationsEmpty(self):
        for station in G.CapacityStationList:
            if len(station.getActiveObjectQueue()):
                return False
        return True        
     
    def createInCapacityStationBuffers(self):    
        pass

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
                    buffer.sortEntities()
                print '-'
                for entity in buffer.getActiveObjectQueue():
                    print entity.name, entity.shouldMove
                print '-' 
                    
    def checkIfBufferFinished(self, buffer):
        if buffer.getActiveObjectQueue():
            return False
        return True               
     