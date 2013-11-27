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
        if self.getGiverObject():
            return self.getGiverObject().haveToDispose(self) and len(self.getActiveObjectQueue())<self.capacity
        else:
            return False
                
    #checks if the Machine can dispose an entity. Returns True only to the potential receiver     
    def haveToDispose(self, callerObject=None):
        if callerObject!=None:
            #check it the object that called the method holds an Entity that requests for current object        
            if self.getReceiverObject()==callerObject:
                return len(self.getActiveObjectQueue())>0    #return according to the state of the machine
        return False

    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):      
        activeEntity=Queue.getEntity(self)
        self.nextStationId=activeEntity.remainingRoute[1][0]    #read the next station id
        activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return activeEntity  

    #get the giver object in a getEntity transaction.       
    def getGiverObject(self):
        #if there are predecessors use default method
        if len(self.previous)>0:
            return Queue.getGiverObject(self)
        from Globals import G
        #loop through the objects to see if there is one that holds an Entity requesting for current object
        for obj in G.ObjList:
            if len(obj.getActiveObjectQueue())>0 and (obj!=self) and now()!=0:
                activeEntity=obj.getActiveObjectQueue()[0]
                if activeEntity.remainingRoute[0][0]==self.id:
                    return obj
        return None
    
    #get the receiver object in a removeEntity transaction.  
    def getReceiverObject(self):
        #if there are successors use default method
        if len(self.next)>0:
            return Queue.getReceiverObject(self)
        if len(self.getActiveObjectQueue())>0:
            from Globals import G
            receiverObjectId=self.getActiveObjectQueue()[0].remainingRoute[0][0]
            #loop through the objects to to assign the next station to the one that has the id
            for obj in G.ObjList:
                if obj.id==receiverObjectId:
                    return obj    
        else: 
            return None 
        
        