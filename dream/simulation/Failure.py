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
Created on 9 Nov 2012

@author: George
'''

'''
models the failures that servers can have
'''

# from SimPy.Simulation import now, Process, hold, request, release
import simpy
import math
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

class Failure(ObjectInterruption):
    
    def __init__(self, victim=None, distribution=None, index=0, repairman=None, offshift=False,
                 deteriorationType='constant'):
        #Process.__init__(self)
        ObjectInterruption.__init__(self,victim)
        if distribution:
            self.distType=distribution.get('distributionType','No')              # the distribution that the failure duration follows
            self.MTTF=distribution.get('MTTF',60)                  # the MTTF
            self.MTTR=distribution.get('MTTR',5)                  # the MTTR  
            self.availability=distribution.get('availability',100)  # the availability      
        else:
            self.distType='No'
            self.MTTF=60
            self.MTTR=5
            self.availability=100
        self.name="F"+str(index)
        self.repairman=repairman        # the resource that may be needed to fix the failure
                                        # if now resource is needed this will be "None" 
        self.type="Failure"
        self.id=0

        # shows how the time to failure is measured
        # 'constant' means it counts not matter the state of the victim
        # 'onShift' counts only if the victim is onShift
        # 'working' counts only working time
        self.deteriorationType=deteriorationType
        
        if(self.distType=="Availability"):      
            
            # -------------------------------------------------------------- 
            #     the following are used if we have availability defined 
            #      (as in plant) the erlang is a special case of Gamma. 
            #        To model the Mu and sigma (that is given in plant) 
            #    as alpha and beta for gamma you should do the following:
            #                     beta=(sigma^2)/Mu    
            #                     alpha=Mu/beta
            # --------------------------------------------------------------    
            self.AvailabilityMTTF=self.MTTR*(float(availability)/100)/(1-(float(availability)/100))
            self.sigma=0.707106781185547*self.MTTR   
            self.theta=(pow(self.sigma,2))/float(self.MTTR)             
            self.beta=self.theta
            self.alpha=(float(self.MTTR)/self.theta)        
            self.rngTTF=RandomNumberGenerator(self, "Exp")
            self.rngTTF.avg=self.AvailabilityMTTF
            self.rngTTR=RandomNumberGenerator(self, "Erlang")
            self.rngTTR.alpha=self.alpha
            self.rngTTR.beta=self.beta       
        else:   
            # --------------------------------------------------------------
            #               if the distribution is fixed
            # --------------------------------------------------------------
            self.rngTTF=RandomNumberGenerator(self, self.distType)
            self.rngTTF.mean=self.MTTF
            self.rngTTR=RandomNumberGenerator(self, self.distType)
            self.rngTTR.mean=self.MTTR
        # flag used to identify if the time between failures should be counted while the victim is off-shift
        self.offshift=offshift

    def initialize(self):
        ObjectInterruption.initialize(self)
        self.victimStartsProcess=self.env.event()
        self.victimEndsProcess=self.env.event()       
        
    # =======================================================================
    #    The run method for the failure which has to served by a repairman
    # =======================================================================
    def run(self):     
        while 1:
            # if the time that the victim is off-shift should not be counted
            timeToFailure=self.rngTTF.generateNumber()
            remainingTimeToFailure=timeToFailure
            failureNotTriggered=True
            
            # if time to failure counts not matter the state of the victim
            if self.deteriorationType=='constant':
                yield self.env.timeout(remainingTimeToFailure)
            # if time to failure counts only in onShift time
            elif self.deteriorationType=='onShift':
                while failureNotTriggered:
                    timeRestartedCounting=self.env.now
                    self.isWaitingForVictimOffShift=True                   
                    receivedEvent=yield self.env.timeout(remainingTimeToFailure) | self.victimOffShift 
                    # the failure should receive a signal if there is a shift-off triggered
                    if self.victimOffShift in receivedEvent:
                        assert self.victim.onShift==False, 'shiftFailure cannot recalculate TTF if the victim is onShift'
                        self.victimOffShift=self.env.event()
                        remainingTimeToFailure=remainingTimeToFailure-(self.env.now-timeRestartedCounting)   
                        # wait for the shift to start again
                        self.isWaitingForVictimonShift=True
                        yield self.victim.interruptionEnd
                        self.isWaitingForVictimonShift=False
                        self.victimOnShift=self.env.event()
                        assert self.victim.onShift==True, 'the victim of shiftFailure must be onShift to continue counting the TTF'
                    else:
                        self.isWaitingForVictimOffShift=False
                        failureNotTriggered=False
            # if time to failure counts only in working time
            elif self.deteriorationType=='working':
                # wait for victim to start process
                yield self.victimStartsProcess
                self.victimStartsProcess=self.env.event()
                while failureNotTriggered:
                    timeRestartedCounting=self.env.now
                    # wait either for the failure or end of process
                    receivedEvent=yield self.env.timeout(remainingTimeToFailure) | self.victimEndsProcess 
                    if self.victimEndsProcess in receivedEvent:
                        self.victimEndsProcess=self.env.event()
                        remainingTimeToFailure=remainingTimeToFailure-(self.env.now-timeRestartedCounting)
                        yield self.victimStartsProcess
                        # wait for victim to start again processing
                        self.victimStartsProcess=self.env.event()
                    else:
                        failureNotTriggered=False
           
           
            # interrupt the victim only if it was not previously interrupted
            if not self.victim.interruptionStart.triggered:
                self.interruptVictim()                      # interrupt the victim

            self.victim.Up=False
            self.victim.timeLastFailure=self.env.now           
            self.outputTrace("is down")
            # update the failure time
            failTime=self.env.now    
            if(self.repairman and self.repairman!="None"):     # if the failure needs a resource to be fixed, 
                                                               # the machine waits until the 
                                                               # resource is available
                
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
            
            # add the failure
            # if victim is off shift add only the fail time before the shift ended
            if not self.victim.onShift and failTime < self.victim.timeLastShiftEnded:
                self.victim.totalFailureTime+=self.victim.timeLastShiftEnded-failTime
            # if the victim was off shift since the start of the failure add nothing
            elif not self.victim.onShift and failTime >= self.victim.timeLastShiftEnded:
                pass
            # if victim was off shift in the start of the fail time, add on
            elif self.victim.onShift and failTime < self.victim.timeLastShiftStarted:
                self.victim.totalFailureTime+=self.env.now-self.victim.timeLastShiftStarted
                # this can happen only if deteriorationType is constant
                assert self.deteriorationType=='constant', 'object got failure while off-shift and deterioration type not constant' 
            else:
                self.victim.totalFailureTime+=self.env.now-failTime   
            self.reactivateVictim()                     # since repairing is over, the Machine is reactivated
            self.victim.Up=True              
            self.outputTrace("is up")
