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

from SimPy.Simulation import now, Process, hold, request, release, infinity
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

class ScheduledMaintenance(ObjectInterruption):
    def __init__(self, victim=None, start=0, duration=1):
        ObjectInterruption.__init__(self,victim)
        self.start=start
        self.duration=duration
        
            
    def run(self):
        yield hold,self,self.start      #wait until the start time
        try:
            if(len(self.getVictimQueue())>0):           # when a Machine gets failure
                self.interruptVictim()                  # while in process it is interrupted
            self.victim.Up=False
            self.victim.timeLastFailure=now()           
            self.outputTrace("is down")
        except AttributeError:
            print "AttributeError1"
            
        yield hold,self,self.duration      #wait until the start time
        self.victim.totalFailureTime+=self.duration
        
        try:
            if(len(self.getVictimQueue())>0):                
                self.reactivateVictim()                 # since the maintenance is over, the victim is reactivated
            self.victim.Up=True              
            self.outputTrace("is up")                                           
        except AttributeError:
            print "AttributeError2"    
        

        