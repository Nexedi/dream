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
from SimPy.Simulation import now

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
    
    def canAcceptAndIsRequested(self):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        giverObjectQueue = self.getGiverObjectQueue()
        
        #if we have only one potential giver just check if there is a place available and the potential giver has an entity to dispose
        if(len(activeObject.previous)==1):
            if len(activeObjectQueue)==0:
                return giverObject.haveToDispose(activeObject) and\
                       giverObjectQueue[0].type == 'SubBatch'
            else:
                return len(activeObjectQueue)<self.capacity and \
                       giverObject.haveToDispose(activeObject) and \
                       giverObjectQueue[0].type == 'SubBatch' and \
                       giverObjectQueue[0].batchId==activeObjectQueue[0].batchId
            
        isRequested=False               # dummy boolean variable to check if any potential giver has something to hand in
        maxTimeWaiting=0                # dummy timer to check which potential giver has been waiting the most
        
        #loop through the potential givers to see which have to dispose and which is the one blocked for longer
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject)):                 # if they have something to dispose off
                isRequested=True                                    # then the Queue is requested to handle the entity
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# if the predecessor has failed wile waiting 
                    timeWaiting=now()-object.timeLastFailureEnded   # then update according the timeWaiting to be compared with the ones
                else:                                               # of the other machines
                    timeWaiting=now()-object.timeLastEntityEnded
                
                #if more than one potential giver have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting):                    
                    activeObject.giver=object
                    maxTimeWaiting=timeWaiting                   
                                                                    # true when the Queue is not fully occupied and 
                                                                    # a predecessor is requesting it
        if len(activeObjectQueue)==0:
            return isRequested and\
                    activeObject.getGiverObjectQueue()[0].type == 'SubBatch'
        else:
            return len(activeObjectQueue)<self.capacity and\
                    isRequested and \
                    activeObject.getGiverObjectQueue()[0].type == 'SubBatch' and\
                    activeObject.getGiverObjectQueue()[0].batchId == activeObjectQueue[0].batchId
