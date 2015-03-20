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
Created on 19 Mar 2015

@author: George
'''

'''
models the breaks that CoreObjects or ObjectResources can have
'''

# from SimPy.Simulation import now, Process, hold, request, release
import simpy
import math
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

class Break(ObjectInterruption):
    
    def __init__(self, id='',name='',victim=None, distribution={},deteriorationType='constant',
                 endUnfinished=True,**kw):
        ObjectInterruption.__init__(self,id,name,victim=victim)
        self.rngTTB=RandomNumberGenerator(self, distribution.get('TTB',{'Fixed':{'mean':100}}))
        self.rngTTR=RandomNumberGenerator(self, distribution.get('TTR',{'Fixed':{'mean':10}}))
        self.type="Break"
        
        # shows how the time to break is measured
        # 'constant' means it counts not matter the state of the victim
        self.deteriorationType=deteriorationType
        self.endUnfinished=endUnfinished

    def initialize(self):
        ObjectInterruption.initialize(self)
        self.victimStartsProcess=self.env.event()
        self.victimEndsProcess=self.env.event()       
        
    # =======================================================================
    #    The run method for the break which has to served by a repairman
    # =======================================================================
    def run(self):     
        from CoreObject import CoreObject
        from ObjectResource import ObjectResource

        while 1:
            # if the time that the victim is off-shift should not be counted
            timeToBreak=self.rngTTB.generateNumber()
            remainingTimeToBreak=timeToBreak
            breakNotTriggered=True
            
            # if time to break counts not matter the state of the victim
            if self.deteriorationType=='constant':
                yield self.env.timeout(remainingTimeToBreak)
#             # if time to break counts only in onShift time
#             elif self.deteriorationType=='onShift':
#                 while breakNotTriggered:
#                     timeRestartedCounting=self.env.now
#                     self.isWaitingForVictimOffShift=True
#                     
#                     self.expectedSignals['victimOffShift']=1
#                     
#                     receivedEvent=yield self.env.timeout(remainingTimeToBreak) | self.victimOffShift 
#                     # the break should receive a signal if there is a shift-off triggered
#                     if self.victimOffShift in receivedEvent:
#                         assert self.victim.onShift==False, 'break cannot recalculate TTB if the victim is onShift'
#                         self.victimOffShift=self.env.event()
#                         remainingTimeToBreak=remainingTimeToBreak-(self.env.now-timeRestartedCounting)   
#                         # wait for the shift to start again
#                         self.isWaitingForVictimOnShift=True
#                         
#                         self.expectedSignals['victimOnShift']=1
#                         
#                         yield self.victimOnShift
# 
#                         self.isWaitingForVictimOnShift=False
#                         self.victimOnShift=self.env.event()
#                         assert self.victim.onShift==True, 'the victim of break must be onShift to continue counting the TTB'
#                     else:
#                         self.isWaitingForVictimOffShift=False
#                         breakNotTriggered=False
# 
#             # if time to break counts only in working time
#             elif self.deteriorationType=='working':
#                 # wait for victim to start process
#                 
#                 self.expectedSignals['victimStartsProcess']=1
#                 
#                 yield self.victimStartsProcess
# 
#                 self.victimStartsProcess=self.env.event()
#                 while breakNotTriggered:
#                     timeRestartedCounting=self.env.now
#                     
#                     self.expectedSignals['victimEndsProcess']=1
#                     
#                     # wait either for the break or end of process
#                     receivedEvent=yield self.env.timeout(remainingTimeTobreak) | self.victimEndsProcess 
#                     if self.victimEndsProcess in receivedEvent:
#                         self.victimEndsProcess=self.env.event()
#                         remainingTimeTobreak=remainingTimeTobreak-(self.env.now-timeRestartedCounting)
#                         
#                         self.expectedSignals['victimStartsProcess']=1
#                         
#                         yield self.victimStartsProcess
# 
#                         # wait for victim to start again processing
#                         self.victimStartsProcess=self.env.event()
#                     else:
#                         breakNotTriggered=False
            
                
            # interrupt the victim
            # if the victim is station
            if issubclass(self.victim.__class__, CoreObject):
                # if the mode is to end current work before going to break and there is current work, 
                # wait for victimEndedLastProcessing or victimFailed
                # signal before going into break
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
                self.victim.schedule.append({"station": {'id':'on-break'},
                                             "entranceTime": self.env.now})
                self.requestAllocation()
            
            self.victim.timeLastBreakStarted=self.env.now     
            self.victim.onBreak=True                        # get the victim on break     
            self.outputTrace(self.victim.name,"starts break")
            # update the break time
            breakTime=self.env.now                
                                
            yield self.env.timeout(self.rngTTR.generateNumber())    # wait until the repairing process is over
            
            # add the break
            # if victim is off shift add only the fail time before the shift ended
            if not self.victim.onShift and breakTime < self.victim.timeLastShiftEnded:
                self.victim.totalBreakTime+=self.victim.timeLastShiftEnded-breakTime
            # if the victim was off shift since the start of the break add nothing
            elif not self.victim.onShift and breakTime >= self.victim.timeLastShiftEnded:
                pass
            # if victim was off shift in the start of the fail time, add on
            elif self.victim.onShift and breakTime < self.victim.timeLastShiftStarted:
                self.victim.totalBreakTime+=self.env.now-self.victim.timeLastShiftStarted
                # this can happen only if deteriorationType is constant
                assert self.deteriorationType=='constant', 'object got break while off-shift and deterioration type not constant' 
            else:
                self.victim.totalBreakTime+=self.env.now-breakTime   

            if issubclass(self.victim.__class__, CoreObject): 
                self.reactivateVictim()                 # re-activate the victim in case it was interrupted
            else:
                if self.victim.schedule:
                    if not self.victim.schedule[-1].get("exitTime", None):
                        self.victim.schedule[-1]["exitTime"] = self.env.now
                self.requestAllocation()
            
            self.victim.timeLastBreakEnded=self.env.now     
            self.victim.onBreak=False                        # get the victim on break     
            self.outputTrace(self.victim.name,"returns from break")
