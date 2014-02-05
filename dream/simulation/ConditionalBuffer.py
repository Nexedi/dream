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
from SimPy.Simulation import now

# ===========================================================================
# Error in the setting up of the WIP
# ===========================================================================
class NoCallerError(Exception):
    def __init__(self, callerError):
        Exception.__init__(self, callerError) 

# ===========================================================================
# the ConditionalBuffer object
# ===========================================================================
class ConditionalBuffer(QueueManagedJob):
    # =======================================================================                
    # the default __init__ method of the QueueManagedJob class
    # whereas the default capacity is set to infinity
    # =======================================================================
    def __init__(self,  id, name, capacity=-1, dummy=False, schedulingRule="FIFO"):
        QueueManagedJob.__init__(self, id=id, name=name, capacity=capacity, dummy=dummy, schedulingRule=schedulingRule)
        
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

        # assert that the callerObject is not None
        try:
            if callerObject:
                thecaller = callerObject
            else:
                raise NoCallerError('The caller of the MouldAssemblyBuffer must be defined')
        except NoCallerError as noCaller:
            print 'No caller error: {0}'.format(noCaller)
        # check the length of the activeObjectQueue 
        # if the length is zero then no componentType or entity.type can be read
        if len(activeObjectQueue)==0:
            return False
        #if we have only one possible receiver just check if the receiver is the caller
        if(len(activeObject.next)==1):
            activeObject.receiver=activeObject.next[0]
            return thecaller is activeObject.receiver\
                and activeObject.checkCondition()
        #give the entity to the possible receiver that is waiting for the most time. 
        #plant does not do this in every occasion!       
        maxTimeWaiting=0     
        # loop through the object in the successor list
        for object in activeObject.next:
            # if the object can accept
            if(object.canAccept(activeObject)):
                timeWaiting=now()-object.timeLastEntityLeft
                # compare the time that it has been waiting with the others'
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                    maxTimeWaiting=timeWaiting
                    # and update the receiver to the index of this object
                    activeObject.receiver=object
        #return True if the Queue caller is the receiver
        return thecaller is activeObject.receiver\
            and activeObject.checkCondition()
        
    # =======================================================================
    # check whether the condition is True
    # ======================================================================= 
    def checkCondition(self):
        activeObject = self.getActiveObject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # read the entity to be disposed
        index = 0
        activeEntity=None
        for index in range(len(activeObjectQueue)):
            if activeObjectQueue[index].componentType=='Basic':
                activeEntity=activeObjectQueue[index]
                return True
            elif activeObjectQueue[index].order.basicsEnded:
                activeEntity=activeObjectQueue[index]
                return True
            index +=1
        # if there is no entity in the activeQ that its parentOrder has the flag componentsReadyForAssembly set  
        if not activeEntity:
        # return false
            return False
        
# #         activeEntity = activeObjectQueue[0]
#         # assert that the entity.type is OrderComponent
#         assert activeEntity.type=='OrderComponent',\
#                  "the entity to be disposed is not of type OrderComponent"
#         # if the type of the component is Secondary then verify that the basics of the same Order
#         # are already processed before disposing them to the next object
#         # TODO: the activeEntity is already checked if it has the basicsEnded flag set
#         return activeEntity.componentType=='Secondary'\
#                 and (activeEntity.order.basicsEnded)
    
    # =======================================================================                
    # sort the entities of the activeQ
    # bring to the front the entities of componentType Basic
    # and the entities of componentType Secondary that 
    # have the flag basicsEnded set
    # =======================================================================
    def sortEntities(self):
        activeObject = self.getActiveObject()
        # run the default sorting of the Queue first
        QueueManagedJob.sortEntities(self)
        # and in the end sort according to the ConditionalBuffer sorting rule
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # if the componentType of the entities in the activeQueue is Basic then don't move it to the end of the activeQ
        # else if the componentType is Secondary and it's basics are not ended then move it to the back
        activeObjectQueue.sort(key=lambda x: not ((x.componentType=='Basic')\
                                              or ((x.order.basicsEnded)\
                                                  and (x.componentType=='Secondary'))))
    