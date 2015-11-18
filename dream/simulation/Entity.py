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

# from SimPy.Simulation import now
import simpy
from ManPyObject import ManPyObject

# ===========================================================================
# The entity object 
# ===========================================================================
class Entity(ManPyObject):
    type="Entity"

    def __init__(self, id=None, name=None, priority=0, dueDate=0, orderDate=0, 
                 isCritical=False, remainingProcessingTime=0,remainingSetupTime=0,currentStation=None,
                 status='Good',**kw):
        ManPyObject.__init__(self,id,name)
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
        self.priority=float(priority)
        self.dueDate=float(dueDate)
        self.orderDate=float(orderDate)
        #         a list that holds information about the schedule 
        #         of the entity (when it enters and exits every station)
        self.schedule=[]
        # the current station of the entity
        self.currentStation=currentStation
        #         values to be used in the internal processing of compoundObjects
        self.internal = False               # informs if the entity is being processed internally
        if isinstance(isCritical, unicode):
            self.isCritical=bool(int(isCritical))
        elif isinstance(isCritical, int): 
            self.isCritical=bool(isCritical)          # flag to inform weather the entity is critical -> preemption
        else:
            self.isCritical=isCritical
        self.manager=None                   # default value
        self.numberOfUnits=1                # default value
        # variable used to differentiate entities with and entities without routes
        self.family='Entity'
        
        # variables to be used by OperatorRouter
        self.proceed=False               # boolean that is used to check weather the entity can proceed to the candidateReceiver
        self.candidateReceivers=[]          # list of candidateReceivers of the entity (those stations that can receive the entity
        self.candidateReceiver=None         # the station that is finaly chosen to receive the entity
        # alias used for printing the Route
        self.alias=None
        self.remainingProcessingTime=remainingProcessingTime
        self.remainingSetupTime=remainingSetupTime
        self.status=status
        
    #===========================================================================
    # return the responsible operator for the current step, not implemented for entities
    #===========================================================================
    def responsibleForCurrentStep(self):
        return None
   
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
    
    #===========================================================================
    # print the route (the different stations the entity moved through)
    #===========================================================================
    def printRoute(self):
        pass
    
    #===========================================================================
    # method not implemented yet
    #===========================================================================
    def checkIfRequiredPartsReady(self):
        return True
    
    #===========================================================================
    # method not implemented yet
    #===========================================================================
    def getRequiredParts(self):
        return []
    