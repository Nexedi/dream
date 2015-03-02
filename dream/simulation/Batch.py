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

#===============================================================================
# The batch object
#===============================================================================
class Batch(Entity):
    type="Batch"

    def __init__(self, id, name, numberOfUnits=1, currentStation=None, 
                 remainingProcessingTime=0, unitsToProcess=0, **kw):
        Entity.__init__(self, name=name, id=id, remainingProcessingTime=remainingProcessingTime,
                        currentStation=currentStation)
        self.numberOfUnits=int(numberOfUnits)
        self.numberOfSubBatches=1       #integer that shows in how many sub batches is the batch broken
        self.subBatchList=[]            #list that contains the sub-batches that this batch has been broken into
        self.unitsToProcess=int(float(unitsToProcess))
    
    #===========================================================================
    # finds the schedule of each child and returns the combined route 
    # (it should be the same for every sub-batch)
    #===========================================================================
    def routing(self):
        route=[]
        for child in self.subBatchList:
            for step in child.schedule:
                route.append(step["station"])
        route=list(set(route))
        return route
