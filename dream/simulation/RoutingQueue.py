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
Created on 11 Jul 2014

@author: Ioannis
'''
'''
Models a queue where entities can wait in order to be routed to the same server that other entities of the same parent entity have already been rooted.
if the level is reached Router object is signalled
'''


import simpy
from Queue import Queue
# ===========================================================================
#                            the Queue object
# ===========================================================================
class RoutingQueue(Queue):
    
    # =======================================================================
    # checks if the Queue can dispose an entity to the following object
    # it checks also who called it and returns TRUE 
    # only to the receiver that will give the entity. 
    # this is kind of slow I think got to check   
    # TODO: check which route the entities of the same parent entity have picked and route them the same way
    # =======================================================================
    def haveToDispose(self, callerObject=None): 
        activeObjectQueue=self.Res.users     
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(callerObject==None):
            return len(activeObjectQueue)>0
        thecaller=callerObject
        # local flag to control whether the callerObject can receive any of the entities in the buffers internal queue 
        isInRouting=False
        # for each entity in the buffer
        for entity in activeObjectQueue:
            if thecaller==entity.receiver:
                isInRouting=True
                break
        if not isInRouting:
            for entity in activeObjectQueue:
                if not entity.receiver:
                    # check additionally the next objects if they alreay hold a sub-batch of this batch
                    for o in self.next:
                        if o.getActiveObjectQueue():
                            if o.getActiveObjectQueue()[0].parentBatch==entity.parentBatch and not (o is callerObject):
                                return False
                    isInRouting=True
                    break
        return len(activeObjectQueue)>0 and thecaller.isInRouteOf(self) and isInRouting
    
    #===========================================================================
    # sort the entities of the queue for the receiver
    # TODO should a sortEntitiesForReceiver method to bring to the front the entity that can proceed in that route
    #===========================================================================
    def sortEntitiesForReceiver(self, receiver=None):
        activeObjectQueue=self.getActiveObjectQueue()
        activeObjectQueue.sort(key=lambda x: not(x.receiver is receiver), reverse=False)
        activeObjectQueue.sort(key=lambda x: x.receiver==None, reverse=True)
        activeObjectQueue.sort(key=lambda x: (x.receiver is receiver), reverse=True)

    
    # =======================================================================
    #            gets an entity from the predecessor that 
    #                the predecessor index points to
    # =======================================================================     
    def removeEntity(self, entity=None, resetFlags=True, addBlockage=True):
        activeEntity=Queue.removeEntity(self, entity)
        parentBatch=activeEntity.parentBatch
        for subbatch in parentBatch.subBatchList:
            subbatch.receiver=activeEntity.currentStation
        return activeEntity
    
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # TODO: sort the entities according to the schedulingRUle and then sort them again 
    #     bringing to the front the entities that can proceed
    # =======================================================================
    def sortEntities(self):
        #if we have sorting according to multiple criteria we have to call the sorter many times
        if self.schedulingRule=="MC":
            for criterion in reversed(self.multipleCriterionList):
               self.activeQSorter(criterion=criterion) 
        #else we just use the default scheduling rule
        else:
            self.activeQSorter()
        # sort again according to the existence or not of receiver attribute of the entities
        activeObjectQueue=self.getActiveObjectQueue()
        # if no entity.receiver, then show preference to these entities
        activeObjectQueue.sort(key=lambda x: x.receiver==None, reverse=True)
        # if there is entity.receiver then check if it is the same as the self.receiver of the queue (if any)
        activeObjectQueue.sort(key=lambda x: x.receiver==self.receiver, reverse=True)
