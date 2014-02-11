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

from SimPy.Simulation import now, Process, hold, request, release, infinity
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

# ===========================================================================
# the shift scheduler class
# ===========================================================================
class ShiftScheduler(ObjectInterruption):

    # =======================================================================
    # the __init__() method of the class
    # =======================================================================
    def __init__(self, victim=None, shiftPattern=[], endUnfinished=False):
        ObjectInterruption.__init__(self,victim)
        self.type='ShiftScheduler'
        self.shiftPattern=shiftPattern
        self.endUnfinished=endUnfinished    #flag that shows if half processed Jobs should end after the shift ends
        
    
    
    # =======================================================================
    # initialize for every replications
    # =======================================================================
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.remainingShiftPattern=list(self.shiftPattern) 
        
    # =======================================================================
    #    The run method for the failure which has to served by a repairman
    # =======================================================================
    def run(self):    
        self.victim.totalOffShiftTime=0
        self.victim.timeLastShiftEnded=now()
        self.victim.onShift=False
        while 1:
            yield hold,self,float(self.remainingShiftPattern[0][0]-now())    # wait for the onShift                  
            if(len(self.getVictimQueue())>0 and self.victim.interruptCause and not(self.endUnfinished)):
                self.reactivateVictim()                 # re-activate the victim in case it was interrupted
            
            self.victim.totalOffShiftTime+=now()-self.victim.timeLastShiftEnded
            self.victim.onShift=True
            self.victim.timeLastShiftStarted=now()           
            self.outputTrace("is on shift")
            startShift=now()            
            
            yield hold,self,float(self.remainingShiftPattern[0][1]-now())    # wait until the shift is over
        
            if(len(self.getVictimQueue())>0 and not(self.endUnfinished)):            
                self.interruptVictim()                  # interrupt processing operations if any
            self.victim.onShift=False                        # get the victim off-shift
            self.victim.timeLastShiftEnded=now()              
            self.outputTrace("is off shift")              
            
            self.remainingShiftPattern.pop(0)
            if len(self.remainingShiftPattern)==0:
                break
