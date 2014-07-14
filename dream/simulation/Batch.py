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
        Entity.__init__(self, name=name, id=id)
        self.numberOfUnits=numberOfUnits
        self.numberOfSubBatches=1       #integer that shows in how many sub batches is the batch broken
        self.subBatchList=[]            #list that contains the sub-batches that this batch has been broken into
        self.routing=[]                 # list that holds the route a child entity has picked in case the other children have to follow the same routing  
    
    
