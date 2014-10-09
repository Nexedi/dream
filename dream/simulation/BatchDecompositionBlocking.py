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
Customization of BatchDecomposition so that it is blocked when the stations in front are (until it finds a buffer or an Exit)
'''

from BatchDecomposition import BatchDecomposition

class BatchDecompositionBlocking(BatchDecomposition):

    # =======================================================================
    # extend  default behaviour to return false if next stations are full
    # =======================================================================
    def canAcceptAndIsRequested(self, callerObject=None):
        station=self
        from Queue import Queue
        from Exit import Exit
        # loop to next stations until a Queue or Exit is reached
        while 1:
            next=station.next[0]
            # if a Queue or Exit is reached break
            if issubclass(next.__class__, Queue) or issubclass(next.__class__, Exit):
                break
            # if the object is not free return False
            if len(next.getActiveObjectQueue()):
                return False
            station=next
        # return according to parent
        return BatchDecomposition.canAcceptAndIsRequested(self, callerObject)




