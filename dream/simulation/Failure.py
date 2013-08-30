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

from SimPy.Simulation import *
import math
from RandomNumberGenerator import RandomNumberGenerator
from ObjectInterruption import ObjectInterruption

class Failure(ObjectInterruption):
    
    def __init__(self, victim, dist, MTTF, MTTR, availability, index, repairman):
        Process.__init__(self)
        self.distType=dist      #the distribution that the failure duration follows
        self.MTTF=MTTF          #the MTTF
        self.MTTR=MTTR          #the MTTR
        self.availability=availability    #the availability  
        self.victim=victim      #the victim of the failure (work center)
        self.name="F"+str(index)
        self.repairman=repairman    #the resource that may be needed to fix the failure
                                    #if now resource is needed this will be "None" 
        self.type="Failure"
        self.id=0

        if(self.distType=="Availability"):      
            
            #the following are used if we have availability defined (as in plant)
            #the erlang is a special case of Gamma. 
            #To model the Mu and sigma that is given in plant as alpha and beta for gamma you should do the following:
            #beta=(sigma^2)/Mu    
            #alpha=Mu/beta    
            self.AvailabilityMTTF=MTTR*(float(availability)/100)/(1-(float(availability)/100))
            self.sigma=0.707106781185547*MTTR   
            self.theta=(pow(self.sigma,2))/float(MTTR)             
            self.beta=self.theta
            self.alpha=(float(MTTR)/self.theta)        

                
            self.rngTTF=RandomNumberGenerator(self, "Exp")
            self.rngTTF.avg=self.AvailabilityMTTF
            self.rngTTR=RandomNumberGenerator(self, "Erlang")
            self.rngTTR.alpha=self.alpha
            self.rngTTR.beta=self.beta       
        else:   #if the distribution is fixed
            self.rngTTF=RandomNumberGenerator(self, self.distType)
            self.rngTTF.avg=MTTF            
            self.rngTTR=RandomNumberGenerator(self, self.distType)
            self.rngTTR.avg=MTTR
        
    def run(self):           
        while 1:
            yield hold,self,self.rngTTF.generateNumber()    #wait until a failure happens                  
            try:
                if(len(self.victim.Res.activeQ)>0):
                    self.interrupt(self.victim)       #when a Machine gets failure while in process it is interrupted
                self.victim.Up=False
                self.victim.timeLastFailure=now()           
                self.outputTrace("is down")

            except AttributeError:
                print "AttributeError1"
                
                
            failTime=now()            
            if(self.repairman!="None"):     #if the failure needs a resource to be fixed, the machine waits until the 
                                            #resource is available
                yield request,self,self.repairman.Res
                timeRepairStarted=now()
                self.repairman.timeLastRepairStarted=now()
                                
            yield hold,self,self.rngTTR.generateNumber()    #wait until the repairing process is over
            self.victim.totalFailureTime+=now()-failTime    
            
            try:
                if(len(self.victim.Res.activeQ)>0):                
                    reactivate(self.victim)   #since repairing is over, the Machine is reactivated
                self.victim.Up=True              
                self.outputTrace("is up")              
                if(self.repairman!="None"): #if a resource was used, it is now released
                    yield release,self,self.repairman.Res 
                    self.repairman.totalWorkingTime+=now()-timeRepairStarted                                
            except AttributeError:
                print "AttributeError2"    
           
    #outputs message to the trace.xls. Format is (Simulation Time | Machine Name | message)            
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

