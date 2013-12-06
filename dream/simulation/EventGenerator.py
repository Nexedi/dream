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
    def __init__(self, id=id, name=None, start=None, stop=None, interval=None, duration=None, method=None, argumentDict=None):
        ObjectInterruption.__init__(self)
        self.id=id
        self.name=name
        self.start=start
        self.stop=stop
        self.interval=interval
        self.duration=duration
        self.method=method
        self.argumentDict=argumentDict
        
    def run(self):
        yield hold,self,self.start
        while 1:
            if self.stop:
                if now()>self.stop:
                    break
            self.method(self.argumentDict)
            yield hold,self,self.interval
        
    
    
    