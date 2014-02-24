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
Created on 8 Nov 2012

@author: George
'''

'''
models the source object that generates the entities
'''

from SimPy.Simulation import now, Process, Resource, infinity, hold
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject
from Globals import G
import Globals
#============================================================================
#                 The Source object is a Process
#============================================================================
class Source(CoreObject): 
    def __init__(self, id, name, interarrivalTime=None, entity='Dream.Part', **kw):
        # Default values
        if not interarrivalTime:
          interarrivalTime = {'distributionType': 'Fixed', 'mean': 1}

        CoreObject.__init__(self, id, name)
        # properties used for statistics
        self.totalInterArrivalTime = 0                    # the total interarrival time 
        self.numberOfArrivals = 0                         # the number of entities that were created
#         # list containing objects that follow in the routing 
#         self.next=[]                                    # list with the next objects in the flow
#         self.nextIds=[]                                 # list with the ids of the next objects in the flow
#         self.previousIds=[]                             # list with the ids of the previous objects in the flow. 
#                                                         # For the source it is always empty!
        self.type="Source"                              #String that shows the type of object
        
        self.rng = RandomNumberGenerator(self, **interarrivalTime)

        self.item=Globals.getClassFromName(entity)       #the type of object that the Source will generate
        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
         
        # initialize the internal Queue (type Resource) of the Source 
        self.Res=Resource(capacity=infinity)
        self.Res.activeQ=[]                                 
        self.Res.waitQ=[]                                   
        
    def run(self):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        while 1:
            entity=self.createEntity()                            # create the Entity object and assign its name 
            entity.creationTime=now()                             # assign the current simulation time as the Entity's creation time 
            entity.startTime=now()                                # assign the current simulation time as the Entity's start time 
            entity.currentStation=self                            # update the current station of the Entity
            G.EntityList.append(entity)
            self.outputTrace(entity.name, "generated")          # output the trace
            activeObjectQueue.append(entity)                      # append the entity to the resource 
            self.numberOfArrivals+=1                              # we have one new arrival
            G.numberOfEntities+=1       
            yield hold,self,self.calculateInterarrivalTime()      # wait until the next arrival
    #============================================================================
    #            sets the routing out element for the Source
    #============================================================================
    def defineRouting(self, successorList=[]):
        self.next=successorList                                   # only successors allowed for the source
    #============================================================================        
    #                          creates an Entity
    #============================================================================
    def createEntity(self):
        return self.item(id = self.item.type+str(G.numberOfEntities), name = self.item.type+str(self.numberOfArrivals)) #return the newly created Entity
    #============================================================================
    #                    calculates the processing time
    #============================================================================
    def calculateInterarrivalTime(self):
        return self.rng.generateNumber()    #this is if we have a default interarrival  time for all the entities

