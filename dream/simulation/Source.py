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
Created on 8 Nov 2012

@author: George
'''

'''
models the source object that generates the entities
'''

from SimPy.Simulation import *
from Part import Part
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject

#The Source object is a Process
class Source(CoreObject): 
    def __init__(self, id, name, dist, time, item):
        Process.__init__(self)
        self.id=id   
        self.objName=name   
        self.distType=dist      #label that sets the distribution type
        self.interArrivalTime=time     #the mean interarrival time 
        self.totalInterArrivalTime=0    #the total interarrival time 
        self.numberOfArrivals=0         #the number of entities that were created 
        self.next=[]        #list with the next objects in the flow
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.previousIds=[]     #list with the ids of the previous objects in the flow. For the source it is always empty!
        
        self.type="Source"   #String that shows the type of object
        #self.waitToDispose=False
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=time
        self.item=item      #the type of object that the Source will generate
        
        #self.Res=Resource(capacity=infinity) 
        
    def initialize(self):
        Process.__init__(self) 
        self.Res=Resource(capacity=infinity)    
        self.Res.activeQ=[]  
        self.Res.waitQ=[]       
        
        self.Up=True                    #Boolean that shows if the object is in failure ("Down") or not ("up")
        self.currentEntity=None      
          
        self.totalBlockageTime=0        #holds the total blockage time
        self.totalFailureTime=0         #holds the total failure time
        self.totalWaitingTime=0         #holds the total waiting time
        self.totalWorkingTime=0         #holds the total working time
        self.completedJobs=0            #holds the number of completed jobs 
        
        self.timeLastEntityEnded=0      #holds the last time that an entity ended processing in the object
        self.nameLastEntityEnded=""     #holds the name of the last entity that ended processing in the object
        self.timeLastEntityEntered=0    #holds the last time that an entity entered in the object
        self.nameLastEntityEntered=""   #holds the name of the last entity that entered in the object
        self.timeLastFailure=0          #holds the time that the last failure of the object started
        self.timeLastFailureEnded=0          #holds the time that the last failure of the object Ended
        self.downTimeProcessingCurrentEntity=0  #holds the time that the object was down while processing the current entity
        self.downTimeInTryingToReleaseCurrentEntity=0 #holds the time that the object was down while trying 
                                                      #to release the current entity  
        self.downTimeInCurrentEntity=0                  #holds the total time that the object was down while holding current entity
        self.timeLastEntityLeft=0        #holds the last time that an entity left the object
                                                
        self.processingTimeOfCurrentEntity=0        #holds the total processing time that the current entity required                                               
                                                      
        self.waitToDispose=False    #shows if the object waits to dispose an entity   
        
    def run(self):
        i=0
        if(self.distType=="Fixed"): #if the distribution type is fixed
            from Globals import G            
            while 1:
                #self.waitToDispose=True
                self.numberOfArrivals+=1           #we have one new arrival     
                #entity=Entity("Ent"+str(i))        
                entity=self.item(self.item.type+"_"+self.objName+"_"+str(i)) #create the Entity object and assign its name 
                entity.creationTime=now()          #assign the current simulation time as the Entity's creation time 
                entity.startTime=now()             #assign the current simulation time as the Entity's start time 
                self.outputTrace(self.item.type+"_"+self.objName+"_"+str(i))     #output the trace
                self.Res.activeQ.append(entity)    #append the entity to the resource 
                i+=1        
                #yield hold,self,self.interArrivalTime       #one entity at every interArrivalTime   
                yield hold,self,self.rng.generateNumber()
        elif(self.distType=="Exp"): #if the distribution type is exponential
            from Globals import G
            while 1:
                #self.waitToDispose=True                
                self.numberOfArrivals+=1        #we have one new arrival
                #entity=Entity("Ent"+str(i))     #create the Entity object and assign its name 
                entity=self.item(self.item.type+str(i)) #create the Entity object and assign its name                 
                entity.creationTime=now()          #assign the current simulation time as the Entity's creation time
                entity.startTime=now()             #assign the current simulation time as the Entity's start time 
                self.outputTrace(self.item.type+str(i))      #output the trace
                i+=1
                self.Res.activeQ.append(entity)     #append the entity to the resource           
                timeTillNextArrival=G.Rnd.expovariate(1.0/(self.interArrivalTime))  #create a random number that follows the     
                                                                                    #exponential distribution                                                  
                #yield hold,self,timeTillNextArrival       #one entity at every interArrivalTime   
                yield hold,self,self.rng.generateNumber()
                self.totalInterArrivalTime+=timeTillNextArrival                                                
        else:   #if the distribution type is something else it is an error
            print "Distribution Error in Source "+str(self.id)   
            
    #sets the routing out element for the Source
    def defineRouting(self, n):
        self.next=n  
            
   #outputs message to the trace.xls. Format is (Simulation Time | Entity Name | "generated")            
    def outputTrace(self, message):
        from Globals import G
        
        if(G.trace=="Yes"):     #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,message)
            G.traceSheet.write(G.traceIndex,2,"generated")          
            G.traceIndex+=1      #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)     
