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
Inherits from QueueManagedJob. It is the buffer before the MouldAssembly. 
Only if all the mould (order) components are present, will it be able to dispose them
'''

from QueueManagedJob import QueueManagedJob
# from SimPy.Simulation import now
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
class MouldAssemblyBufferManaged(QueueManagedJob):
    # =======================================================================                
    # the default __init__ method of the QueueManagedJob class
    # whereas the default capacity is set to infinity
    # =======================================================================
    def __init__(self,  id, name, capacity=-1, isDummy=False,
                 schedulingRule="FIFO",**kw):
        QueueManagedJob.__init__(self, id=id, name=name, capacity=capacity,
                                 isDummy=isDummy, schedulingRule=schedulingRule)
        
    # =======================================================================                
    # Sort the entities of the activeQ
    # bring the entities that are ready for assembly to the front
    # =======================================================================
    def sortEntities(self):
        activeObject = self.getActiveObject()
        # run the default sorting of the Queue first
        QueueManagedJob.sortEntities(self)
        # and in the end sort according to the ConditionalBuffer sorting rule
        activeObjectQueue = activeObject.getActiveObjectQueue()
        # if all the components of the same mould are present then move them to the front of the activeQ
        activeObjectQueue.sort(key=lambda x: x.order.componentsReadyForAssembly, reverse=True)
        '''
        maybe the below lines should go after
        if len(activeObjectQueue)>0:
        '''
        # keep the first entity of the activeQ
        activeEntity = activeObjectQueue[0]
        # bring the entities that have the same parentOrder as the first entity to the front
        activeObjectQueue.sort(key=lambda x: not x.order.name == activeEntity.order.name)
        
    # =======================================================================
    # extend the default so that it sets order.basicsEnded to 1
    #     if all the mould components are present in the activeQ.
    # In addition, check if the activeQ has received all the entities
    #     of the same parentOrder needed to assemble the mould and set 
    #     the corresponding componentsReadyForAssembly flag of the parentOrder.
    # We suppose that only one MouldAssembly buffer is present in the topology
    #     and thus there is no need to check if entities of the same parentOrder
    #     are present in other MouldAssemblyBuffers
    # TODO: has to signal ConditionalBuffer to start sending entities again
    # =======================================================================
    def getEntity(self):
        activeObject = self.getActiveObject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        activeEntity=QueueManagedJob.getEntity(self)   #execute default behaviour
        # if the activeEntity is of type orderComponent
        try:
            if activeEntity.componentType=='Basic' or 'Secondary':
                activeEntity.readyForAssembly=1
            # check if all the basics have finished being processed in the previous machines
            # if the componentType of the activeEntity just received is 'Basic', 
            # go through the components of its parent order
            # and check if they are present in the activeObjectQueue
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
                # TODO: has to signal ConditionalBuffer to start sending entities again
                for secondary in [x for x in activeEntity.order.secondaryComponentsList if activeEntity.order.basicsEnded]:
                    if secondary.currentStation.__class__.__name__=='ConditionalBufferManaged':
#                         print now(), self.id, '                                                    signalling conditional buffer'
                        if secondary.currentStation.expectedSignals['canDispose']:
                            self.sendSignal(receiver=secondary.currentStation,signal=secondary.currentStation.canDispose)
                        break
            # for all the components that have the same parent Order as the activeEntity
            activeEntity.order.componentsReadyForAssembly = 1
            for entity in activeEntity.order.basicComponentsList+\
                            activeEntity.order.secondaryComponentsList:
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
    # checks if the Buffer can dispose an entity. 
    # Returns True only to the potential receiver
    # Returns True when all the mould components/parts reside either
    # in the internal buffer activeQ or in the callerObject's activeQ
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller=callerObject
        activeObject.objectSortingFor=thecaller
        # check the length of the activeObjectQueue 
        # if the length is zero then no componentType or entity.type can be read
        if len(activeObjectQueue)==0:
            return False
        # find out if there are entities with available managers that are ready for assembly
        activeEntity=None
        for entity in activeObjectQueue:
            if entity.order.componentsReadyForAssembly:
                # if the entity has no manager
                if entity.manager==None:
                    activeEntity=entity
                    break
                # otherwise, if the manager of the entity is available
                elif entity.manager.checkIfResourceIsAvailable(thecaller):
                    activeEntity=entity
                    break
        # if there is no entity in the activeQ that its parentOrder has the flag componentsReadyForAssembly set  
        if not activeEntity:
        # return false
            return False
        # sort the entities now that the receiver is updated
        activeObject.sortEntities()
        # update the activeEntity
        activeEntity=activeObjectQueue[0]
        # if no caller is defined then check if the entity to be disposed has the flag componentsReadyForAssembly raised
        if not thecaller:
            return activeEntity.order.componentsReadyForAssembly
        # if the successors (MouldAssembly) internal queue is empty then proceed with checking weather
        # the caller is the receiver
        # TODO: the activeEntity is already checked for the flag componentsReadyForAssembly
        if len(thecaller.getActiveObjectQueue())==0:
            if activeEntity.type=='Mould':
                return thecaller.isInRouteOf(activeObject)
            else:
                return thecaller.isInRouteOf(activeObject)\
                        and activeEntity.order.componentsReadyForAssembly
        # otherwise, check additionally if the receiver holds orderComponents of the same order
        # TODO: should revise, this check may be redundant, as the receiver (assembler must be empty in order to start receiving
        # It is therefore needed that the control is performed by the assembler's getEntity() 
        else:
            return thecaller.isInRouteOf(activeObject)\
                    and thecaller.getActiveObjectQueue()[0].order is activeEntity.order\
                    and activeEntity.order.componentsReadyForAssembly
                    
    #===========================================================================
    # checks whether the entity can proceed to a successor object
    #===========================================================================
    def canDeliver(self, entity=None):
        activeObject=self.getActiveObject()
        assert activeObject.isInActiveQueue(entity), entity.id +' not in the internalQueue of'+ activeObject.id
        activeEntity=entity
        
        # unassembled components of a mould must wait at a MouldAssemblyBuffer till the componentsReadyForAssembly flag is raised 
        if not activeEntity.order.componentsReadyForAssembly:
            return False
        mayProceed=False
        # for all the possible receivers of an entity check whether they can accept and then set accordingly the canProceed flag of the entity 
        for nextObject in [object for object in activeObject.next if object.canAcceptEntity(activeEntity)]:
            activeEntity.proceed=True
            activeEntity.candidateReceivers.append(nextObject)
            mayProceed=True
        return mayProceed
