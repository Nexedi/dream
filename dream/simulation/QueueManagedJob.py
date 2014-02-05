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
Created on 4 Feb 2014

@author: George
'''
'''
inherits from QueueJobShop. The difference is that it reads the operator from the Entity and
checks if he is available before it disposed it
'''
from SimPy.Simulation import now
from QueueJobShop import QueueJobShop

# ===========================================================================
# the QueueManagedJob object
# ===========================================================================
class QueueManagedJob(QueueJobShop):
    
    # =======================================================================
    # checks if the Queue can dispose an entity. 
    # Returns True only to the potential receiver
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller = callerObject
        
        #search if for one or more of the Entities the operator is available
        haveEntityWithAvailableManager=False
        for entity in activeObjectQueue:
            if entity.manager:        
                if entity.manager.checkIfResourceIsAvailable:
                    haveEntityWithAvailableManager=True
        #if none of the Entities has an available manager return False

        if not haveEntityWithAvailableManager:
            return False
        
        #sort the internal queue so that the Entities that have an available manager go in the front
        self.sortEntities()
        
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(len(activeObject.next)==1 or callerObject==None):
            
            activeObject.receiver=activeObject.next[0]
                   
            return len(activeObjectQueue)>0\
                    and thecaller==activeObject.receiver
        
        #give the entity to the possible receiver that is waiting for the most time.     
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

    #override the default method so that Entities that have the manager available go in front
    def sortEntities(self):
        QueueJobShop.sortEntities(self)     #do the default sorting first
        activeObjectQueue=self.getActiveObjectQueue()
        for entity in activeObjectQueue:
            entity.managerAvailable=False
            if entity.manager:        
                if entity.manager.checkIfResourceIsAvailable:
                    entity.managerAvailable=True
        activeObjectQueue.sort(key=lambda x: x.managerAvailable, reverse=True)
        
        