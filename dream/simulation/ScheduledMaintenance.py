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
models an one time scheduled maintenance. It happens and stops at fixed times and it is also deterministic
'''

# from SimPy.Simulation import now, Process, hold, request, release, infinity
import simpy
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

# ===========================================================================
# the scheduled maintenance class
# ===========================================================================
class ScheduledMaintenance(ObjectInterruption):
    # =======================================================================
    # the __init__() method of the class
    # =======================================================================
    def __init__(self, id='',name='',victim=None, start=0, duration=1, endStatus='interrupted',**kw):
        '''
            interrupted    : the maintenance starts immediately
            loaded         : the maintenance starts as soon as the victim has ended processing
            emptied        : the maintenance starts as soon as the victim is empty
        '''
        self.type="ScheduledMaintenance"
        ObjectInterruption.__init__(self,victim=victim)
        self.start=start
        self.duration=duration
        # the victim can be 'interrupted', 'loaded' or 'emptied' when the maintenance interruption happens
        self.endStatus=endStatus
    
    # =======================================================================
    # initialize for every replications
    # =======================================================================
    def initialize(self):
        ObjectInterruption.initialize(self) 
#         self.victimEndedLastProcessing=self.env.event()
        self.waitingSignal=False
        # not used yet
        self.victimIsEmptyBeforeMaintenance=self.env.event()
    
    # =======================================================================
    # the run method
    # holds till the defined start time, interrupts the victim,
    # holds for the maintenance duration, and finally reactivates the victim
    # =======================================================================
    def run(self):
        yield self.env.timeout(self.start)              #wait until the start time
        try:
            # if the station is occupied then it should not be interrupted but the maintenance must wait until the station is clear, 
            # the maintenance should be performed then (the victim is not interrupted)
            waitTime=0
            # TODO: should be implemented by signals or else there is no way to control when to stop the maintenance
            if(len(self.getVictimQueue())>0):           # when a Machine gets failure
                # TODO: boolean flags canInterruptProc, canInterruptBlock to be used when the desired behaviour is required
                if self.endStatus=='interrupted':
                    self.interruptVictim()                  # while in process it is interrupted
                elif self.endstatus=='loaded':
                    waitStartTime=self.env.now
                    self.victim.isWorkingOnTheLast=True
                    self.waitingSignal=True
                    # TODO: signal to be triggered by postProcessingActions of Machines
                    
                    self.expectedSignals['endedLastProcessing']=1
                    
                    yield self.victim.endedLastProcessing                # there is no signal yet that signals the change of such state (an object getting empty)
                    
                    transmitter, eventTime=self.victim.endedLastProcessing.value
                    assert eventTime==self.env.now, 'the processing end signal is not received by maintenance on time'
                    self.victim.endedLastProcessing=self.env.event()
                    waitTime=self.env.now-waitStartTime
                    self.interruptVictim()
                # XXX not yet implemented
                elif self.endStatus=='emptied':
                    waitStartTime=self.env.now
                    self.waitingSignal=True
                    # TODO: signal to be triggered by removeEntity of Machines
                    
                    self.expectedSignals['victimIsEmptyBeforeMaintenance']=1
                    
                    yield self.victimIsEmptyBeforeMaintenance                # there is no signal yet that signals the change of such state (an object getting empty)
                    
                    transmitter, eventTime=self.victimIsEmptyBeforeMaintenance.value
                    assert eventTime==self.env.now, 'the processing end signal is not received by maintenance on time'
                    self.victimIsEmptyBeforeMaintenance=self.env.event()
                    waitTime=self.env.now-waitStartTime
                    self.interruptVictim()
            self.victim.Up=False
            self.victim.timeLastFailure=self.env.now
            self.outputTrace(self.victim.name,"is down")
        except AttributeError:
            print "AttributeError1"
            
        yield self.env.timeout(self.duration)           # wait for the defined duration of the interruption 
        self.victim.totalFailureTime+=self.duration-waitTime
        
        try:
            if(len(self.getVictimQueue())>0):
                self.reactivateVictim()                 # since the maintenance is over, the victim is reactivated
            self.victim.Up=True              
            self.outputTrace(self.victim.name,"is up")                                           
        except AttributeError:
            print "AttributeError2"    
        

        