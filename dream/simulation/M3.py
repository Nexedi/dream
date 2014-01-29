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
Customization of BatchScrapMachine so that it gets blocked if the succeeding BatchDecomposition is blocked.
Custom object, not too much of generic use. Maybe in the future there should be a composite 
BatchScrapMachine->BatchDecomposition
'''

from BatchScrapMachine import BatchScrapMachine
from SimPy.Simulation import now

class M3(BatchScrapMachine):
    
    # =======================================================================
    # This is only for a BatchScrapMachine that is followed by a BatchDecomposition
    # We consider that since this is in essence one station, the BatchScrapMachine
    # should be blocked if the BatchDecomposition is blocked
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        nextObject=self.next[0]
        batchReassemblyHoldsBatch=False
        if len(nextObject.getActiveObjectQueue())>0:
            if nextObject.getActiveObjectQueue()[0].type=='Batch' or len(nextObject.getActiveObjectQueue())==4:
                batchReassemblyHoldsBatch=True
                
               
        # if we have only one predecessor just check if there is a place, 
        # the machine is up and the predecessor has an entity to dispose
        # this is done to achieve better (cpu) processing time
        if(len(activeObject.previous)==1):
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                 and giverObject.haveToDispose(activeObject) and (not batchReassemblyHoldsBatch)
    
    
    