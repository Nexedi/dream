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
the buffer of the capacity station. Only change from queue that it can be blocked.
'''

import simpy
from dream.simulation.Queue import Queue
# ===========================================================================
#                            the Queue object
# ===========================================================================
class CapacityStationBuffer(Queue):
    #===========================================================================
    # the __init__ method of the CapacityStationBuffer
    #===========================================================================
    def __init__(self, id, name, requireFullProject =False, capacity=float("inf"), isDummy=False, 
                 schedulingRule="FIFO", gatherWipStat=False, notRequiredOperations=[],**kw):
        Queue.__init__(self, id, name, capacity=capacity)
        self.isLocked=True
        self.requireFullProject=requireFullProject       # flag that shows if here the whole project is assembled
        from dream.simulation.Globals import G
        if hasattr(G, 'CapacityStationBufferList'):
            G.CapacityStationBufferList.append(self)
        else:
            G.CapacityStationBufferList=[]
            G.CapacityStationBufferList.append(self)
        self.notRequiredOperations=notRequiredOperations    # operations that are not required to be assembled

        
    def initialize(self):
        Queue.initialize(self)
        import dream.simulation.Globals as Globals
        # identify the notRequiredOperations
        # input gives only stationId, buffer and exit should be identified
        notRequiredOperations=[]
        for id in self.notRequiredOperations:
            station=Globals.findObjectById(id)
            notRequiredOperations.append(station.id)
            bufferId=station.previous[0].id
            notRequiredOperations.append(bufferId)
            exitId=station.next[0].id
            notRequiredOperations.append(exitId)
        self.notRequiredOperations=notRequiredOperations
        self.isLocked=True

    def canAccept(self, callerObject=None):
        if self.isLocked:
            return False
        return Queue.canAccept(self)

    def haveToDispose(self, callerObject=None):
        activeObjectQ=self.getActiveObjectQueue()
        if len(activeObjectQ)==0:
            return False
        if not activeObjectQ[0].shouldMove:
            return False

    # put the entities that should move in front
    def sortEntities(self):
        activeObjectQ=self.getActiveObjectQueue()
        activeObjectQ.sort(key=lambda x: x.shouldMove, reverse=True) 
