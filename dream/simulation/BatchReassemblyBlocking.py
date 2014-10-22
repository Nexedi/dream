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
        if self.timeLastBlockageStarted:
            # calculate how much time the previous station was offShift 
            offShift=0
            for endShiftTime in station.endShiftTimes:
                # if there was end of shift while the station was blocked
                if endShiftTime>=self.timeLastBlockageStarted:
                    end=endShiftTime
                    lastShift=True
                    # find the start of the next shift
                    for startShiftTime in station.startShiftTimes:
                        if startShiftTime>end:
                            lastShift=False
                            nextStart=startShiftTime
                            break
                    # if there is not start of next shift, then it was the last shift, so 
                    # the station is currently off. Subtract this off-shift time
                    if lastShift:
                        offShift+=self.env.now-end
                    # else, subtract the whole off-shift time of that shift
                    else:
                        offShift+=nextStart-end
            self.totalBlockageTime+=self.env.now-self.timeLastBlockageStarted-offShift  
