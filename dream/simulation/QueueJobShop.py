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

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold

from Queue import Queue


#the MachineJobShop object
class QueueJobShop(Queue):
    
    def initialize(self):
        Queue.initialize(self)
        self.giver=None     #the CoreObject that the activeObject will take an Entity from
        self.receiver=None  #the CoreObject that the activeObject will give an Entity to
        
    #checks if the Queue can accept an entity       
    #it checks also the next station of the Entity and returns true only if the active object is the next station 
    def canAccept(self, callerObject=None): 
        if callerObject!=None:
            #check it the caller object holds an Entity that requests for current object
            if len(callerObject.getActiveObjectQueue())>0:
                activeEntity=callerObject.getActiveObjectQueue()[0]
                if activeEntity.remainingRoute[0][0]==self.id:
                    return len(self.getActiveObjectQueue())<self.capacity  #return according to the state of the Queue
        return False

    #checks if the Queue can accept an entity and there is an entity in some predecessor waiting for it
    #also updates the predecessorIndex to the one that is to be taken
    def canAcceptAndIsRequested(self):   
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        # dummy variables that help prioritize the objects requesting to give objects to the Machine (activeObject)
        isRequested=False                                           # is requested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked
        
        from Globals import G
        # loop through the objects to see which have to dispose and which is the one blocked for longer                                                      # index used to set the predecessorIndex to the giver waiting the most
        for object in G.ObjList:
            if(object.haveToDispose(activeObject) and object.receiver==self):   #if the caller is the receiver and it has to dispose
                isRequested=True                                    # if the predecessor objects have entities to dispose of
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the predecessor has been down while trying to give away the Entity
                    timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                else:
                    timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.giver=object                 # the object to deliver the Entity to the activeObject is set to the ith member of the previous list
                    maxTimeWaiting=timeWaiting    
            #i+=1                                                    # in the next loops, check the other predecessors in the previous list
        return activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested
    
    
    #checks if the Machine can dispose an entity. Returns True only to the potential receiver     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        #return True if the Queue has Entities and the caller is the receiver
        return len(activeObjectQueue)>0 and (callerObject is self.receiver) 

    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):      
        activeEntity=Queue.getEntity(self)
        self.receiver=self.findObjectById(activeEntity.remainingRoute[1][0])    #read the next station 
        activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return activeEntity  

      
    #get the receiver object in a removeEntity transaction.  
    def getReceiverObject(self):
        #if there are successors use default method
        if len(self.next)>0:
            return Machine.getReceiverObject(self)
        #else if there is a receiver return it 
        elif self.receiver:
            return self.receiver 
        return None 
   
    #get the giver object in a getEntity transaction.       
    def getGiverObject(self):
        #if there are predecessors use default method
        if len(self.previous)>0:
            return Machine.getGiverObject(self)
        #else if there is a giver return it
        elif self.giver:
            return self.giver 
        return None 

    def findObjectById(self, id):
        from Globals import G
        for obj in G.ObjList:
            if obj.id==id:
                return obj
        