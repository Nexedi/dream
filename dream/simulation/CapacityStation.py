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
Created on 5 June 2013

@author: George
'''
'''
a station that can process a specified capacity in every time period
'''

from Queue import Queue

import simpy

# ===========================================================================
#                            the CapacityStation object
# ===========================================================================
class CapacityStation(Queue):
    
    #===========================================================================
    # the __init__ method of the CapacityStation
    #===========================================================================
    def __init__(self, id, name, capacity=float("inf"), intervalCapacity=[], schedulingRule="FIFO", gatherWipStat=False):
        Queue.__init__(self, id, name, capacity=capacity)
        # a list that holds the capacity (manhours) that is available in each interval
        self.intervalCapacity=intervalCapacity
        print self.id, intervalCapacity
        # a list that holds the capacity (manhours) that is available in each interval for the remaining time
        self.remainingIntervalCapacity=list(self.intervalCapacity)
        # blocks the entry of the capacity station, so that it can be manipulated to accept only in certain moments of simulation time
        self.isLocked=True
        
    def initialize(self):
        Queue.initialize(self)
        self.remainingIntervalCapacity=list(self.intervalCapacity)
        self.isLocked=True

    def canAccept(self, callerObject=None):
        if self.isLocked:
            return False
        return Queue.canAccept(self)
        
        