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
Created on 18 Aug 2013

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All the Entities should inherit from it
'''

from SimPy.Simulation import now

# ===========================================================================
# The entity object 
# ===========================================================================
class Entity(object):
    type="Entity"

    def __init__(self, id=None, name=None, priority=0, dueDate=None, orderDate=None, isCritical=False):
        self.name=name
        #         information on the object holding the entity
        #         initialized as None and updated every time an entity enters a new object
        #         information on the lifespan of the entity  
        self.creationTime=0
        self.startTime=0            #holds the startTime for the lifespan
        #         dimension data of the entity
        self.width=1.0
        self.height=1.0
        self.length=1.0
        #         information concerning the sorting of the entities inside (for example) queues
        self.priority=priority
        self.dueDate=dueDate
        self.orderDate=orderDate
        #         a list that holds information about the schedule 
        #         of the entity (when it enters and exits every station)
        self.schedule=[]
        self.currentStation=None
        #         values to be used in the internal processing of compoundObjects
        self.internal = False               # informs if the entity is being processed internally
        self.isCritical=isCritical          # flag to inform weather the entity is critical -> preemption
        self.manager=None                   # default value
        self.numberOfUnits=1                # default value
        #        flag that signalizes that an entity is ready to enter a machine
        #        gets cold by the time it has finished its processing
        self.hot=False
        # variable used to differentiate entities with and entities without routes
        self.family='Entity'
        
        # variables to be used by OperatorRouter
        self.proceed=False               # boolean that is used to check weather the entity can proceed to the candidateReceiver
        self.candidateReceivers=[]          # list of candidateReceivers of the entity (those stations that can receive the entity
        self.candidateReceiver=None         # the station that is finaly chosen to receive the entity
        
        # variables used to avoid signalling the same object twice before it receives an entity
        self.receiver=None
        self.timeOfAssignement=0
        
    #===========================================================================
    # check if the entity can proceed to an operated machine, for use by Router
    #===========================================================================
    def canProceed(self):
        activeObject=self.currentStation
        return activeObject.canDeliver(self)
    
    #===========================================================================
    # method that finds a receiver for a candidate entity
    #===========================================================================
    def findCandidateReceiver(self):
        from Globals import G
        router=G.Router
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
        if not router.sorting and not availableReceiver and bool(availableReceivers):
            availableReceiver=self.currentStation.selectReceiver(self.candidateReceivers)
            if not self in router.conflictingEntities:
                router.conflictingEntities.append(self)
        return availableReceiver
            
    #===========================================================================
    # assign the entity to a station
    #===========================================================================
    def assignTo(self, object=None):
        self.receiver=object
        self.timeOfAssignement=now()
        
    #===========================================================================
    # unassign the entity from the object it is currently assigned to
    #===========================================================================
    def unassign(self):
        self.receiver=None
        self.timeOfAssignement=0
        
    #===========================================================================
    # returns the object the entity is currently assigned to
    #===========================================================================
    def isAssignedTo(self):
        return self.receiver
    # =======================================================================
    # outputs results to JSON File 
    # =======================================================================
    def outputResultsJSON(self):
        pass
    
    # =======================================================================
    # initializes all the Entity for a new simulation replication 
    # =======================================================================
    def initialize(self):
        pass