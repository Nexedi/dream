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
Created on 26 Aug 2014

@author: Ioannis
'''
'''
Inherits from QueueJobShop. Checks the condition of (a) order component(s) before it can dispose them/it
'''

from QueueJobShop import QueueJobShop

# ===========================================================================
# Error in the setting up of the WIP
# ===========================================================================
class NoCallerError(Exception):
    def __init__(self, callerError):
        Exception.__init__(self, callerError) 

# ===========================================================================
# the ConditionalBuffer object
# ===========================================================================
class ConditionalBuffer(QueueJobShop):
    # =======================================================================                
    # the default __init__ method of the QueueManagedJob class
    # whereas the default capacity is set to infinity
    # =======================================================================
    def __init__(self,  id, name, capacity=-1, isDummy=False,
                 schedulingRule="FIFO",**kw):
        QueueJobShop.__init__(self, id=id, name=name, capacity=capacity,
        isDummy=isDummy, schedulingRule=schedulingRule)
        
    # =======================================================================
    # checks if the Buffer can dispose an entity. 
    # Returns True only to the potential receiver
    # If it holds components with requiredParts, checks first if the requiredParts 
    # have concluded their route steps with sequence smaller than the sequence
    # of the activeEntity's next step
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        # and then perform the default behaviour
        if QueueJobShop.haveToDispose(self,callerObject):
            # sort the activeObjectQueue to brink the entities that can proceed to front
            activeObject.sortEntities()
            # return True if the first object of the queue can proceed
            return activeObjectQueue[0].mayProceed
        return False
    
    #===========================================================================
    # getEntity method
    # ass soon as the buffer receives an entity it controls if the entity is requested elsewhere,
    # then it checks if there other requested entities by the same requesting entity.
    # Finally, it is controlled whether all the requested parts have concluded 
    # their sequences for the requesting entity
    #===========================================================================
    def getEntity(self):
        activeEntity=QueueJobShop.getEntity(self)
        from Globals import G
        # for all the entities in the EntityList
        for entity in G.EntityList:
            requiredParts=entity.getRequiredParts()
            if requiredParts:
                # if the activeEntity is in the requierdParts of the entity
                if activeEntity in requiredParts:
                    # if the entity that requires the activeEntity can proceed then signal the currentStation of the entity
                    if entity.checkIfRequiredPartsReady() and entity.currentStation.expectedSignals['canDispose']:
                        entity.mayProceed=True
                        self.sendSignal(receiver=entity.currentStation, signal=entity.currentStation.canDispose)
        return activeEntity
    
    # =======================================================================                
    # sort the entities of the activeQ
    # bring to the front the entities that have no requestedParts for the following step in their route
    # or their requestedParts have concluded the step with sequence no bigger than the sequence of their next step  
    # =======================================================================
    def sortEntities(self):
        activeObject = self.getActiveObject()
        # perform the default sorting
        QueueJobShop.sortEntities(activeObject)
        # and in the end sort according to the ConditionalBuffer sorting rule
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # for every entity in the activeObjectQueue
        for entity in activeObjectQueue:
            # check if the requiredParts (if any) have concluded the steps with sequence smaller 
            # than the sequence of the entity next step
            entity.mayProceed=entity.checkIfRequiredPartsReady()
        activeObjectQueue.sort(key=lambda x: x.mayProceed, reverse=True)
