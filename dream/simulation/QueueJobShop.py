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
Created on 1 oct 2012

@author: George
'''
'''
extends the Queue object so that it can act as a jobshop station. Preceding station is read from the Entity
'''

import simpy
from Queue import Queue

# ===========================================================================
# the QueueJobShop object
# ===========================================================================
class QueueJobShop(Queue):
    
    # =======================================================================
    # parses inputs if they are given in a dictionary
    # =======================================================================       
    def parseInputs(self, inputsDict):
        Queue.parseInputs(self, inputsDict)
        from Globals import G
        G.QueueJobShopList.append(self)
    
    # =======================================================================
    # set all the objects in previous and next
    # =======================================================================
    def initialize(self):
        from Globals import G
        self.previous=G.ObjList
        self.next=[]
        Queue.initialize(self)  #run default behaviour
    
    # =======================================================================    
    # checks if the Queue can accept an entity       
    # it checks also the next station of the Entity 
    # and returns true only if the active object is the next station
    # ======================================================================= 
    def canAccept(self, callerObject=None):
        activeObjectQueue=self.Res.users
        thecaller=callerObject
        #return according to the state of the Queue
        #check it the caller object holds an Entity that requests for current object
        return len(self.Res.users)<self.capacity\
                and self.isInRoute(callerObject)
    
    #===========================================================================
    # method used to check whether the station is in the entity-to-be-received route
    # TODO: consider giving the activeEntity as attribute
    #===========================================================================
    def isInRoute(self, callerObject=None):
        activeObjectQueue=self.Res.users
        thecaller=callerObject
        # if the caller is not defined then return True. We are only interested in checking whether 
        # the station can accept whatever entity from whichever giver
        if not thecaller:
            return True
        #check it the caller object holds an Entity that requests for current object
        if len(thecaller.Res.users)>0:
            # TODO: make sure that the first entity of the callerObject is to be disposed
            activeEntity=thecaller.Res.users[0]
            # if the machine's Id is in the list of the entity's next stations
            if self.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                return True
        return False
    
    # =======================================================================
    # checks if the Queue can dispose an entity. 
    # Returns True only to the potential receiver
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        activeObjectQueue=self.Res.users
        thecaller = callerObject
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(callerObject==None):
            return len(activeObjectQueue)>0
        
        #return True if the Queue has Entities and the caller is in the self.next list
        return len(activeObjectQueue)>0\
                and (thecaller in self.next)\
                and thecaller.isInRoute(self)
    
    #===========================================================================
    # extend the default behaviour to check if whether the station 
    #     is in the route of the entity to be received
    #===========================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        if self.isInRoute(giverObject):
            return Queue.canAcceptAndIsRequested(self,giverObject)

    # =======================================================================
    # gets an entity from the predecessor that the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeEntity=Queue.getEntity(self)
        activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return activeEntity
    
    #===========================================================================
    # update the next list of the object after reading the remaining list of the activeEntity
    #===========================================================================
    def updateNext(self,entity=None):
        activeEntity=entity
        # read the possible receivers - update the next list
        import Globals
        nextObjectIds=activeEntity.remainingRoute[1].get('stationIdsList',[])
        nextObjects = []
        for nextObjectId in nextObjectIds:
            nextObject = Globals.findObjectById(nextObjectId)
            nextObjects.append(nextObject)
        # update the next list of the object
        for nextObject in nextObjects:
            # append only if not already in the list
            if nextObject not in self.next:
                self.next.append(nextObject)
    
    # =======================================================================
    # removes an entity from the Queue
    # extension to remove possible receivers accordingly
    # =======================================================================
    def removeEntity(self, entity=None):
        receiverObject=self.getReceiverObject()
        #run the default method
        activeEntity=Queue.removeEntity(self, entity)
        removeReceiver=True 
        # search in the internalQ. If an entity has the same receiver do not remove
        for ent in self.Res.users:
            nextObjectIds=ent.remainingRoute[0].get('stationIdsList',[])
            if receiverObject.id in nextObjectIds:
                removeReceiver=False      
        # if not entity had the same receiver then the receiver will be removed 
        if removeReceiver:
            self.next.remove(receiverObject)
        return activeEntity

        