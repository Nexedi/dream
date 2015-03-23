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
schedules the availability of an object according to its shift pattern
'''

# from SimPy.Simulation import now, Process, hold, request, release, infinity
import simpy
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption
from copy import deepcopy

# ===========================================================================
# the shift scheduler class
# ===========================================================================
class ShiftScheduler(ObjectInterruption):

    # =======================================================================
    # the __init__() method of the class
    # =======================================================================
    def __init__(self, id='', name='', victim=None, shiftPattern=[], endUnfinished=False, receiveBeforeEndThreshold=0.0,
                 thresholdTimeIsOnShift=True,rolling=False,lastOffShiftDuration=10,**kw):
        ObjectInterruption.__init__(self,victim=victim)
        self.type='ShiftScheduler'
        self.shiftPattern=shiftPattern
        self.endUnfinished=endUnfinished    #flag that shows if half processed Jobs should end after the shift ends
        # if the end of shift is below this threshold then the victim is on shift but does not accept new entities
        self.receiveBeforeEndThreshold=receiveBeforeEndThreshold   
        # flag that shows if the threshold time is counted as off-shift or waiting
        self.thresholdTimeIsOnShift=thresholdTimeIsOnShift
        self.rolling=rolling
        self.lastOffShiftDuration=lastOffShiftDuration
    
    # =======================================================================
    # initialize for every replications
    # =======================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.remainingShiftPattern=list(self.shiftPattern) 
#         self.victimEndedLastProcessing=self.env.event()
        self.waitingSignal=False
               
    # =======================================================================
    #    The run method for the failure which has to served by a repairman
    # =======================================================================
    def run(self):
        from CoreObject import CoreObject
        from ObjectResource import ObjectResource
        
        # the victim should not be interrupted but the scheduler should wait for the processing to finish before the stations turns to off-shift mode
        self.victim.totalOffShiftTime=0
        self.victim.timeLastShiftEnded=self.env.now
        # if in the beginning the victim is offShift set it as such
        if float(self.remainingShiftPattern[0][0])!=self.env.now:
            self.victim.onShift=False
            # if the victim is CoreObject interrupt it. Else ask the router for allocation of operators
            # TODO more generic implementation
            if issubclass(self.victim.__class__, CoreObject): 
                # interrupt the victim only if it was not previously interrupted
                self.interruptVictim()                      # interrupt the victim
            else:
                if self.victim.schedule:
                    if not self.victim.schedule[-1].get("exitTime", None):
                        self.victim.schedule[-1]["exitTime"] = self.env.now
                self.victim.schedule.append({"station": {'id':'off-shift'},
                                             "entranceTime": self.env.now})
                self.requestAllocation()

            self.victim.timeLastShiftEnded=self.env.now
            self.victim.endShiftTimes.append(self.env.now)
            self.outputTrace(self.victim.name,"is off shift")

        while 1:
            if not self.victim.onShift:
                assert self.remainingShiftPattern[0][0] > self.env.now, "Incorrect shift defined for %s (%s)" % (self.env.now, self.shiftPattern)
                yield self.env.timeout(float(self.remainingShiftPattern[0][0]-self.env.now))    # wait for the onShift
                # if the victim is CoreObject reactivate it. Else ask the router for allocation of operators
                # TODO more generic implementation
                self.victim.onShift=True
                self.victim.totalOffShiftTime+=self.env.now-self.victim.timeLastShiftEnded
                self.victim.timeLastShiftStarted=self.env.now
                self.victim.startShiftTimes.append(self.env.now)
                self.outputTrace(self.victim.name,"is on shift")
                startShift=self.env.now
                if issubclass(self.victim.__class__, CoreObject): 
                    self.reactivateVictim()                 # re-activate the victim in case it was interrupted
                else:
                    if self.victim.schedule:
                        if not self.victim.schedule[-1].get("exitTime", None):
                            self.victim.schedule[-1]["exitTime"] = self.env.now
                    self.requestAllocation()

                # if the victim has interruptions that measure only the on-shift time, they have to be notified
                for oi in self.victim.objectInterruptions:
                    if oi.isWaitingForVictimOnShift:
                        if oi.expectedSignals['victimOnShift']:
                            self.sendSignal(receiver=oi, signal=oi.victimOnShift)
            else:
                timeToEndShift=float(self.remainingShiftPattern[0][1]-self.env.now)
                yield self.env.timeout(timeToEndShift-self.receiveBeforeEndThreshold)   # wait until the entry threshold
                # if threshold time is counted as onShift, then yield until the end of shift. Else, set as off-shift now
                if self.thresholdTimeIsOnShift:
                    self.victim.isLocked=True   # lock the entry of the victim
                    yield self.env.timeout(self.receiveBeforeEndThreshold)    # wait until the shift is over
                    self.victim.isLocked=False  # unlock the entry of the victim
                # if the victim is station
                if issubclass(self.victim.__class__, CoreObject):
                    # if the mode is to end current work before going off-shift and there is current work, 
                    # wait for victimEndedLastProcessing or victimFailed
                    # signal before going off-shift
                    if self.endUnfinished and self.victim.isProcessing:
                        self.victim.isWorkingOnTheLast=True
                        self.waitingSignal=True
                        self.expectedSignals['endedLastProcessing']=1
                        self.expectedSignals['victimFailed']=1
                        receivedEvent=yield self.env.any_of([self.victim.endedLastProcessing , self.victimFailed])
                        if self.victim.endedLastProcessing in receivedEvent:
                            transmitter, eventTime=self.victim.endedLastProcessing.value
                            self.victim.endedLastProcessing=self.env.event()
                        elif self.victimFailed in receivedEvent:
                            transmitter, eventTime=self.victimFailed.value
                            self.victimFailed=self.env.event()
                    # sometimes the time to end the last process may overcome the time to restart theshift
                    # so off-shift should not happen at such a case
                    if len(self.remainingShiftPattern)>1:
                        if self.env.now>=self.remainingShiftPattern[1][0]:
                            self.remainingShiftPattern.pop(0)                
                            # if there is no more shift data break the loop
                            if len(self.remainingShiftPattern)==0:
                                break
                            continue
                    self.interruptVictim()
                # if the victim is operator
                elif issubclass(self.victim.__class__, ObjectResource):
                    # if the operator is working in a station and the mode is 
                    # to stop current work in the end of shift
                    # signal to the station that the operator has to leave
                    station=self.victim.workingStation
                    if station:
                        if not self.endUnfinished and station.expectedSignals['processOperatorUnavailable']:
                            self.sendSignal(receiver=station, signal=station.processOperatorUnavailable)
                    if self.victim.schedule:
                        if not self.victim.schedule[-1].get("exitTime", None):
                            self.victim.schedule[-1]["exitTime"] = self.env.now
                    self.victim.schedule.append({"station": {'id':'off-shift'},
                                                 "entranceTime": self.env.now})
                    self.requestAllocation()

                # if the victim has interruptions that measure only the on-shift time, they have to be notified
                for oi in self.victim.objectInterruptions:
                    if oi.isWaitingForVictimOffShift:
                        if oi.expectedSignals['victimOffShift']:
                            self.sendSignal(receiver=oi, signal=oi.victimOffShift)
                       
                self.victim.onShift=False                        # get the victim off-shift
                self.victim.timeLastShiftEnded=self.env.now
                self.victim.endShiftTimes.append(self.env.now)
                self.outputTrace(self.victim.name,"is off shift")
                
                self.remainingShiftPattern.pop(0)
            # if there is no more shift data 
            if not len(self.remainingShiftPattern):
                # if the shift is rolling recreate the pattern
                if self.rolling:
                    self.remainingShiftPattern=deepcopy(self.shiftPattern)
                    for record in self.remainingShiftPattern:
                        # for value in record:
                        record[0]+=(self.env.now+self.lastOffShiftDuration)
                        record[1]+=(self.env.now+self.lastOffShiftDuration)
                # else break the loop
                else:
                    break
