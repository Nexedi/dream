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

# from SimPy.Simulation import now, Process, Resource, infinity, hold, SimEvent, activate, waitevent
import simpy
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject
from Globals import G
import Globals


#============================================================================
#                 the EntityGenerator object
#============================================================================
class EntityGenerator(object):
    #===========================================================================
    # the __init__ method of the EntityGenerator
    #===========================================================================
    def __init__(self, victim=None):
        self.env=G.env
        self.type="EntityGenerator"                       #String that shows the type of object
        self.victim=victim
            
    #===========================================================================
    # the generator of the EntitiesGenerator
    #===========================================================================
    def run(self): 
        while 1:
            # if the Source is empty create the Entity
            if len(self.victim.getActiveObjectQueue())==0:
                entity=self.victim.createEntity()                       # create the Entity object and assign its name
                entity.creationTime=self.env.now                               # assign the current simulation time as the Entity's creation time 
                entity.startTime=self.env.now                                  # assign the current simulation time as the Entity's start time 
                entity.currentStation=self.victim                            # update the current station of the Entity
                G.EntityList.append(entity)
                self.victim.outputTrace(entity.name, "generated")       # output the trace
                self.victim.getActiveObjectQueue().append(entity)            # append the entity to the resource 
                self.victim.numberOfArrivals+=1                              # we have one new arrival
                G.numberOfEntities+=1
                self.victim.appendEntity(entity)
                if self.victim.expectedSignals['entityCreated']:
                    succeedTupple=(entity,self.env.now)
                    self.victim.entityCreated.succeed(succeedTupple)
                    self.victim.expectedSignals['entityCreated']=0
            # else put it on the time list for scheduled Entities
            else:
                entityCounter=G.numberOfEntities+len(self.victim.scheduledEntities) # this is used just ot output the trace correctly
                self.victim.scheduledEntities.append(self.env.now)
                self.victim.outputTrace(self.victim.item.type+str(entityCounter), "generated")       # output the trace
            yield self.env.timeout(self.victim.calculateInterArrivalTime()) # wait until the next arrival

#============================================================================
#                 The Source object is a Process
#============================================================================
class Source(CoreObject):
    #===========================================================================
    # the __init__method of the Source class
    #===========================================================================
    def __init__(self, id, name, interArrivalTime=None, entity='Dream.Part',**kw):
        # Default values
        if not interArrivalTime:
          interArrivalTime = {'Fixed': {'mean': 1}}
        if 'Normal' in interArrivalTime.keys() and\
              interArrivalTime['Normal'].get('max', None) is None:
          interArrivalTime['Normal']['max'] = interArrivalTime['Normal']['mean'] + 5 * interArrivalTime['Normal']['stdev']

        CoreObject.__init__(self, id, name)
        # properties used for statistics
        self.totalinterArrivalTime = 0                  # the total interarrival time 
        self.numberOfArrivals = 0                       # the number of entities that were created

        self.type="Source"                              #String that shows the type of object
        self.rng = RandomNumberGenerator(self, interArrivalTime)

        self.item=Globals.getClassFromName(entity)      #the type of object that the Source will generate
               
        self.scheduledEntities=[]       # list of creations that are scheduled. pattern is [timeOfCreation, EntityCounter]     
        from Globals import G
        G.SourceList.append(self)  
    
    #===========================================================================
    # The initialize method of the Source class
    #===========================================================================
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        
        # initialize the internal Queue (type Resource) of the Source 
        # self.Res=Resource(capacity=infinity)
        self.Res=simpy.Resource(self.env, capacity=float('inf'))
        self.Res.users=[]                                 
        self.entityGenerator=EntityGenerator(victim=self)     # the EntityGenerator of the Source

        self.numberOfArrivals = 0 
#         self.entityGenerator.initialize()
        # activate(self.entityGenerator,self.entityGenerator.run())
        self.env.process(self.entityGenerator.run())
        # self.entityCreated=SimEvent('an entity is created')
        self.entityCreated=self.env.event()
        # event used by router
        # self.loadOperatorAvailable=SimEvent('loadOperatorAvailable')
        self.loadOperatorAvailable=self.env.event()
        self.scheduledEntities=[]       # list of creations that are scheduled
        
        self.expectedSignals['entityCreated']=1
        self.expectedSignals['loadOperatorAvailable']=1
        self.expectedSignals['canDispose']=1
    
    #===========================================================================
    # the generator of the Source class 
    #===========================================================================
    def run(self):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        while 1:
            # wait for any event (entity creation or request for disposal of entity)
            self.expectedSignals['canDispose']=1
            self.expectedSignals['entityCreated']=1
            self.expectedSignals['loadOperatorAvailable']=1
            receivedEvent=yield self.env.any_of([self.entityCreated, self.canDispose, self.loadOperatorAvailable])
            self.printTrace(self.id, received='')
            # if an entity is created try to signal the receiver and continue
            if self.entityCreated in receivedEvent:
                transmitter, eventTime=self.entityCreated.value
                self.entityCreated=self.env.event()
            # otherwise, if the receiver requests availability then try to signal him if there is anything to dispose of
            if self.canDispose in receivedEvent:
                transmitter, eventTime=self.canDispose.value
                self.canDispose=self.env.event()
            if self.loadOperatorAvailable in receivedEvent:
                transmitter, eventTime=self.loadOperatorAvailable.value
                self.loadOperatorAvailable=self.env.event()
            if self.haveToDispose():
                if self.signalReceiver():
                    continue
        
    #===========================================================================
    # add newly created entity to pendingEntities
    #===========================================================================
    def appendEntity(self, entity):
        from Globals import G
        assert entity, 'cannot append None entity'
        activeEntity=entity
        if G.RouterList:
            # at the newly created entity to the pendingEntities
            G.pendingEntities.append(activeEntity)

    #============================================================================
    #            sets the routing out element for the Source
    #============================================================================
    def defineRouting(self, successorList=[]):
        self.next=successorList                                   # only successors allowed for the source
    #============================================================================        
    #                          creates an Entity
    #============================================================================
    def createEntity(self):
        self.printTrace(self.id, create='')
        return self.item(id = self.item.type+str(G.numberOfEntities), name = self.item.type+str(self.numberOfArrivals)) #return the newly created Entity
    #============================================================================
    #                    calculates the processing time
    #============================================================================
    def calculateInterArrivalTime(self):
        return self.rng.generateNumber()    #this is if we have a default interarrival  time for all the entities
    
    # =======================================================================
    # removes an entity from the Source
    # =======================================================================
    def removeEntity(self, entity=None):
        if len(self.getActiveObjectQueue())==1 and len(self.scheduledEntities):
            newEntity=self.createEntity()                       # create the Entity object and assign its name
            newEntity.creationTime=self.scheduledEntities.pop(0)                      # assign the current simulation time as the Entity's creation time 
            newEntity.startTime=newEntity.creationTime                                # assign the current simulation time as the Entity's start time
            #print self.env.now, 'getting from the list. StartTime=',newEntity.startTime
            newEntity.currentStation=self                            # update the current station of the Entity
            G.EntityList.append(newEntity)
            self.getActiveObjectQueue().append(newEntity)            # append the entity to the resource 
            self.numberOfArrivals+=1                              # we have one new arrival
            G.numberOfEntities+=1
            self.appendEntity(newEntity)  
        activeEntity=CoreObject.removeEntity(self, entity)          # run the default method  
        if len(self.getActiveObjectQueue())==1:
            if self.expectedSignals['entityCreated']:
                self.sendSignal(receiver=self, signal=self.entityCreated)
        return activeEntity
