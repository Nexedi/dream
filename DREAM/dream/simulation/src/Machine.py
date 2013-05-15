'''
Created on 8 Nov 2012

@author: George
'''
'''
Models a machine that can also have failures
'''

from SimPy.Simulation import *
from Failure import Failure
import xlwt
import xlrd
from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat

#the Machine object
class Machine(Process):
            
    #initialize the id the capacity, of the resource and the distribution        
    def __init__(self, id, name, capacity, dist, time, fDist, MTTF, MTTR, availability, repairman):
        Process.__init__(self)
        self.id=id
        self.objName=name
        self.capacity=capacity      
        self.distType=dist          #the distribution that the procTime follows      
        self.failureDistType=fDist  #the distribution that the failure follows   
                    
        self.repairman=repairman         
        #self.xls = xlwt.Workbook()     #create excel file     
        #self.sheet = self.xls.add_sheet('sheet ', cell_overwrite_ok=True)  #create excel sheet
        #self.xlindex=0
        
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
        
        self.timeLastEntityEnded=0      #holds the last time that an entity ended processing in the machine
        self.nameLastEntityEnded=""     #holds the name of the last entity that ended processing in the machine
        self.timeLastEntityEntered=0    #holds the last time that an entity entered in the machine
        self.nameLastEntityEntered=""   #holds the name of the last entity that entered in the machine
        self.timeLastFailure=0          #holds the time that the last failure of the machine started
        self.timeLastFailureEnded=0          #holds the time that the last failure of the machine Ended
        self.downTimeProcessingCurrentEntity=0  #holds the time that the machine was down while processing the current entity
        self.downTimeInTryingToReleaseCurrentEntity=0 #holds the time that the machine was down while trying 
                                                      #to release the current entity  
        self.downTimeInCurrentEntity=0                  #holds the total time that the machine was down while holding current entity
        self.timeLastEntityLeft=0        #holds the last time that an entity left the machine
                                                
        self.processingTimeOfCurrentEntity=0        #holds the total processing time that the current entity required                                               
                                                      
        self.waitToDispose=False    #shows if the machine waits to dispose an entity       
        
        #if the failure distribution for the machine is fixed, activate the failure       
        if(self.failureDistType=="Fixed" or self.failureDistType=="Availability"):  
            MFailure=Failure(self,  self.failureDistType, self.MTTF, self.MTTR, self.availability, self.id, self.repairman)
            activate(MFailure,MFailure.Run())

        self.Res=Resource(self.capacity)      
    
    #the main process of the machine
    def Run(self):
        #execute all through simulation time
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the machine can accept an entity
                                                                    #and one predecessor requests it      
                                                                                          
            self.getEntity()    #get the entity from the predecessor
            #self.previous[0].removeEntity()

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
            
    #sets the routing in and out elements for the queue
    def defineRouting(self, p, n):
        self.next=n
        self.previous=p

    #checks if the waitQ of the machine is empty
    def checkIfWaitQEmpty(self):
        return len(self.M.waitQ)==0
 
    #checks if the activeQ of the machine is empty   
    def checkIfActiveQEmpty(self):     
        return len(self.M.activeQ)==0      
    
    #checks if the machine is Up  
    def checkIfMachineIsUp(self):
        return self.Up
    
    #checks if the machine can accept an entity 
    def canAccept(self):
        return self.Up and len(self.Res.activeQ)==0
    
    #checks if the machine can accept an entity and there is an entity waiting for it
    def canAcceptAndIsRequested(self):
        return self.Up and len(self.Res.activeQ)==0 and self.previous[0].haveToDispose()      
    
    #checks if the machine down or it can dispose the object
    def ifCanDisposeOrHaveFailure(self):
         return self.Up==False or self.next[0].canAccept() or len(self.Res.activeQ)==0  #the last part is added so that it is not removed and stack
                                                                                        #gotta think of it again    
     
    #checks if the Machine can dispose an entity to the following object     
    def haveToDispose(self): 
        return len(self.Res.activeQ)>0 and self.waitToDispose and self.Up
    
    #removes an entity from the Machine
    def removeEntity(self):
        #the time of blockage is derived from the whole time in the machine minus the processing time and the failure time 
        #self.totalBlockageTime+=(now()-self.timeLastEntityEntered)-(self.processingTimeOfCurrentEntity+self.downTimeInCurrentEntity)        
        #print (now()-self.timeLastEntityEntered)-(self.processingTimeOfCurrentEntity+self.downTimeInCurrentEntity)
        #print self.downTimeInCurrentEntity
        self.timeLastEntityLeft=now()
        self.outputTrace("releases "+self.objName)
        self.waitToDispose=False                 
        self.Res.activeQ.pop(0)   
        self.downTimeInTryingToReleaseCurrentEntity=0          
        #self.outputTrace("got blocked in M"+str(self.id)+" for "
        #                                     +str(self.totalBlockageTime))
        
    #gets an entity from the predecessor     
    def getEntity(self):
        self.Res.activeQ.append(self.previous[0].Res.activeQ[0])    #get the entity from the predecessor
        self.previous[0].removeEntity()
    
    
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):

        alreadyAdded=False      #a flag that shows if the blockage time has already been added
        
        #if there is an entity that finished processing in a Machine but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Machine
        #we should exclude the failure time in current entity though!
        if (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):              
            self.totalBlockageTime+=now()-(self.timeLastEntityEnded+self.downTimeInTryingToReleaseCurrentEntity)
            #X=now()-(self.timeLastEntityEnded+self.downTimeInTryingToReleaseCurrentEntity)
            if self.Up==False:
                self.totalBlockageTime-=now()-self.timeLastFailure
                #X-=now()-self.timeLastFailure
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
        
    #takes the array and checks if all its values are identical (returns false) or not (returns true) 
    #needed because if somebody runs multiple runs in deterministic case it would crash!          
    def checkIfArrayHasDifValues(self, array):
        difValuesFlag=False 
        for i in range(1, len(array)):
           if(array[i]!=array[1]):
               difValuesFlag=True
        return difValuesFlag  