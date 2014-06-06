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
Created on 6 June 2013

@author: George
'''
'''
the exit of the capacity station. Only change from buffer that it can be blocked.
'''

from Exit import Exit

import simpy

# ===========================================================================
#                            the CapacityStationExit object
# ===========================================================================
class CapacityStationExit(Exit):
    
    #===========================================================================
    # the __init__ method of the CapacityStationExit
    #===========================================================================
    def __init__(self, id, name=None):
        Exit.__init__(self, id, name)
        self.isBlocked=True
        
    def initialize(self):
        Exit.initialize(self)
        self.isBlocked=True

    def canAccept(self):
        if self.isBlocked:
            return False
        return Exit.canAccept()