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
Created on 28 Aug 2014

@author: Ioannis
'''
'''
Inherits from ConditionalBuffer. It is the buffer before the MouldAssembly. 
Only if all the mould (order) components are present, will it be able to dispose them
'''

from ConditionalBuffer import ConditionalBuffer
import simpy

# ===========================================================================
# Error in the setting up of the WIP
# ===========================================================================
class NoCallerError(Exception):
    def __init__(self, callerError):
        Exception.__init__(self, callerError) 

# ===========================================================================
# the MouldAssemblyBuffer object
# ===========================================================================
class MouldAssemblyBuffer(ConditionalBuffer):
    # =======================================================================                
    # the default __init__ method of the QueueManagedJob class
    # whereas the default capacity is set to infinity
    # =======================================================================
    def __init__(self,  id, name, capacity=-1, isDummy=False,
                 schedulingRule="FIFO",**kw):
        ConditionalBuffer.__init__(self, id=id, name=name, capacity=capacity,
                                 isDummy=isDummy, schedulingRule=schedulingRule)
    
    assemblyValidTypes=set(['Mold Base', 'Mold Insert', 'Slider', 'Misc', 'Electrode','Z-Standards', 'K-Standards'])
    assemblyInvalidTypes=set(['Mold','Injection Molding Part'])
    # =======================================================================
    # extends the default get entity
    # =======================================================================
    def getEntity(self):
        '''
        it checks if the activeQ has received all the entities
            of the same parentOrder needed to assemble the mould and set 
            the corresponding componentsReadyForAssembly flag of the parentOrder.
        We suppose that only one MouldAssembly buffer is present in the topology
            and thus there is no need to check if entities of the same parentOrder
            are present in other MouldAssemblyBuffers
        '''
        # execute default behaviour
        from Globals import G
        activeObject = self.getActiveObject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        activeEntity=ConditionalBuffer.getEntity(self)
        # if the activeEntity is of type orderComponent
        try:
            if activeEntity.componentType in self.assemblyValidTypes:
                activeEntity.readyForAssembly=1
            # for all the components that have the same parent Order as the activeEntity
            activeEntity.order.componentsReadyForAssembly = 1
            for entity in activeEntity.order.getAssemblyComponents():
            # if one of them has not reach the Buffer yet,
                if not entity.readyForAssembly:
            # the mould is not ready for assembly
                    activeEntity.order.componentsReadyForAssembly = 0
                    break
        # if the activeEntity is of type Mould
        except:
            pass
        return activeEntity
    
    # =======================================================================
    # extends the default behaviour 
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        '''
        checks if the Buffer can dispose an entity. 
        Returns True only to the potential receiver
        Returns True when all the mould components/parts reside either
        in the internal buffer activeQ or in the callerObject's activeQ
        '''
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller=callerObject
        # and then perform the default behaviour
        if ConditionalBuffer.haveToDispose(self,callerObject):
            # update the local variable activeEntity
            activeEntity=activeObjectQueue[0]
            # if we are at the start of the simulation then check if all the child components 
            # of a specific order are present in the buffer and ready to be delivered to the assembly station
            try:
                # for all the components that have the same parent Order as the activeEntity
                activeEntity.order.componentsReadyForAssembly = 1
                for entity in activeEntity.order.getAssemblyComponents():
                # if one of them has not reach the Buffer yet,
                    if not entity.readyForAssembly:
                # the mould is not ready for assembly
                        activeEntity.order.componentsReadyForAssembly = 0
                        break
            # if the activeEntity is of type Mould
            except:
                pass

            try:
                return thecaller.getActiveObjectQueue()[0].order is activeEntity.order\
                       and activeEntity.order.componentsReadyForAssembly
            except:
                return activeEntity.order.componentsReadyForAssembly
    
    # =======================================================================                
    # Sort the entities of the activeQ
    # =======================================================================
    ''' bring the entities that are ready for assembly to the front'''
    def sortEntities(self):
        activeObject = self.getActiveObject()
        # run the default sorting of the Queue first
        ConditionalBuffer.sortEntities(self)
        # and in the end sort according to the ConditionalBuffer sorting rule
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # if all the components of the same mould are present then move them to the front of the activeQ
        activeObjectQueue.sort(key=lambda x: x.order.componentsReadyForAssembly, reverse=True)
        if activeObjectQueue:
            # keep the first entity of the activeQ
            activeEntity = activeObjectQueue[0]
            # bring the entities that have the same parentOrder as the first entity to the front
            activeObjectQueue.sort(key=lambda x: not x.order.name == activeEntity.order.name)

