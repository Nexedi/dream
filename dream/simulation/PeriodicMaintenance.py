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
Created on 16 Nov 2014

@author: George
'''

'''
A maintenance happens periodically. The change from failure is that it works in an endUnfinished fashion,
i.e. if the victim is processing when it happens it would first end the processing and then start the maintenance 
'''

import simpy
import math
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

class PeriodicMaintenance(ObjectInterruption):
    
    def __init__(self, id='',name='',victim=None, distribution=None, index=0, repairman=None,**kw):
        ObjectInterruption.__init__(self,id,name,victim=victim)
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
        self.type="PeriodicMaintenance"
        
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
            
            yield self.env.timeout(remainingTimeToFailure)
 
            if self.victim.isProcessing:
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
           
            # interrupt the victim
            self.interruptVictim()                      # interrupt the victim
            
            # check in the ObjectInterruptions of the victim. If there is a one that is waiting for victimFailed send it
            for oi in self.victim.objectInterruptions:
                if oi.expectedSignals['victimFailed']:
                    self.sendSignal(receiver=oi, signal=oi.victimFailed)
            self.victim.Up=False
            self.victim.timeLastFailure=self.env.now           
            self.outputTrace(self.victim.name,"is down")
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
                    self.outputTrace(self.victim.name,"is up")
                    
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
            self.outputTrace(self.victim.name,"is up")
