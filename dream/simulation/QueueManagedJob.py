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
# from SimPy.Simulation import now
import simpy
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
    
    def __init__(self, id, name, capacity=1, isDummy=False, schedulingRule="FIFO", **kw):
        QueueJobShop.__init__(self, id=id, name=name,capacity=capacity, isDummy=isDummy, schedulingRule=schedulingRule)
        # variable used by the sortEntities method 
        # to identify the object it will be sorting for (manager.checkIfResourceIsAvailable(self.objectSortingFor))
        self.objectSortingFor=None
        
       
    # =======================================================================
    # set all the objects in previous and next
    # =======================================================================
    def initialize(self):
        QueueJobShop.initialize(self)  #run default behaviour
        # variable used by the sortEntities method 
        #     to identify the object it will be sorting for (manager.checkIfResourceIsAvailable(self.objectSortingFor))
        self.objectSortingFor=None
        
    # =======================================================================
    # checks if the Queue can dispose an entity. 
    # Returns True only to the potential receiver
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller=callerObject
        # update the objectSortingFor variable to hold the value of the callerObject
        activeObject.objectSortingFor=thecaller
        # TODO: when the callerObject is not defined will receive error ass the checkIfResourceIsAvailable requests a caller
        
        #search if for one or more of the Entities the operator is available        
        haveEntityWithAvailableManager=False
        for entity in activeObjectQueue:
            if entity.manager:
                if entity.manager.checkIfResourceIsAvailable(thecaller):
                    haveEntityWithAvailableManager=True
                    break
            else:
                haveEntityWithAvailableManager=True
                break
        #if none of the Entities has an available manager return False
        if not haveEntityWithAvailableManager:
            return False
        #sort the internal queue so that the Entities that have an available manager go in the front
        # the sortEntities method needs a receiver defined to sort the entities according to the availability of the manager
        #     so if there is a caller define him ass receiver and after the sorting set the receiver again to None
        activeObject.sortEntities()
        activeObject.sortEntitiesForReceiver(activeObject.objectSortingFor)
        
        # and then perform the default behaviour
        return QueueJobShop.haveToDispose(self,thecaller)
    
    #===========================================================================
    #  signalRouter method
    #===========================================================================
    @staticmethod
    def signalRouter(receiver=None):
        # if an operator is not assigned to the receiver then do not signal the receiver but the Router
        # TODO: identifyEntityToGet needs giver defined but here is not yet defined for Machines and machineJobShops 
        try:
            if receiver.identifyEntityToGet().manager:
                if receiver.isLoadRequested():
                    if receiver.identifyEntityToGet().manager.isAssignedTo()!=receiver:
                        try:
                            from Globals import G
                            if not G.RouterList[0].invoked and G.RouterList[0].expectedSignals['isCalled']:
#                                 self.printTrace(self.id, signal='router')
                                G.RouterList[0].invoked=True
                                succeedTuple=(G.env, G.env.now)
                                G.RouterList[0].isCalled.succeed(succeedTuple)
                                G.RouterList[0].expectedSignals['isCalled']=0
                            return True
                        except:
                            return False
            else:
                return False
        except:
            return False
        
    # =======================================================================
    # override the default method so that Entities 
    # that have the manager available go in front
    # TODO: need receiver to sort the entities
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
                if entity.manager.checkIfResourceIsAvailable(self.objectSortingFor):
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
            activeObjectQueue.sort(key=lambda x: x.manager==operator and x.managerAvailable, reverse=True)
        else:
            # added for testing
            print 'there must be a caller defined for this kind of Queue sorting'