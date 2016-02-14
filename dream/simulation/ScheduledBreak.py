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
Created on 3 Jan 2014

@author: George
'''

'''
models deterministic scheduled breaks (e.g. lunch break)
designed to work only with ObjectResource as victim
'''

import simpy
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption
from copy import deepcopy

# ===========================================================================
# the shift scheduler class
# ===========================================================================
class ScheduledBreak(ObjectInterruption):

    # =======================================================================
    # the __init__() method of the class
    # =======================================================================
    def __init__(self, id='', name='', victim=None, breakPattern=[], endUnfinished=False, receiveBeforeEndThreshold=0.0,
                 rolling=False,lastNoBreakDuration=0,**kw):
        ObjectInterruption.__init__(self,victim=victim)
        self.type='ShiftScheduler'
        self.breakPattern=breakPattern
        self.endUnfinished=endUnfinished    #flag that shows if half processed Jobs should end after the shift ends
        # if the end of shift is below this threshold then the victim is on shift but does not accept new entities
        self.receiveBeforeEndThreshold=receiveBeforeEndThreshold   
        # flag that shows if the threshold time is counted as off-shift or waiting
        self.rolling=rolling
        self.lastNoBreakDuration=lastNoBreakDuration
    
    # =======================================================================
    # initialize for every replications
    # =======================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.remainingBreakPattern=list(self.breakPattern) 
        self.waitingSignal=False
               
    # =======================================================================
    #    The run method for the failure which has to served by a repairman
    # =======================================================================
    def run(self):       
        # the victim should not be interrupted but the scheduler should wait for the processing to finish before the stations turns to off-shift mode
        self.victim.totalOffShiftTime=0
        self.victim.timeLastShiftEnded=self.env.now
        # if in the beginning the victim is on break set it as such
        if float(self.remainingBreakPattern[0][0])==self.env.now:
            self.victim.onBreak=True
            if self.victim.schedule:
                if not self.victim.schedule[-1].get("exitTime", None):
                    self.victim.schedule[-1]["exitTime"] = self.env.now
            self.victim.schedule.append({"station": {'id':'on-break'},
                                         "entranceTime": self.env.now})
            self.requestAllocation()

            self.victim.timeLastBreakStarted=self.env.now  
            self.outputTrace(self.victim.name,"is on break")

        while 1:
            if not self.victim.onBreak:
                timeToStartBreak=float(self.remainingBreakPattern[0][0]-self.env.now)
                yield self.env.timeout(timeToStartBreak-self.receiveBeforeEndThreshold)   # wait until the entry threshold
                # if the operator is working in a station and the mode is 
                # to stop current work in the end of shift
                # signal to the station that the operator has to leave
                station=self.victim.workingStation
                if station:
                    # signal the station that operator left
                    if not self.endUnfinished and station.expectedSignals['processOperatorUnavailable']:
                        self.sendSignal(receiver=station, signal=station.processOperatorUnavailable)
                    # if SkilledRouter waits for the station to finish, send this signal to this router
                    from Globals import G
                    from dream.simulation.SkilledOperatorRouter import SkilledRouter
                    if G.RouterList[0].__class__ is SkilledRouter and \
                            station.id in G.RouterList[0].expectedFinishSignalsDict.keys() and \
                            not G.RouterList[0].expectedFinishSignalsDict[station.id].triggered:
                        self.sendSignal(receiver=G.RouterList[0], signal=G.RouterList[0].expectedFinishSignalsDict[station.id],
                                            sender=station)
                if self.victim.schedule:
                    if not self.victim.schedule[-1].get("exitTime", None):
                        self.victim.schedule[-1]["exitTime"] = self.env.now
                self.victim.schedule.append({"station": {'id':'on-break'},
                                             "entranceTime": self.env.now})
                self.requestAllocation()

                self.victim.onBreak=True                        # get the victim off-shift
                self.victim.timeLastBreakStarted=self.env.now
                self.outputTrace(self.victim.name,"is on break")
            else:               
                assert self.remainingBreakPattern[0][1] > self.env.now, "Incorrect shift defined for %s (%s)" % (self.env.now, self.breakPattern)
                yield self.env.timeout(float(self.remainingBreakPattern[0][1]-self.env.now))    # wait for the onShift
                self.victim.onBreak=False
                self.victim.totalBreakTime+=self.env.now-self.victim.timeLastBreakStarted
                self.victim.timeLastBreakEnded=self.env.now
                self.outputTrace(self.victim.name,"returned from break")
                if self.victim.schedule:
                    if not self.victim.schedule[-1].get("exitTime", None):
                        self.victim.schedule[-1]["exitTime"] = self.env.now
                self.requestAllocation()
                self.remainingBreakPattern.pop(0)
    
            # if there is no more shift data 
            if not len(self.remainingBreakPattern):
                # if the shift is rolling recreate the pattern
                if self.rolling:
                    self.remainingBreakPattern=deepcopy(self.breakPattern)
                    for record in self.remainingBreakPattern:
                        # for value in record:
                        record[0]+=(self.env.now+self.lastNoBreakDuration)
                        record[1]+=(self.env.now+self.lastNoBreakDuration)
                # else break the loop
                else:
                    break
