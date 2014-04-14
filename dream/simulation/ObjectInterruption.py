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
Created on 18 Aug 2013

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All object interruptions (eg failures, breaks) should inherit from it
'''

from SimPy.Simulation import Process, Resource, reactivate, now

#===============================================================================
# The ObjectInterruption process
#===============================================================================
class ObjectInterruption(Process):
    
    def __init__(self, victim=None):
        Process.__init__(self)
        self.victim=victim
        # variable used to hand in control to the objectInterruption
        self.call=False
    
    def initialize(self):
#         Process.__init__(self)
        self.call=False
    
    #===========================================================================
    # the main process of the core object
    # this is dummy, every object must have its own implementation
    #===========================================================================
    def run(self):
        raise NotImplementedError("Subclass must define 'run' method")
    
    # =======================================================================
    #           hand in the control to the objectIterruption.run
    #                   to be called by the machine
    # =======================================================================    
    def invoke(self):
        self.call=True
    
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exit(self):
        self.call=False
    
    # =======================================================================
    #                        call the objectInterruption 
    #        filter for object interruption - yield waituntil isCalled
    # =======================================================================
    def isCalled(self):
        return self.call
    
    # =======================================================================
    #        the objectIterruption returns control to machine.Run
    #        filter for Machine - yield request/release operator
    # =======================================================================
    def isSet(self):
        return not self.call
    
    #===========================================================================
    # outputs data to "output.xls"
    #===========================================================================
    def outputTrace(self, message):
        pass
    
    #===========================================================================
    # returns the internal queue of the victim
    #===========================================================================
    def getVictimQueue(self):
        return self.victim.getActiveObjectQueue()
    
    #===========================================================================
    # actions to be performed after the end of the simulation
    #===========================================================================
    def postProcessing(self):
        pass
    
    #===========================================================================
    # interrupts the victim
    #===========================================================================
    def interruptVictim(self):
        # if the victim is not in position to dispose an entity, then interrupt the processing
        if not self.victim.waitToDispose and self.victim.getActiveObjectQueue():
            self.interrupt(self.victim)
        # otherwise it waits for an interruption event
        else:
            self.victim.interruptionStart.signal(now()) 
    
    #===========================================================================
    # reactivate the victim
    #===========================================================================
    def reactivateVictim(self):
        self.victim.interruptionEnd.signal(self.victim)
#         reactivate(self.victim)  
        
    #===========================================================================
    # outputs message to the trace.xls. Format is (Simulation Time | Victim Name | message)            
    #===========================================================================
    def outputTrace(self, message):
        from Globals import G  
        if(G.trace=="Yes"):     #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1, self.victim.objName)
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1      #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)
        