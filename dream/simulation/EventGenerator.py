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
Created on 4 Dec 2013

@author: George
'''

'''
models a generator that runs a method at specified intervals
'''

from SimPy.Simulation import now, hold, Process
from ObjectInterruption import ObjectInterruption

class EventGenerator(ObjectInterruption):
    def __init__(self, id=id, name=None, start=None, stop=None, interval=None,
                 duration=None, method=None, argumentDict=None, **kw):
        ObjectInterruption.__init__(self)
        self.id=id
        self.name=name
        self.start=start                #the time that the generator will be activated for the first time
        self.stop=stop                  #the time that the generator will stop to trigger events
        self.interval=interval          #the interval that the generator sleeps
        self.duration=duration          #the duration that the generation is awake (this is not active for now)
        self.method=method              #the method to be invoked
        self.argumentDict=argumentDict  #the arguments of the method given in a dict
        
    def run(self):
        yield hold,self,self.start      #wait until the start time
        #loop until the end of the simulation
        while 1:
            #if the stop time is exceeded then break the loop
            if self.stop:
                if now()>self.stop:
                    break
            self.method(self.argumentDict)      #call the method
            yield hold,self,self.interval       #wait for the predetermined interval
        
    
    
    
