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
Created on 14 11 2013

@author: George
'''
'''
Customization of the BatchDecomposition so that it sets the start time in the Batch.
Custom object. Maybe we should have a generic method that the objects can call in order to set that
'''

from BatchDecomposition import BatchDecomposition

class BatchDecompositionStartTime(BatchDecomposition):
    
    '''
    #gets an entity from the predecessor     
    def getEntity(self):
        activeEntity=BatchDecomposition.getEntity(self)
        activeEntity.startTime=self.env.now
        return activeEntity
    '''
    
    #removes an entity from the object    
    def removeEntity(self, entity=None):
        # if it is the first sub-batch of the parent batch that leaves
        # assign it as the batch start time
        if len(self.getActiveObjectQueue())==self.numberOfSubBatches:
            batch=self.getActiveObjectQueue()[0].parentBatch
            batch.startTime=self.env.now
        activeEntity=BatchDecomposition.removeEntity(self, entity)
        return activeEntity
