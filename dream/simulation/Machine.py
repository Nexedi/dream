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
Models a machine that can also have failures
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold

from Failure import Failure
from CoreObject import CoreObject

from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat

#the Machine object
class Machine(CoreObject):
            
    #initialize the id the capacity, of the resource and the distribution        
    def __init__(self, id, name, capacity=1, distribution='Fixed', mean=1, stdev=0, min=0, max=10, failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None'):
        Process.__init__(self)
        self.predecessorIndex=0     #holds the index of the predecessor from which the Machine will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Machine will dispose an entity next
        self.id=id
        self.objName=name
        self.capacity=capacity      
        self.distType=distribution          #the distribution that the procTime follows      
        self.failureDistType=failureDistribution  #the distribution that the failure follows   
                    
        self.repairman=repairman         

        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=mean
        self.rng.stdev=stdev
        self.rng.min=min
        self.rng.max=max
        self.MTTF=MTTF
        self.MTTR=MTTR
        self.availability=availability        
      
        self.next=[]        #list with the next objects in the flow
        self.previous=[]    #list with the previous objects in the flow
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.previousIds=[]     #list with the ids of the previous objects in the flow
        self.type="Machine"   #String that shows the type of object
                
        #lists to hold statistics of multiple runs
        self.Failure=[]
        self.Working=[]
        self.Blockage=[]
        self.Waiting=[]

            
    def initialize(self):
        Process.__init__(self)
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
        
        #if the failure distribution for the object is fixed, activate the failure       
        if(self.failureDistType=="Fixed" or self.failureDistType=="Availability"):  
            MFailure=Failure(self,  self.failureDistType, self.MTTF, self.MTTR, self.availability, self.id, self.repairman)
            activate(MFailure,MFailure.run())

        self.Res=Resource(self.capacity)      
        
        self.predecessorIndex=0     #holds the index of the predecessor from which the Machine will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Machine will dispose an entity next
    
    #the main process of the machine
    def run(self):
        #execute all through simulation time
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the machine can accept an entity
                                                                    #and one predecessor requests it      
                                                                                          
            self.getEntity()    #get the entity from the predecessor

            self.outputTrace("got into "+self.objName)
            self.currentEntity=self.Res.activeQ[0]                 #entity is the current entity processed in Machine  
            self.timeLastEntityEntered=now()        #this holds the last time that an entity got into Machine  
            self.nameLastEntityEntered=self.currentEntity.name    #this holds the name of the last entity that got into Machine
            timeEntered=now()            
            tinMStart=self.calculateProcessingTime()         #get the processing time  
            tinM=tinMStart 
            self.processingTimeOfCurrentEntity=tinMStart                  
            interruption=False    
            processingEndedFlag=True 
            failureTime=0       
            self.downTimeInCurrentEntity=0
  
            #this loop is repeated until the processing time is expired with no failure              
            while processingEndedFlag:                         
                tBefore=now()                           
                yield hold,self,tinM          #getting processed 
                if self.interrupted():        #if a failure occurs while processing the machine is interrupted.                                                                   
                    self.outputTrace("Interrupted at "+self.objName)
                            
                    tinM=tinM-(now()-tBefore)         #the processing time left
                    if(tinM==0):           #sometimes the failure may happen exactly at the time that the processing would finish
                                                    #this may produce ina ccordance to the simul8 because in both SimPy and Simul8
                                                    #it seems to be random which happens 1st
                                                    #this should not appear often to stochastic models though where times are random
                                                    
                        interruption=True
                            
                    breakTime=now()
                    yield passivate,self    #if there is a failure in the machine it is passivated
                    self.downTimeProcessingCurrentEntity+=now()-breakTime
                    self.downTimeInCurrentEntity+=now()-breakTime
                    self.timeLastFailureEnded=now()
                    failureTime+=now()-breakTime
                    self.outputTrace("passivated in "+self.objName+" for "+str(now()-breakTime))              
                            
                else:
                    processingEndedFlag=False               #if no interruption occurred the processing in M1 is ended 
        
            self.outputTrace("ended processing in "+self.objName)  
            self.waitToDispose=True
            self.totalWorkingTime+=tinMStart   #the total processing time for this entity is what the distribution initially gave          
            self.timeLastEntityEnded=now()      #this holds the last time that an entity ended processing in Machine 
            self.nameLastEntityEnded=self.currentEntity.name  #this holds the name of the last entity that ended processing in Machine
            self.completedJobs+=1               #Machine completed one more Job
            self.downTimeProcessingCurrentEntity=0      
            reqTime=now()           #entity has ended processing in Machine and requests for the next object 
        
        
            self.downTimeInTryingToReleaseCurrentEntity=0         
            notBlockageTime=0    
                
            while 1:
                yield waituntil, self, self.ifCanDisposeOrHaveFailure       #wait until the next Object                                                                                 #is available or machine has failure
                        
                if self.Up:  #if Next object available break 
                    break
                else:       #if M1 had failure, we want to wait until it is fixed and also count the failure time. 
                    failTime=now()   
                    yield waituntil, self, self.checkIfMachineIsUp
                    failureTime+=now()-failTime      
                    self.downTimeInTryingToReleaseCurrentEntity+=now()-failTime         
                    self.downTimeInCurrentEntity+=now()-failTime        
                    self.timeLastFailureEnded=now()           
                            
            totalTime=now()-timeEntered    
            blockageTime=totalTime-(tinMStart+failureTime)
            self.totalBlockageTime+=totalTime-(tinMStart+failureTime)   #the time of blockage is derived from 
                                                                                         #the whole time in the machine
                                                                                         #minus the processing time and the failure time                        
    #checks if the machine is Up  
    def checkIfMachineIsUp(self):
        return self.Up
    
    #calculates the processing time
    def calculateProcessingTime(self):
        return self.rng.generateNumber()    #this is if we have a default processing time for all the entities
    
    #checks if the Machine can accept an entity       
    #it checks also who called it and returns TRUE only to the predecessor that will give the entity.  
    def canAccept(self, callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        
        #if we have only one predecessor just check if there is a place and the machine is up
        if(len(activeObject.previous)==1 or callerObject==None):      
            return activeObject.Up and len(activeObjectQueue)==0
        
        #if the machine is busy return False immediately
        if len(activeObjectQueue)==activeObject.capacity:
            return False
                      
        thecaller=callerObject
        
        return len(activeObjectQueue)<self.capacity and (thecaller is giverObject)  
    
    #checks if the Machine can accept an entity and there is an entity in some predecessor waiting for it
    #also updates the predecessorIndex to the one that is to be taken
    def canAcceptAndIsRequested(self):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
                
        #if we have only one predecessor just check if there is a place, the machine is up and the predecessor has an entity to dispose
        if(len(activeObject.previous)==1):
            return activeObject.Up and len(activeObjectQueue)==0 and giverObject.haveToDispose(activeObject) 
        
        isRequested=False
        maxTimeWaiting=0
        
        #loop through the predecessors to see which have to dispose and which is the one blocked for longer
        i=0
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject)):
                isRequested=True               
                if(object.downTimeInTryingToReleaseCurrentEntity>0):
                    timeWaiting=now()-object.timeLastFailureEnded
                else:
                    timeWaiting=now()-object.timeLastEntityEnded
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.predecessorIndex=i  
                    maxTimeWaiting=timeWaiting    
            i+=1                                 
        return len(activeObjectQueue)<activeObject.capacity and isRequested               
    
    #checks if the machine down or it can dispose the object
    def ifCanDisposeOrHaveFailure(self):
         return self.Up==False or self.next[0].canAccept(self) or len(self.Res.activeQ)==0  #the last part is added so that it is not removed and stack
                                                                                        #gotta think of it again    
  
    #removes an entity from the Machine
    def removeEntity(self):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()        
        
        activeObject.timeLastEntityLeft=now()
        activeObject.outputTrace("releases "+activeObject.objName)
        activeObject.waitToDispose=False                           
        activeObjectQueue.pop(0)        #remove the Entity from the activeQ
        activeObject.downTimeInTryingToReleaseCurrentEntity=0 
           
     
    #checks if the Machine can dispose an entity to the following object     
    def haveToDispose(self, callerObject=None): 
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()    
        
        #if we have only one successor just check if machine waits to dispose and also is up        
        if(len(activeObject.next)==1 or callerObject==None):
            return len(activeObjectQueue)>0 and activeObject.waitToDispose and activeObject.Up
        
        #if the Machine is empty it returns false right away
        if(len(activeObjectQueue)==0):
            return False
   
        thecaller=callerObject
        
        #give the entity to the successor that is waiting for the most time. 
        #(plant simulation does not do this in every occasion!)       
        maxTimeWaiting=0      
        i=0
        for object in activeObject.next:
            if(object.canAccept(activeObject)):
                timeWaiting=now()-object.timeLastEntityLeft
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                    maxTimeWaiting=timeWaiting
                    activeObject.successorIndex=i     
            i+=1 
              
        receiverObject=activeObject.getReceiverObject()
        return len(activeObjectQueue)>0 and activeObject.waitToDispose and activeObject.Up and (thecaller is receiverObject)       
    
    
   #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        alreadyAdded=False      #a flag that shows if the blockage time has already been added
        
        #checks all the successors. If no one can accept an Entity then the machine might be blocked
        mightBeBlocked=True
        for nextObject in self.next:
            if nextObject.canAccept():
                mightBeBlocked=False
           
        #if there is an entity that finished processing in a Machine but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Machine
        #we should exclude the failure time in current entity though!
        #if (len(self.Res.activeQ)>0) and (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):       
        if (len(activeObjectQueue)>0) and (mightBeBlocked) and ((activeObject.nameLastEntityEntered == activeObject.nameLastEntityEnded)):
            activeObject.totalBlockageTime+=now()-(activeObject.timeLastEntityEnded+activeObject.downTimeInTryingToReleaseCurrentEntity)
            if activeObject.Up==False:
                activeObject.totalBlockageTime-=now()-activeObject.timeLastFailure
                alreadyAdded=True

        #if Machine is currently processing an entity we should count this working time    
        if(len(activeObject.Res.activeQ)>0) and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered)):           
            #if Machine is down we should add this last failure time to the time that it has been down in current entity 
            if(len(activeObjectQueue)>0) and (self.Up==False):                         
                activeObject.downTimeProcessingCurrentEntity+=now()-activeObject.timeLastFailure             
            activeObject.totalWorkingTime+=now()-activeObject.timeLastEntityEntered-activeObject.downTimeProcessingCurrentEntity 

        #if Machine is down we have to add this failure time to its total failure time
        #we also need to add the last blocking time to total blockage time     
        if(activeObject.Up==False):
            activeObject.totalFailureTime+=now()-activeObject.timeLastFailure
            #we add the value only if it hasn't already been added
            #if((len(self.next[0].Res.activeQ)>0) and (self.nameLastEntityEnded==self.nameLastEntityEntered) and (not alreadyAdded)):
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(now()-activeObject.timeLastEntityEnded)-(now()-activeObject.timeLastFailure)-activeObject.downTimeInTryingToReleaseCurrentEntity 

        #Machine was idle when it was not in any other state    
        activeObject.totalWaitingTime=MaxSimtime-activeObject.totalWorkingTime-activeObject.totalBlockageTime-activeObject.totalFailureTime   
        
        if activeObject.totalBlockageTime<0 and activeObject.totalBlockageTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalBlockageTime=0  
         
        if activeObject.totalWaitingTime<0 and activeObject.totalWaitingTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalWaitingTime=0  
            
        activeObject.Failure.append(100*self.totalFailureTime/MaxSimtime)    
        activeObject.Blockage.append(100*self.totalBlockageTime/MaxSimtime)  
        activeObject.Waiting.append(100*self.totalWaitingTime/MaxSimtime)    
        activeObject.Working.append(100*self.totalWorkingTime/MaxSimtime)  
    
    #outputs message to the trace.xls. Format is (Simulation Time | Entity Name | message)
    def outputTrace(self, message):
        from Globals import G
        if(G.trace=="Yes"):         #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,self.Res.activeQ[0].name)
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1       #increment the row

            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)    
                
    #outputs the the "output.xls"
    def outputResultsXL(self, MaxSimtime):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel    
            G.outputSheet.write(G.outputIndex,0, "The percentage of Failure of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalFailureTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Working of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWorkingTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Blockage of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalBlockageTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Waiting of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWaitingTime/MaxSimtime)
            G.outputIndex+=1       
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value    
            
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Failure of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Failure):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][1])
            else:     
                G.outputSheet.write(G.outputIndex,1,self.Failure[0])
                G.outputSheet.write(G.outputIndex,2,self.Failure[0])
                G.outputSheet.write(G.outputIndex,3,self.Failure[0])            
            
            G.outputIndex+=1  
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Working of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Working):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Working[0])
                G.outputSheet.write(G.outputIndex,2,self.Working[0])
                G.outputSheet.write(G.outputIndex,3,self.Working[0])                           
            
            G.outputIndex+=1  
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Blockage of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Blockage):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Blockage[0])
                G.outputSheet.write(G.outputIndex,2,self.Blockage[0])
                G.outputSheet.write(G.outputIndex,3,self.Blockage[0])                    
            
            G.outputIndex+=1               
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Waiting):        
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][1])   
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Waiting[0])
                G.outputSheet.write(G.outputIndex,2,self.Waiting[0])
                G.outputSheet.write(G.outputIndex,3,self.Waiting[0])                            
            G.outputIndex+=1    
        G.outputIndex+=1    
        
    #outputs results to JSON File
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            json={}
            json['_class'] = 'Dream.Machine';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['failure_ratio']=100*self.totalFailureTime/G.maxSimTime
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['blockage_ratio']=100*self.totalBlockageTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
        else: #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value           
            json={}
            json['_class'] = 'Dream.Machine';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['failure_ratio']={}
            if self.checkIfArrayHasDifValues(self.Failure):
                json['results']['failure_ratio']['min']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][0]
                json['results']['failure_ratio']['avg']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][0]
                json['results']['failure_ratio']['max']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][1]
            else:
                json['results']['failure_ratio']['min']=self.Failure[0]
                json['results']['failure_ratio']['avg']=self.Failure[0]
                json['results']['failure_ratio']['max']=self.Failure[0] 
            json['results']['working_ratio']={}
            if self.checkIfArrayHasDifValues(self.Working):
                json['results']['working_ratio']['min']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0]
                json['results']['working_ratio']['avg']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0]
                json['results']['working_ratio']['max']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1]
            else:
                json['results']['working_ratio']['min']=self.Working[0]
                json['results']['working_ratio']['avg']=self.Working[0]
                json['results']['working_ratio']['max']=self.Working[0]   
            json['results']['blockage_ratio']={}
            if self.checkIfArrayHasDifValues(self.Blockage):
                json['results']['blockage_ratio']['min']=stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][0]
                json['results']['blockage_ratio']['avg']=stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][0]
                json['results']['blockage_ratio']['max']=stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][1]
            else:
                json['results']['blockage_ratio']['min']=self.Blockage[0]
                json['results']['blockage_ratio']['avg']=self.Blockage[0]
                json['results']['blockage_ratio']['max']=self.Blockage[0]                 
            json['results']['waiting_ratio']={}
            if self.checkIfArrayHasDifValues(self.Waiting):
                json['results']['waiting_ratio']['min']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][0]
                json['results']['waiting_ratio']['avg']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][0]
                json['results']['waiting_ratio']['max']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][1]
            else:
                json['results']['waiting_ratio']['min']=self.Waiting[0]
                json['results']['waiting_ratio']['avg']=self.Waiting[0]
                json['results']['waiting_ratio']['max']=self.Waiting[0] 
                
        G.outputJSON['elementList'].append(json)
    