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
Created on 15 Jan 2014

@author: Ioannis
'''
'''
Inherits from QueueManagedJob. Checks the condition of (a) component(s) before it can dispose them/it
'''

from QueueManagedJob import QueueManagedJob

# ===========================================================================
# Error in the setting up of the WIP
# ===========================================================================
class NoCallerError(Exception):
    def __init__(self, callerError):
        Exception.__init__(self, callerError) 

# ===========================================================================
# the ConditionalBuffer object
# ===========================================================================
class ConditionalBufferManaged(QueueManagedJob):
    # =======================================================================                
    # the default __init__ method of the QueueManagedJob class
    # whereas the default capacity is set to infinity
    # =======================================================================
    def __init__(self,  id, name, capacity=-1, isDummy=False,
                 schedulingRule="FIFO",**kw):
        QueueManagedJob.__init__(self, id=id, name=name, capacity=capacity,
        isDummy=isDummy, schedulingRule=schedulingRule)
        
    # =======================================================================
    # checks if the Buffer can dispose an entity. 
    # Returns True only to the potential receiver
    # If it holds secondary components, checks first if the basicsEnded is
    # True first. Otherwise, it waits until the basics are ended.
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        # and then perform the default behaviour
        if QueueManagedJob.haveToDispose(self,callerObject):
            return activeObject.checkCondition()
        return False
        
    # =======================================================================
    # check whether the condition is True
    # ======================================================================= 
    def checkCondition(self):
        activeObject = self.getActiveObject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # read the entity to be disposed
        activeEntity=activeObjectQueue[0]
        # assert that the entity.type is OrderComponent
        assert activeEntity.type=='OrderComponent',\
                 "the entity to be disposed is not of type OrderComponent"
        # check weather the entity to be moved is Basic
        if activeEntity.componentType=='Basic':
            return True
        # or whether it is of type Secondary
        elif activeEntity.componentType=='Secondary':
            # in that case check if the basics are already ended
            if activeEntity.order.basicsEnded:
                return True
        # in any other case return False
        else:
            return False
    
    # =======================================================================                
    # sort the entities of the activeQ
    # bring to the front the entities of componentType Basic
    # and the entities of componentType Secondary that 
    # have the flag basicsEnded set
    # =======================================================================
    def sortEntities(self):
        activeObject = self.getActiveObject()
        # (run the default behaviour - loan from Queue)
        # if we have sorting according to multiple criteria we have to call the sorter many times
        if self.schedulingRule=="MC":
            for criterion in reversed(self.multipleCriterionList):
               self.activeQSorter(criterion=criterion) 
        #else we just use the default scheduling rule
        else:
            self.activeQSorter()
        
        # and in the end sort according to the ConditionalBuffer sorting rule
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # search for the entities in the activeObjectQueue that have available manager
        # if no entity is managed then the list managedEntities has zero length
        managedEntities=[]
        for entity in activeObjectQueue:
            entity.managerAvailable=False
            if entity.manager:
                managedEntities.append(entity)
                if entity.manager.checkIfResourceIsAvailable(self.objectSortingFor):
                    entity.managerAvailable=True
        # if the entities are operated
        if len(managedEntities):
            # if the componentType of the entities in the activeQueue is Basic then don't move it to the end of the activeQ
            # else if the componentType is Secondary and it's basics are not ended then move it to the back
            activeObjectQueue.sort(key=lambda x: x.managerAvailable\
                                            and \
                                                (x.componentType=='Basic' \
                                                or\
                                                (x.componentType=='Secondary'\
                                                 and\
                                                 x.order.basicsEnded)), reverse=True)
        # otherwise do not check for managers availability
        else:
            activeObjectQueue.sort(key=lambda x: x.componentType=='Basic'\
                                                or\
                                                (x.componentType=='Secondary'\
                                                 and\
                                                 x.order.basicsEnded),reverse=True)
#         activeObjectQueue.sort(key=lambda x: x.managerAvailable, reverse=True)

    #===========================================================================
    # checks whether the entity can proceed to a successor object
    #===========================================================================
    def canDeliver(self, entity=None):
        activeObject=self.getActiveObject()
        assert activeObject.isInActiveQueue(entity), entity.id +' not in the internalQueue of'+ activeObject.id
        activeEntity=entity
        
        # for entities of type OrderComponent, if they reside at a conditionalBuffer, 
        #     they must wait till their basicsEnded flag is raised
        if activeEntity.type=='OrderComponent':
            if (activeEntity.componentType=='Secondary'\
                and activeEntity.order.basicsEnded==False):
                return False
        
        mayProceed=False
        # for all the possible receivers of an entity check whether they can accept and then set accordingly the canProceed flag of the entity 
        for nextObject in [object for object in activeObject.next if object.canAcceptEntity(activeEntity)]:
            activeEntity.proceed=True
            activeEntity.candidateReceivers.append(nextObject)
            mayProceed=True
        return mayProceed
