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
Created on 8 Nov 2012

@author: Ioannis
'''
'''
Core object that inherits from Queue. It takes SubBatches, 
only if all its contents are from the same Batch
'''

from Queue import Queue
# from SimPy.Simulation import now
import simpy

# ===========================================================================
#                        the LineClearance object
# ===========================================================================
class LineClearance(Queue):
    # =======================================================================
    #               checks if the Queue can accept an entity       
    #             it checks also who called it and returns TRUE 
    #            only to the potential giver that will give the entity.
    # =======================================================================  
    def canAccept(self, callerObject=None): 
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        giverObjectQueue=self.getGiverObjectQueue()
        
        #if we have only one potential giver just check if there is a place available
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(len(activeObject.previous)==1 or callerObject==None):
#             return len(activeObjectQueue)<activeObject.capacity
            if len(activeObjectQueue)==0:
                return giverObject.haveToDispose(activeObject)\
                        and giverObjectQueue[0].type == 'SubBatch'
            else:
                return len(activeObjectQueue)<activeObject.capacity\
                        and giverObject.haveToDispose(activeObject)\
                        and giverObjectQueue[0].type == 'SubBatch'\
                        and giverObjectQueue[0].batchId==activeObjectQueue[0].batchId
    
#         if len(activeObjectQueue)==activeObject.capacity:
#             return False
        
        thecaller=callerObject
        
        #return true only to the potential giver from which the queue will take 
        #flag=False
        #if thecaller is self.previous[self.predecessorIndex]:
        #    flag=True
        # all these checks may not be needed
        if len(activeObjectQueue)==0:
            return giverObject.haveToDispose(activeObject)\
                    and thecaller==giverObject\
                    and giverObjectQueue[0].type == 'SubBatch'
        else:
            return len(activeObjectQueue)<activeObject.capacity\
                    and thecaller==giverObject\
                    and giverObject.haveToDispose(activeObject)\
                    and giverObjectQueue[0].type == 'SubBatch'\
                    and giverObjectQueue[0].batchId == activeObjectQueue[0].batchId
    
