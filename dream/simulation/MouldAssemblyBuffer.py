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
Inherits from QueuePreemptive. It is the buffer before the MouldAssembly. 
Only if all the mould (order) components are present, will it be able to dispose them
'''

from QueuePreemptive import QueuePreemptive
from SimPy.Simulation import now

# ===========================================================================
# the MouldAssemblyBuffer object
# ===========================================================================
class MouldAssemblyBuffer(QueuePreemptive):
    # ===========================================================================
    # the __init__ function
    # ===========================================================================
    def __init__(self, id, name, capacity=1, dummy=False, schedulingRule="MAB"):
        # run the default method, change the schedulingRule to 'MAB'
        # for description, check activeQSorter function of Queue coreObject 
        QueuePreemptive.__init__(self, id, name, capacity, dummy, schedulingRule)
        
        
    # =======================================================================
    # extend he default so that it sets order.basicsEnded to 1
    # if all the mould components are present in the activeQ
    # =======================================================================
    def getEntity(self):
        activeObject = self.getActiveObject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        activeEntity=QueuePreemptive.getEntity(self)   #execute default behaviour
        
        # check if all the basics have finished being processed
        # if the componentType of the activeEntity just received
        # is 'Basic' then go through the components of its parent order
        # to check weather they are present in activeObjectQueue
        if activeEntity.componentType=='Basic':
            # local variable to notify when all the basics are received
            allBasicsPresent = True
            # run through all the basicComponentsList
            for entity in activeEntity.order.basicComponentsList:
                # if a basic is not present then set the local variable False and break
                if not (entity in activeObjectQueue):
                    allBasicsPresent = False
                    break
            # if all are present then basicsEnded
            if allBasicsPresent:
                activeEntity.order.basicsEnded = 1
    
    # =======================================================================
    # checks if the Buffer can dispose an entity. 
    # Returns True only to the potential receiver
    # Returns True when all the mould components/parts reside either
    # in the internal buffer activeQ or in the callerObject's activeQ
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller = callerObject
        # assert that the callerObject is not None
        assert thecaller!=None, 'the caller object of the MouldAssemblyBuffer should not be None'
        
        thecallerQueue = callerObject.getActiveObjectQueue()
        # -------------------------------------------------------------------
        # check the length of the activeObjectQueue 
        # if the length is zero then no componentType or entity.type can be read
        if len(activeObjectQueue)==0:
            return False
        # read the entity to be disposed
        activeEntity = activeObjectQueue[0]
        # assert that the entity.type is OrderComponent
        assert activeEntity.type=='OrderComponent',\
                 "the entity to be disposed is not of type OrderComponent"
        # assert that the entity.componentType is Basic or Secondary
        assert activeEntity.componetType=='Secondary' or 'Basic',\
                 "the entity to be disposed is not Basic or Secondary component"
        # -------------------------------------------------------------------
        # check if the basics of the same parent order are already processed before disposing them to the next object
        # for all the components that have the same parent Order as the activeEntity
        for entity in activeEntity.order.basicComponentsList+\
                        activeEntity.order.secondaryComponentsList:
            # if one of them is not present in the activeObjectQueue or the caller's activeObjectQueue, return false 
            if not (entity in activeObjectQueue+thecallerQueue):
                return False
        # if the previous check is passed and all the needed components are present and ready for the MouldAssembly
        # then set the flag componentsReadyForAssembly to True (1)
        activeEntity.order.componentsReadyForAssembly = 1
        # -------------------------------------------------------------------
        #if we have only one possible receiver just check if the caller is the receiver
        if(len(activeObject.next)==1 or callerObject==None):
            activeObject.receiver=activeObject.next[0]
            # get the internal queue of the receiver
            receiverQueue = activeObject.receiver.getActiveObjectQueue()
            # if the successors (MouldAssembly) internal queue is empty then proceed with checking weather
            # the caller is the receiver
            if len(receiverQueue)==0:
                return thecaller==activeObject.receiver
            # otherwise, check additionally if the receiver holds orderComponents of the same order
            else:
                return thecaller==activeObject.receiver\
                        and receiverQueue[0].order==activeObjectQueue[0].order
        # -------------------------------------------------------------------
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
        # get the internal queue of the receiver
        receiverQueue = activeObject.receiver.getActiveObjectQueue()
        # if the successors (MouldAssembly) internal queue is empty then proceed with checking weather
        # the caller is the receiver
        if len(receiverQueue)==0:
            return thecaller==activeObject.receiver
        # otherwise, check additionally if the receiver holds orderComponents of the same order
        else:
            return thecaller==activeObject.receiver\
                    and receiverQueue[0].order==activeObjectQueue[0].order