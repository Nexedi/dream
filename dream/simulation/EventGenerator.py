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

# from SimPy.Simulation import now, hold, Process
import simpy
from ObjectInterruption import ObjectInterruption

class EventGenerator(ObjectInterruption):
    def __init__(self, id=id, name=None, start=0, stop=float('inf'), interval=1,
                 duration=0, method=None, argumentDict={}, **kw):
        ObjectInterruption.__init__(self)
        self.id=id
        self.name=name
        self.start=float(start)                #the time that the generator will be activated for the first time
        self.stop=float(stop)                  #the time that the generator will stop to trigger events
        # negative stop means infinity
        if self.stop<0:
            self.stop=float('inf') 
        self.interval=float(interval)          #the interval that the generator sleeps
        self.duration=float(duration)          #the duration that the generation is awake (this is not active for now)
        self.method=method              #the method to be invoke       
        self.argumentDict=argumentDict
        # if the argumentDict is passed as string convert it to dict
        if isinstance(self.argumentDict, basestring):
            import ast
            self.argumentDict=ast.literal_eval(self.argumentDict)
        from Globals import G
        G.EventGeneratorList.append(self)
        self.method=method
        if isinstance(method, basestring):
            import Globals
            self.method=Globals.getMethodFromName(method)
            
    def run(self):
        yield self.env.timeout(self.start)              #wait until the start time
        #loop until the end of the simulation
        while 1:
            #if the stop time is exceeded then break the loop
            if self.stop:
                if self.env.now>self.stop:
                    break
            import inspect
            # if the method is generator yield it
            if inspect.isgeneratorfunction(self.method):
                yield self.env.process(self.method(**self.argumentDict))     
            # else just call the method
            else:
                self.method(**self.argumentDict)
            # wait for the predetermined interval
            yield self.env.timeout(self.interval)                
        
    
    
    
