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
import sys

#the Machine object
class Machine(CoreObject):
            
    #initialize the id the capacity, of the resource and the distribution        
    def __init__(self, id, name, capacity, dist, time, fDist, MTTF, MTTR, availability, repairman):
        Process.__init__(self)
        self.predecessorIndex=0     #holds the index of the predecessor from which the Machine will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Machine will dispose an entity next
        self.id=id
        self.objName=name
        self.capacity=capacity      
        self.distType=dist          #the distribution that the procTime follows      
        self.failureDistType=fDist  #the distribution that the failure follows   
                    
        self.repairman=repairman         

        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=time[0]
        self.rng.stdev=time[1]
        self.rng.min=time[2]
        self.rng.max=time[3]
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
            tinMStart=self.rng.generateNumber()         #get the processing time  
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
    #checks if the waitQ of the machine is empty
    def checkIfWaitQEmpty(self):
        return len(self.M.waitQ)==0
 
    #checks if the activeQ of the machine is empty   
    def checkIfActiveQEmpty(self):     
        return len(self.M.activeQ)==0      
    
    #checks if the machine is Up  
    def checkIfMachineIsUp(self):
        return self.Up
    
    #checks if the Machine can accept an entity       
    #it checks also who called it and returns TRUE only to the predecessor that will give the entity.  
    def canAccept(self):
        #if we have only one predecessor just check if there is a place and the machine is up
        if(len(self.previous)==1):      
            return self.Up and len(self.Res.activeQ)==0
        
        #if the machine is busy return False immediately
        if len(self.Res.activeQ)==self.capacity:
            return False
         
        #identify the caller method 
        frame = sys._getframe(1)
        arguments = frame.f_code.co_argcount
        if arguments == 0:
            print "Not called from a method"
            return
        caller_calls_self = frame.f_code.co_varnames[0]
        thecaller = frame.f_locals[caller_calls_self]
        
        #return true only to the predecessor from which the queue will take 
        flag=False
        if thecaller is self.previous[self.predecessorIndex]:
            flag=True
        return len(self.Res.activeQ)<self.capacity and flag  
    
    #checks if the Machine can accept an entity and there is an entity in some predecessor waiting for it
    #also updates the predecessorIndex to the one that is to be taken
    def canAcceptAndIsRequested(self):
        #if we have only one predecessor just check if there is a place, the machine is up and the predecessor has an entity to dispose
        if(len(self.previous)==1):
            return self.Up and len(self.Res.activeQ)==0 and self.previous[0].haveToDispose() 
        
        isRequested=False
        maxTimeWaiting=0
        
        #loop through the predecessors to see which have to dispose and which is the one blocked for longer
        for i in range(len(self.previous)):
            if(self.previous[i].haveToDispose()):
                isRequested=True               
                if(self.previous[i].downTimeInTryingToReleaseCurrentEntity>0):
                    timeWaiting=now()-self.previous[i].timeLastFailureEnded
                else:
                    timeWaiting=now()-self.previous[i].timeLastEntityEnded
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    self.predecessorIndex=i  
                    maxTimeWaiting=timeWaiting                                     
        return len(self.Res.activeQ)<self.capacity and isRequested               
    
    #checks if the machine down or it can dispose the object
    def ifCanDisposeOrHaveFailure(self):
         return self.Up==False or self.next[0].canAccept() or len(self.Res.activeQ)==0  #the last part is added so that it is not removed and stack
                                                                                        #gotta think of it again    
  
    #removes an entity from the Machine
    def removeEntity(self):
        self.timeLastEntityLeft=now()
        self.outputTrace("releases "+self.objName)
        self.waitToDispose=False                 
        self.Res.activeQ.pop(0)   
        self.downTimeInTryingToReleaseCurrentEntity=0    
     
    #checks if the Machine can dispose an entity to the following object     
    def haveToDispose(self): 
        #if we have only one successor just check if machine waits to dispose and also is up        
        if(len(self.next)==1):
            return len(self.Res.activeQ)>0 and self.waitToDispose and self.Up
        
        #if the Machine is empty it returns false right away
        if(len(self.Res.activeQ)==0):
            return False
   
        #identify the caller method
        frame = sys._getframe(1)
        arguments = frame.f_code.co_argcount
        if arguments == 0:
            print "Not called from a method"
            return
        caller_calls_self = frame.f_code.co_varnames[0]
        thecaller = frame.f_locals[caller_calls_self]
               
        #give the entity to the successor that is waiting for the most time. 
        #plant does not do this in every occasion!       
        maxTimeWaiting=0      
        for i in range(len(self.next)):
            if(self.next[i].canAccept()):
                timeWaiting=now()-self.next[i].timeLastEntityLeft
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                    maxTimeWaiting=timeWaiting
                    self.successorIndex=i      
              
        #return true only to the predecessor from which the queue will take 
        flag=False
        if thecaller is self.next[self.successorIndex]:
            flag=True
        return len(self.Res.activeQ)>0 and self.waitToDispose and self.Up and flag       
    
    
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):

        alreadyAdded=False      #a flag that shows if the blockage time has already been added
        
        #if there is an entity that finished processing in a Machine but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Machine
        #we should exclude the failure time in current entity though!
        if (len(self.Res.activeQ)>0) and (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):       
            self.totalBlockageTime+=now()-(self.timeLastEntityEnded+self.downTimeInTryingToReleaseCurrentEntity)
            if self.Up==False:
                self.totalBlockageTime-=now()-self.timeLastFailure
                alreadyAdded=True

        #if Machine is currently processing an entity we should count this working time    
        if(len(self.Res.activeQ)>0) and (not (self.nameLastEntityEnded==self.nameLastEntityEntered)):              
            #if Machine is down we should add this last failure time to the time that it has been down in current entity 
            if(len(self.Res.activeQ)>0) and (self.Up==False):                         
                self.downTimeProcessingCurrentEntity+=now()-self.timeLastFailure             
            self.totalWorkingTime+=now()-self.timeLastEntityEntered-self.downTimeProcessingCurrentEntity 

        #if Machine is down we have to add this failure time to its total failure time
        #we also need to add the last blocking time to total blockage time     
        if(self.Up==False):
            self.totalFailureTime+=now()-self.timeLastFailure
            #we add the value only if it hasn't already been added
            if((len(self.next[0].Res.activeQ)>0) and (self.nameLastEntityEnded==self.nameLastEntityEntered) and (not alreadyAdded)):
                #self.totalBlockageTime+=self.timeLastFailure-self.timeLastEntityEnded 
                self.totalBlockageTime+=(now()-self.timeLastEntityEnded)-(now()-self.timeLastFailure)-self.downTimeInTryingToReleaseCurrentEntity 

        #Machine was idle when it was not in any other state    
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime-self.totalBlockageTime-self.totalFailureTime   
        
        if self.totalBlockageTime<0 and self.totalBlockageTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalBlockageTime=0  
         
        if self.totalWaitingTime<0 and self.totalWaitingTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalWaitingTime=0  
            
        self.Failure.append(100*self.totalFailureTime/MaxSimtime)    
        self.Blockage.append(100*self.totalBlockageTime/MaxSimtime)  
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)    
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)  
    
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
    