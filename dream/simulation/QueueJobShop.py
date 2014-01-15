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

# ===========================================================================
# the QueueJobShop object
# ===========================================================================
class QueueJobShop(Queue):
    # =======================================================================
    # set all the objects in previous and next
    # =======================================================================
    def initialize(self):
        from Globals import G
        self.previous=G.ObjList
        self.next=G.ObjList
        Queue.initialize(self)  #run default behaviour
    
    # =======================================================================    
    # checks if the Queue can accept an entity       
    # it checks also the next station of the Entity 
    # and returns true only if the active object is the next station
    # ======================================================================= 
    def canAccept(self, callerObject=None): 
        if callerObject!=None:
            #check it the caller object holds an Entity that requests for current object
            if len(callerObject.getActiveObjectQueue())>0:
                activeEntity=callerObject.getActiveObjectQueue()[0]
                # check if the object in the active entity's route next step
                if self.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
#                 if activeEntity.remainingRoute[0][0]==self.id:
                    return len(self.getActiveObjectQueue())<self.capacity  #return according to the state of the Queue
        return False   
    
    # =======================================================================
    # checks if the Machine can dispose an entity. 
    # Returns True only to the potential receiver
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller = callerObject
        
        
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(len(activeObject.next)==1 or callerObject==None):
            activeObject.receiver=activeObject.next[0]
            return len(activeObjectQueue)>0\
                    and thecaller==activeObject.receiver
        
        #give the entity to the possible receiver that is waiting for the most time. 
        #plant does not do this in every occasion!       
        maxTimeWaiting=0     
                                                        # loop through the object in the successor list
        for object in activeObject.next:
            if(object.canAccept(activeObject)):                                 # if the object can accept
                timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                    maxTimeWaiting=timeWaiting
                    self.receiver=object                           # and update the receiver to the index of this object
        
        #return True if the Queue has Entities and the caller is the receiver
        return len(activeObjectQueue)>0 and (thecaller is self.receiver) 

    # =======================================================================
    # gets an entity from the predecessor that the predecessor index points to
    # =======================================================================     
    def getEntity(self):      
        activeObject = self.getActiveObject()
        activeEntity=Queue.getEntity(self)
        # read the possible receivers - update the next list
        import Globals
        nextObjectIds=activeEntity.remainingRoute[1].get('stationIdsList',[])
        nextObjects = []
        for nextObjectId in nextObjectIds:
            nextObject = Globals.findObjectById(nextObjectId)
            nextObjects.append(nextObject)
        activeObject.next = nextObjects
         
        activeEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return activeEntity  
        