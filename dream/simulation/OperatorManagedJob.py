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

from SimPy.Simulation import Resource, now
from Operator import Operator

# ===========================================================================
#                 the resource that operates the machines
# ===========================================================================
class OperatorManagedJob(Operator):
    
#     def __init__(self, id, name, capacity=1,schedulingRule="FIFO"):
#         Operator.__init__(self,id=id,name=name,capacity=capacity,schedulingRule=schedulingRule)
#         self.operatorAssignedTo=None
    
    # =======================================================================
    #                    checks if the worker is available
    #     it is called only by the have to dispose of a QueueManagedJob
    #                         and its sortEntities
    # =======================================================================       
    def checkIfResourceIsAvailable(self,callerObject=None):
        activeResourceQueue = self.getResourceQueue()
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
                    if self.operatorAssignedTo==activeResourceQueue[0].victim:
                        return self.operatorAssignedTo==callerObject
                return (self.operatorAssignedTo==callerObject) and len(self.Res.activeQ)<self.capacity
        # otherwise, (if the callerObject is None) check if the operator is assigned and if yes
        #     then perform the default behaviour
        else:
#             if self.operatorAssignedTo==None:
#                 return False
            return len(self.Res.activeQ)<self.capacity

