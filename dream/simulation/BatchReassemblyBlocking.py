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

from BatchReassembly import BatchReassembly

class BatchReassemblyBlocking(BatchReassembly):

    # =======================================================================
    #  extend behaviour to send canDispose signal to the correct predecessor  
    # =======================================================================
    def removeEntity(self, entity=None):
        activeEntity=BatchReassembly.removeEntity(self, entity)
        from Queue import Queue
        station=self
        # loop through the previous stations until a Queue is reached
        while 1:
            previous=station.previous[0]
            # when the Queue is reached send to it a canDispose signal with sender its successor
            if issubclass(previous.__class__, Queue):
                if previous.expectedSignals['canDispose']:
                    self.sendSignal(receiver=previous, signal=previous.canDispose, sender=station)
                break
            # continue with further previous stations
            else:
                station=previous
        return activeEntity

    # =======================================================================
    #              adds the blockage time to totalBlockageTime 
    #                    each time an Entity is removed
    # =======================================================================
    def addBlockage(self): 
        # find the previous station
        station=self.previous[0]
        from Globals import G
        from ShiftScheduler import ShiftScheduler
        shift=[]
        # find the shiftPattern of the previous station
        for oi in G.ObjectInterruptionList:
            if issubclass(oi.__class__,ShiftScheduler):
                if oi.victim is station:
                    shift=oi.shiftPattern   
                    break             
        if self.timeLastBlockageStarted:
            # calculate how much time the previous station was offShift 
            offShift=0
            for i, record in enumerate(shift):
                start=record[0]
                end=record[1]
                if start>self.env.now:
                    break
                if end<self.timeLastBlockageStarted:
                    continue
                # if the there is offShift time in the blockage
                if end<self.env.now:
                    try:
                        offShift+=shift[i+1][0]-end        
                    except IndexError:
                        pass                   
            self.totalBlockageTime+=self.env.now-self.timeLastBlockageStarted-offShift  
