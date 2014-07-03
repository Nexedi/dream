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
Created on 2 July 2014

@author: Ioannis
'''

'''
models the failures that servers can have while they are on shift
'''

# from SimPy.Simulation import now, Process, hold, request, release
import simpy
import math
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption
from Failure import Failure

class ShiftFailure(Failure):
    
    # =======================================================================
    #    The run method for the failure which has to served by a repairman
    # =======================================================================
    def run(self):
        while 1:
            
            timeToFailure=self.rngTTF.generateNumber()
            remainingTimeToFailure=timeToFailure
            failureNotTriggered=True
            
            while failureNotTriggered:
                timeRestartedCounting=self.env.now
                # TODO: can also wait for interruptionStart signal of the victim and check whether the interruption is caused by a shiftScheduler
                receivedEvent=yield self.env.timeout(remainingTimeToFailure) | self.victim.interruptionStart #offShift
                # the failure should receive a signal if there is a shift-off triggered
                if self.victim.interruptionStart in receivedEvent:
                    # TODO: the signal interruptionStart is reset by the time it is received by the victim. not sure if will be still triggered when it is checked here 
                    assert self.victim.onShift==False, 'shiftFailure cannot recalculate TTF if the victim is onShift'
                    remainingTimeToFailure=remainingTimeToFailure-(self.env.now-timeRestartedCounting)
                    # wait for the shift to start again
                    yield self.victim.interruptionEnd
                    assert self.victim.onShift==True, 'the victim of shiftFailure must be onShift to continue counting the TTF'
                    # TODO: the signal interruptionStart is reset by the time it is received by the victim. not sure if will be still triggered when it is checked here
                else:
                    failureNotTriggered=False
                    
            self.interruptVictim()                      # interrupt the victim
            self.victim.Up=False
            self.victim.timeLastFailure=self.env.now           
            self.outputTrace("is down")
            # update the failure time
            failTime=self.env.now            
            if(self.repairman and self.repairman!="None"):     #if the failure needs a resource to be fixed, the machine waits until the 
                                            #resource is available
#                 print self.env.now, self.repairman.id, 'will be requested by', self.victim.id
#                 yield self.repairman.getResource().request()
#                 print self.repairman.Res.users
#                 # update the time that the repair started
#                 timeOperationStarted=self.env.now
#                 self.repairman.timeLastOperationStarted=self.env.now
                
                
                with self.repairman.getResource().request() as request:
                    yield request
                    # update the time that the repair started
                    timeOperationStarted=self.env.now
                    self.repairman.timeLastOperationStarted=self.env.now
                    
                    yield self.env.timeout(self.rngTTR.generateNumber())    # wait until the repairing process is over
                    self.victim.totalFailureTime+=self.env.now-failTime    
                    self.reactivateVictim()                     # since repairing is over, the Machine is reactivated
                    self.victim.Up=True              
                    self.outputTrace("is up")
                    
                    self.repairman.totalWorkingTime+=self.env.now-timeOperationStarted   
                continue
                
                
                                
            yield self.env.timeout(self.rngTTR.generateNumber())    # wait until the repairing process is over
            self.victim.totalFailureTime+=self.env.now-failTime    
            self.reactivateVictim()                     # since repairing is over, the Machine is reactivated
            self.victim.Up=True              
            self.outputTrace("is up")
            
#             if(self.repairman and self.repairman!="None"): #if a resource was used, it is now released
#                 print self.repairman.Res.users
#                 print self.env.now, self.repairman.id, 'about to be release from', self.victim.id
#                 self.repairman.Res.release()
#                 self.repairman.totalWorkingTime+=self.env.now-timeOperationStarted                                
    
