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
SubBatch is an Entity that contains a number of units and is derived from a parent Batch
'''

from Entity import Entity

#The batch object
class SubBatch(Entity):
    type="SubBatch"

    def __init__(self, id, name, numberOfUnits=1, parentBatch=None, parentBatchName=None, parentBatchId=None,
                 remainingProcessingTime=0, currentStation=None, unitsToProcess=0,receiver=None,**kw):
        Entity.__init__(self, name=name, id=id, remainingProcessingTime=remainingProcessingTime,
                        currentStation=currentStation)
        self.numberOfUnits=int(numberOfUnits)
        self.parentBatch=parentBatch
        self.unitsToProcess=int(float(unitsToProcess))
        # if the parent batch was not given find it or create it
        if not self.parentBatch:
            # check if the parent batch is already created. If not, then create it
            batch=None
            from Batch import Batch
            from Globals import G
            for b in G.EntityList:
                if b.id==parentBatchId:
                    batch=b
            if batch:               #if the parent batch was found add the number of units of current sub-batch
                batch.numberOfUnits+=self.numberOfUnits
            else:     #if the parent batch was not found create it
                batch=Batch(parentBatchId,parentBatchName,numberOfUnits)
                G.EntityList.append(batch)
            self.parentBatch=batch
        self.batchId=self.parentBatch.id
        import Globals
        self.receiver=Globals.findObjectById(receiver)
        self.parentBatch.subBatchList.append(self)
        
