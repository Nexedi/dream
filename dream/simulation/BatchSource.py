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
models the source object that generates the Batches Entities
'''
from Source import Source
from Batch import Batch
from Globals import G
from SimPy.Simulation import Process
from RandomNumberGenerator import RandomNumberGenerator

class BatchSource(Source):
    def __init__(self, id, name, distribution='Fixed', mean=1, item=Batch, batchNumberOfUnits = 1):
        Source.__init__(self, id=id, name=name, distribution=distribution, mean=mean, item=item)
#         Process.__init__(self)
#         # general properties
#         self.id=id   
#         self.objName=name   
#         self.distType=distribution                      # label that sets the distribution type
#         # properties used for statistics
#         self.totalInterArrivalTime=0                    # the total interarrival time 
#         self.numberOfArrivals=0                         # the number of entities that were created
#         # list containing objects that follow in the routing 
#         self.next=[]                                    # list with the next objects in the flow
#         self.nextIds=[]                                 # list with the ids of the next objects in the flow
#         self.previousIds=[]                             # list with the ids of the previous objects in the flow. 
#                                                         # For the source it is always empty!
#         self.type="Source"                              #String that shows the type of object
#         self.rng=RandomNumberGenerator(self, self.distType)
#         self.rng.avg=mean
#         self.item=item 
#         
        self.numberOfUnits = batchNumberOfUnits
        
        
    def createEntity(self):
        # return the newly created Entity
        return self.item(id = self.item.type+str(G.numberOfEntities), \
                         name = self.item.type+str(self.numberOfArrivals), numberOfUnits=self.numberOfUnits)
        
        