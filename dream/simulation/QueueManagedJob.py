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
# Error in the setting up of the WIP
# ===========================================================================
class NoCallerError(Exception):
    def __init__(self, callerError):
        Exception.__init__(self, callerError) 

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
        # assert that the callerObject is not None
        try:
            if callerObject:
                thecaller = callerObject
            else:
                raise NoCallerError('The caller of the QueueManagedJob haveToDispose must be defined')
        except NoCallerError as noCaller:
            print 'No caller error: {0}'.format(noCaller)
        
        #search if for one or more of the Entities the operator is available
        haveEntityWithAvailableManager=False
        for entity in activeObjectQueue:
            if entity.manager:
                if entity.manager.checkIfResourceIsAvailable(thecaller):
                    haveEntityWithAvailableManager=True
                    break
        #if none of the Entities has an available manager return False
        if not haveEntityWithAvailableManager:
            return False
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(len(activeObject.next)==1):
            activeObject.receiver=activeObject.next[0]
            #sort the internal queue so that the Entities that have an available manager go in the front
            activeObject.sortEntities()
            return len(activeObjectQueue)>0\
                    and thecaller==activeObject.receiver
        
        #give the entity to the possible receiver that is waiting for the most time.     
        maxTimeWaiting=0
        hasFreeReceiver=False
        for object in activeObject.next:                            # loop through the object in the successor list
            if(object.canAccept(activeObject)):                     # if the object can accept
                hasFreeReceiver=True
                timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                    maxTimeWaiting=timeWaiting
                    self.receiver=object                            # and update the receiver
        #sort the internal queue so that the Entities that have an available manager go in the front
        activeObject.sortEntities()
        #return True if the Queue has Entities and the caller is the receiver
        return len(activeObjectQueue)>0 and (thecaller is self.receiver) and hasFreeReceiver

    # =======================================================================
    # override the default method so that Entities 
    # that have the manager available go in front
    # =======================================================================
    def sortEntities(self):
        QueueJobShop.sortEntities(self)     #do the default sorting first
        activeObjectQueue=self.getActiveObjectQueue()
        # search for the entities in the activeObjectQueue that have available manager
        for entity in activeObjectQueue:
            entity.managerAvailable=False
            # if the entity has manager assigned
            if entity.manager:
                # check his availability    
                if entity.manager.checkIfResourceIsAvailable(self.receiver):
                    entity.managerAvailable=True
        # sort the active queue according to the availability of the managers
        activeObjectQueue.sort(key=lambda x: x.managerAvailable, reverse=True)
        
    # =======================================================================
    # sorting will take into account the manager calling the method
    #     the entities which have the same manager with the operator
    #     will be in front of the queue
    #     if the entity in front of the queue has no manager available 
    #     then the sorting is unsuccessful 
    # =======================================================================
    def sortEntitiesForOperator(self, operator=None):
        activeObjectQueue=self.getActiveObjectQueue()
        if operator:
#             self.sortEntities()
            activeObjectQueue.sort(key=lambda x: x.manager==operator and x.managerAvailable, reverse=True)
        else:
            # added for testing
            print 'there must be a caller defined for this kind of Queue sorting'