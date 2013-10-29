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
Created on 22 Oct 2013

@author: George
'''
'''
Batch is an Entity that contains a number of units
'''

from Entity import Entity
from SubBatch import SubBatch

#The batch object
class Batch(Entity):
    type="Batch"

    def __init__(self, id, name, numberOfUnits=1):
        Entity.__init__(self, name=name)
        self.id=id  
        self.numberOfUnits=numberOfUnits
        self.numberOfSubBatches=1       #integer that shows in how many sub batches is the batch broken
        self.subBatchList=[]            #list that contains the sub-batches that this batch has been broken into
    
#     #breaks the Batch to a number of SubBatches
#     def breakToSubBatches(self, numberOfSubBatches=2):
#         numberOfSubBatchUnits=self.numberOfUnits/numberOfSubBatches     #for now it considers that the division gives an integer 
#                                                                         #(E.g. 100 units to be divided to 4 sub-batches)
#         activeObjectQueue=self.currentStation.getActiveObjectQueue()    #get the internal queue of the active core object
#         activeObjectQueue.remove(self)                                  #the Batch is non-existent in this active Queue now (since it is broken)
#         for i in range(numberOfSubBatches):
#             subBatch=SubBatch(str(self.id)+'_'+str(i), self.name+"_SB_"
#                               +str(i), self.id, numberOfUnits=numberOfSubBatchUnits)    #create the sub-batch
#             activeObjectQueue.append(subBatch)                          #append the sub-batch to the active object Queue
#             self.subBatchList.append(subBatch)
#         self.numberOfSubBatches=numberOfSubBatches
#         
#     #re-assembles a batch that was broken into sub-batches    
#     def reAssembleBatch(self):
#         self.numberOfUnits=0
#         activeObjectQueue=self.subBatchList[0].currentStation.getActiveObjectQueue()    #get the internal queue of the active core object
#                                                                                         #it should be the same for all the sub-batches
#         for subBatch in self.subBatchList:
#             self.numberOfUnits+=subBatch.numberOfUnits      #maybe there are units lost (scrapped), so it has to be re-calculated
#             #the sub-batch no longer exists
#             activeObjectQueue.remove(subBatch)              
#             del subBatch
            
            
    
    