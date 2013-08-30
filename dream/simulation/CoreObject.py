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
Created on 12 Jul 2012

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All the core-objects should inherit from it
'''

from SimPy.Simulation import Process, Resource

#the core object
class CoreObject(Process):
    
    def initilize(self):
        Process.__init__(self) 
        self.predecessorIndex=0     #holds the index of the predecessor from which the Machine will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Machine will dispose an entity next
        self.Up=True                    #Boolean that shows if the machine is in failure ("Down") or not ("up")
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
        self.downTimeProcessingCurrentEntity=0  #holds the time that the machine was down while processing the current entity
        self.downTimeInTryingToReleaseCurrentEntity=0 #holds the time that the object was down while trying 
                                                      #to release the current entity  
        self.downTimeInCurrentEntity=0                  #holds the total time that the object was down while holding current entity
        self.timeLastEntityLeft=0        #holds the last time that an entity left the object
                                                
        self.processingTimeOfCurrentEntity=0        #holds the total processing time that the current entity required                                               
                                                      
        self.waitToDispose=False    #shows if the object waits to dispose an entity   


    #the main process of the core object
    #this is dummy, every object must have its own implementation
    def run(self):
        raise NotImplementedError("Subclass must define 'run' method")
        
    #sets the routing in and out elements for the Object
    def defineRouting(self, p, n):
        self.next=n
        self.previous=p

    #removes an entity from the Object
    def removeEntity(self):     
        self.Res.activeQ.pop(0)          
        
    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):
        self.Res.activeQ=[self.previous[self.predecessorIndex].Res.activeQ[0]]+self.Res.activeQ   #get the entity from the previous object
                                                                                                      #and put it in front of the activeQ       
        self.previous[self.predecessorIndex].removeEntity()                                           #remove the entity from the previous object  
        
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        pass    
    
    #outputs message to the trace.xls
    def outputTrace(self, message):
        pass
    
    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime):
        pass
    
    #outputs results to JSON File
    def outputResultsJSON(self):
        pass
    
    #checks if the Object can dispose an entity to the following object     
    def haveToDispose(self): 
        return len(self.Res.activeQ)>0
    
    #checks if the Object can accept an entity and there is an entity in some predecessor waiting for it
    def canAcceptAndIsRequested(self):
        pass
    
    #checks if the Object can accept an entity       
    def canAccept(self): 
        pass
    
    #takes the array and checks if all its values are identical (returns false) or not (returns true) 
    #needed because if somebody runs multiple runs in deterministic case it would crash!          
    def checkIfArrayHasDifValues(self, array):
        difValuesFlag=False 
        for i in range(1, len(array)):
           if(array[i]!=array[1]):
               difValuesFlag=True
        return difValuesFlag 