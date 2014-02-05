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
        self.internal = False       # informs if the entity is being processed internally
        self.isCritical=isCritical          # flag to inform weather the entity is critical -> preemption
        self.manager=None
        
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