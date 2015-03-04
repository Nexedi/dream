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
Created on 13 Feb 2013

@author: Ioannis
'''

'''
models a entity/job assigned operator (manager)
'''

# from SimPy.Simulation import Resource, now
import simpy
from Operator import Operator

# ===========================================================================
#                 the resource that operates the machines
# ===========================================================================
class OperatorManagedJob(Operator):
    
    def __init__(self, id, name, capacity=1,schedulingRule="FIFO",**kw):
        Operator.__init__(self,id=id,name=name,capacity=capacity,schedulingRule=schedulingRule)
        from Globals import G
        G.OperatorManagedJobsList.append(self) 
    
    # =======================================================================
    #                    checks if the worker is available
    #     it is called only by the have to dispose of a QueueManagedJob
    #                         and its sortEntities
    # =======================================================================       
    def checkIfResourceIsAvailable(self,callerObject=None):
        activeResourceQueue = self.getResourceQueue()
        workingOn=self.workingStation
        # in case the operator has the flag operatorAssigned raised 
        #    (meaning the operator will explicitly be assigned to a machine)
        #    return false even if he is free
        # If there is no callerObject defined then do not check the operatorAssignedTo variable
        if callerObject:
            # if the operator is not yet assigned then return the default behaviour
            if self.operatorAssignedTo==None:
                return len(activeResourceQueue)<self.capacity
            # otherwise, in case the operator is occupied, check if the occupier is the 
            #     object the operator is assigned to
            else:
                if len(activeResourceQueue):
#                     if self.operatorAssignedTo==activeResourceQueue[0].victim:
                    if self.operatorAssignedTo==workingOn:
                        return self.operatorAssignedTo==callerObject
                return (self.operatorAssignedTo==callerObject) and len(activeResourceQueue)<self.capacity
        # otherwise, (if the callerObject is None) check if the operator is assigned and if yes
        #     then perform the default behaviour
        else:
#             if self.operatorAssignedTo==None:
#                 return False
            return len(activeResourceQueue)<self.capacity
    
    #=======================================================================
    # findCandidateEntities method finding the candidateEntities of the operator  
    #=======================================================================
    def findCandidateEntities(self, pendingEntities=[]):
        if pendingEntities:
            for entity in [x for x in pendingEntities if x.currentStation.canDeliver(x) and x.manager==self]:
                self.candidateEntities.append(entity)
                
    #===========================================================================
    # recursive method that searches for entities with available receivers
    #===========================================================================
    def findAvailableEntity(self):
        from Globals import G
        router=G.RouterList[0]
        # if the candidateEntities and the entitiesWithOccupiedReceivers lists are identical then return None 
        if len(set(self.candidateEntities).intersection(router.entitiesWithOccupiedReceivers))==len(self.candidateEntities):
            return None
        availableEntity=next(x for x in self.candidateEntities if not x in router.entitiesWithOccupiedReceivers)
        receiverAvailability=False
        if availableEntity:
            for receiver in availableEntity.candidateReceivers:
                if not receiver in router.occupiedReceivers:
                    receiverAvailability=True
                    break
            # if there are no available receivers for the entity
            if not receiverAvailability:
                router.entitiesWithOccupiedReceivers.append(availableEntity)
                return self.findAvailableEntity()
        return availableEntity
    
    #===========================================================================
    # method that finds a candidate entity for an operator
    #===========================================================================
    def findCandidateEntity(self):
        from Globals import G
        router=G.RouterList[0]
        # pick a candidateEntity
        candidateEntity=self.findAvailableEntity()
        if not candidateEntity:
            candidateEntity=next(x for x in self.candidateEntities)
            router.conflictingEntities.append(candidateEntity)
        return candidateEntity