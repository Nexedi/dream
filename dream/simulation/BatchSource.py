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
Created on 29 Oct 2013

@author: Ioannis
'''
'''
models the source object that generates the Batches Entities
'''
from Source import Source
from Globals import G
# from SimPy.Simulation import Process
import simpy
from RandomNumberGenerator import RandomNumberGenerator

class BatchSource(Source):
    def __init__(self, id, name, interArrivalTime=None,
                 entity='Dream.Batch', batchNumberOfUnits=1, **kw):
        Source.__init__(self, id=id, name=name,
                        interArrivalTime=interArrivalTime, entity=entity)
        self.numberOfUnits = int(batchNumberOfUnits)
        from Globals import G
        G.BatchSourceList.append(self)  
        
        
    def createEntity(self):
        # return the newly created Entity
        return self.item(id = self.item.type+str(G.numberOfEntities), \
                         name = self.item.type+str(self.numberOfArrivals), numberOfUnits=self.numberOfUnits)
        
        
