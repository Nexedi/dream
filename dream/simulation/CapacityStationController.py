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
            exit.isLocked==False
        # Send canDispose to all the Stations  
        print 2
        for station in G.CapacityStationList:
            print station.id
            station.canDispose.succeed()
        # give control until all the Stations become empty
        print 3
        while not self.checkIfStationsEmpty():
            yield self.env.timeout(0)
        print 4
        # Lock all StationExits canAccept
        for exit in G.CapacityStationExitList:
            exit.isLocked==True
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
        # Send canDispose to all the StationBuffers  
        print 8
        for buffer in G.CapacityStationBufferList:
            buffer.canDispose.succeed()        
        # give control until all StationBuffers hold only Entities that are not to be given
        print 9
        while not self.checkIfBuffersFinished():
            yield self.env.timeout(0)   
        self.stepsAreComplete.succeed()    
    
    def checkIfStationsEmpty(self):
        for station in G.CapacityStationList:
            if len(station.getActiveObjectQueue()):
                return False
        return True        
     
    def createInCapacityStationBuffers(self):    
        pass

    def calculateWhatIsToBeProcessed(self):
        pass
    
    def checkIfBuffersFinished(self):
        for buffer in G.CapacityStationBufferList:
            for entity in buffer.getActiveObjectQueue():
                if entity.shouldMove:
                    return False
        return True               
     