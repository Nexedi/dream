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

from SimPy.Simulation import now, Process, Resource, infinity, hold, SimEvent, activate, waitevent
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject
from Globals import G
import Globals


#============================================================================
#                 the EntityGenerator object
#============================================================================
class EntityGenerator(Process):
    #===========================================================================
    # the __init__ method of the EntityGenerator
    #===========================================================================
    def __init__(self, victim=None):
        Process.__init__(self)
        self.type="EntityGenerator"                       #String that shows the type of object
        self.victim=victim
    
    #===========================================================================
    # initialize method of the EntityGenerator
    #===========================================================================
    def initialize(self):
        pass
        #Process.initialize(self)                             
        
    #===========================================================================
    # the generator of the EntitiesGenerator
    #===========================================================================
    def run(self):     
#         print 'entity generator starts'   
        while 1:
            entity=self.victim.createEntity()                       # create the Entity object and assign its name
            entity.creationTime=now()                               # assign the current simulation time as the Entity's creation time 
            entity.startTime=now()                                  # assign the current simulation time as the Entity's start time 
            entity.currentStation=self.victim                            # update the current station of the Entity
            G.EntityList.append(entity)
            self.victim.outputTrace(entity.name, "generated")       # output the trace
            self.victim.getActiveObjectQueue().append(entity)            # append the entity to the resource 
            self.victim.numberOfArrivals+=1                              # we have one new arrival
            G.numberOfEntities+=1
            self.victim.entityCreated.signal(entity)
            yield hold,self,self.victim.calculateInterarrivalTime() # wait until the next arrival

#============================================================================
#                 The Source object is a Process
#============================================================================
class Source(CoreObject):
    #===========================================================================
    # the __init__method of the Source class
    #===========================================================================
    def __init__(self, id, name, interarrivalTime=None, entity='Dream.Part'):
        # Default values
        if not interarrivalTime:
          interarrivalTime = {'distributionType': 'Fixed', 'mean': 1}
        if interarrivalTime['distributionType'] == 'Normal' and\
              interarrivalTime.get('max', None) is None:
          interarrivalTime['max'] = interarrivalTime['mean'] + 5 * interarrivalTime['stdev']

        CoreObject.__init__(self, id, name)
        # properties used for statistics
        self.totalInterArrivalTime = 0                  # the total interarrival time 
        self.numberOfArrivals = 0                       # the number of entities that were created

        self.type="Source"                              #String that shows the type of object
        
        self.rng = RandomNumberGenerator(self, **interarrivalTime)

        self.item=Globals.getClassFromName(entity)      #the type of object that the Source will generate
        
        self.entityGenerator=EntityGenerator(victim=self)     # the EntityGenerator of the Source
        
        self.entityCreated=SimEvent('an entity is created')
    
    #===========================================================================
    # The initialize method of the Source class
    #===========================================================================
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
         
        # initialize the internal Queue (type Resource) of the Source 
        self.Res=Resource(capacity=infinity)
        self.Res.activeQ=[]                                 
        self.Res.waitQ=[]   
        
        self.entityGenerator.initialize()                                
        activate(self.entityGenerator,self.entityGenerator.run())
        
    
    #===========================================================================
    # the generator of the Source class 
    #===========================================================================
    def run(self):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        while 1:
            # wait for any event (entity creation or request for disposal of entity)
            yield waitevent, self, [self.entityCreated, self.canDispose]
            # if an entity is created try to signal the receiver and continue
            if self.entityCreated.signalparam:
                self.appendEntity(self.entityCreated.signalparam)
                self.entityCreated.signalparam=None
                if self.signalReceiver():
                    continue
            # otherwise, if the receiver requests availability then try to signal him if there is anything to dispose of
            if self.canDispose.signalparam:
                self.canDispose.signalparam=None
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
        # at the newly created entity to the pendingEntities
        G.pendingEntities.append(activeEntity)
        # TODO: if the successor of the object is a machine that is operated with operationType 'Load'
        #     then the flag hot of the activeEntity must be set to True 
        #     to signalize that the entity has reached its final destination before the next Machine
        # if the entity is not of type Job
        if activeEntity.family=='Entity':
            successorsAreMachines=True
            # for all the objects in the next list
            for object in self.next:
            # if the object is not in the MachineList
            # TODO: We must consider also the case that entities can be blocked before they can reach 
            #     the heating point. In such a case they must be removed from the G.pendingEntities list
            #     and added again after they are unblocked
                if not object in G.MachineList:
                    successorsAreMachines=False
                    break
            # the hot flag should not be raised
            if successorsAreMachines:
                activeEntity.hot = True

    #============================================================================
    #            sets the routing out element for the Source
    #============================================================================
    def defineRouting(self, successorList=[]):
        self.next=successorList                                   # only successors allowed for the source
    #============================================================================        
    #                          creates an Entity
    #============================================================================
    def createEntity(self):
        self.printTrace(self.id, 'created an entity')
        return self.item(id = self.item.type+str(G.numberOfEntities), name = self.item.type+str(self.numberOfArrivals)) #return the newly created Entity
    #============================================================================
    #                    calculates the processing time
    #============================================================================
    def calculateInterarrivalTime(self):
        return self.rng.generateNumber()    #this is if we have a default interarrival  time for all the entities

