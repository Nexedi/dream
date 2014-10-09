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
Created on 09 10 2014

@author: George
'''
'''
Customization of BatchReassembly so that it sends isRequested to the first Queue before
'''

from BatchScrapMachine import BatchScrapMachine

class BatchScrapMachineAfterDecompose(BatchScrapMachine):

    # =======================================================================
    #  extend behaviour to send canDispose signal to the correct predecessor  
    # =======================================================================
    def removeEntity(self, entity=None):
        activeEntity=BatchScrapMachine.removeEntity(self, entity)
        from BatchDecompositionBlocking import BatchDecompositionBlocking
        decomposition = self.previous[0]
        if decomposition.__class__ is BatchDecompositionBlocking:
            buffer=decomposition.previous[0]
            if buffer.expectedSignals['canDispose']:
                self.sendSignal(receiver=buffer, signal=buffer.canDispose, sender=decomposition)
        return activeEntity
            
            
            