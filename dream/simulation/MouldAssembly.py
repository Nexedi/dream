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
Created on 16 Jan 2014

@author: Ioannis
'''
'''
inherits from MachinePreemptive. It takes the components of an order and reassembles them as mould
'''
from MachinePreemptive import MachinePreemptive
from SimPy.Simulation import reactivate, now

# ===========================================================================
# the MachineJobShop object
# ===========================================================================
class MouldAssemble(MachinePreemptive):
    
    # =======================================================================
    # method that updates the capacity according to the componentsList of the 
    # activeEntity's parent order
    # =======================================================================
    def updateCapacity(self,capacity):
        activeObject = self.getActiveObject()
        self.capacity = capacity
        self.Res=Resource(self.capacity)
    
    # =======================================================================
    #     assemble method that assembles the components together to a mould (order
    # and returns the product of the assembly. Furthermore, it resets the capacity
    # of the internal queue to 1
    # =======================================================================
    def assemble(self):
        activeObject = self.getActiveObject()
        # get the internal queue of the active core object
        activeObjectQueue=activeObject.getActiveObjectQueue()
        # assert that all the components are of the same parent order
        for entity in activeObjectQueue:
            assert entity.order==activeObjectQueue[0].order,\
                'The components residing in the MouldAssembly internal queue\
                are not of the same parent order!'
        # if we have to create a new Entity (mould) this should be modified
        # we need the new entity's route, priority, isCritical flag, etc. 
        mouldToBeAssembled = activeObjectQueue[0].order
        del activeObjectQueue[:]
        # after assembling reset the capacity
        activeObject.updateCapacity(1)
        # append the mould entity to the internal Queue
        activeObjectQueue.append(mouldToBeAssembled)
        mouldToBeAssembled.currentStation=self
        self.timeLastEntityEnded=now()
    # =======================================================================
    # getEntity method that gets the entity from the giver
    # it should run in a loop till it get's all the entities from the same order
    # (with the flag componentsReadyForAssembly set)
    # =======================================================================
    def getEntity(self):
        activeObject = self.getActiveObject()
        giverObejct = activeObject.getGiverObject()
        giverObjectQueue = giverObject.getActiveObjectQueue()
        # read the number of basic and secondary components of the moulds
        capacity = len(giverObjectQueue[0].order.basicComponentsList\
                       +giverObjectQueue[0].order.secondaryComponentsList)
        # and set the capacity of the internal queue of the assembler
        activeObject.updateCapacity(capacity)
        # dummy variable to inform when the sum of needed components is received 
        # before the assembly-processing
        orderGroupReceived = False
        # the current activeEntity of the assembler
        activeEntity = None
        # loop till all the requested components are gathered
        # all the components are received at the same time
        while not orderGroupReceived:
            if not (activeEntity is None):
                assert activeEntity.order==giverObjectQueue[0].order,\
                    'the next Entity to be received by the MouldAssembly\
                     must have the same parent order as the activeEntity of the assembler' 
            # get the following component
            activeEntity=MachinePreemptive.getEntity(self)
            # if the length of the internal queue is equal to the updated capacity
            if len(activeObject.getActiveObjectQueue())==self.capacity:
            # then exit the while loop
                orderGroupReceived=True
        # perform the assembly-action and return the assembled mould
        activeEntity = activeObject.assemble()
        return activeEntity
        
    # =======================================================================
    # check if the assemble can accept an entity
    # returns true if it is empty 
    # =======================================================================   
    def canAccept(self, callerObject=None): 
        if callerObject!=None:
            #check it the caller object holds an Entity that requests for current object
            if len(callerObject.getActiveObjectQueue())>0:
                activeEntity=callerObject.getActiveObjectQueue()[0]
                # if the machine's Id is in the list of the entity's next stations 
                if self.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                    #return according to the state of the Queue
                    return len(self.getActiveObjectQueue())==0
        return False
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some predecessor waiting for it and updates the giver to the one that is to be taken
    # The internal queue of the assembler must be empty 
    # and the parent order of the entities to be received must have 
    # the flag componentsReadyForAssembly set to True 
    # =======================================================================    
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
                
        # if we have only one possible giver just check if the internal queue is empty
        # and if the giver has to dispose something
        if(len(activeObject.previous)==1):
            return giverObject.haveToDispose(activeObject)\
                and len(activeObjectQueue)==0\
                        
        # dummy variables that help prioritise the objects requesting to give objects to the Machine (activeObject)
        isRequested=False   # isRequested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0    # dummy variable counting the time a predecessor is blocked
        
        # loop through the possible givers to see which have to dispose and which is the one blocked for longer
        for object in activeObject.previous:
            # if the predecessor objects have entities to dispose of
            if(object.haveToDispose(activeObject) and object.receiver==self):
                isRequested=True
                # and if the predecessor has been down while trying to give away the Entity
                if(object.downTimeInTryingToReleaseCurrentEntity>0):
                # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                    timeWaiting=now()-object.timeLastFailureEnded
                # in any other case, it holds the time since the end of the Entity processing
                else:
                    timeWaiting=now()-object.timeLastEntityEnded
                
                #if more than one predecessor have to dispose, take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting):
                    activeObject.giver=object
                    maxTimeWaiting=timeWaiting    
        
        return len(activeObjectQueue)==0 and isRequested  
