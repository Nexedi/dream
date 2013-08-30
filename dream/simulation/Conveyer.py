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
Created on 23 May 2013

@author: George
'''
'''
Models a conveyer object 
it gathers entities and transfers them with a certain speed
'''

from SimPy.Simulation import *
import xlwt
import scipy.stats as stat
from CoreObject import CoreObject

#The conveyer object
class Conveyer(CoreObject):    
          
    def __init__(self, id, name,length,speed):
        self.id=id        
        self.objName=name
        self.type="Conveyer"
        self.speed=speed    #the speed of the conveyer in m/sec
        self.length=length  #the length of the conveyer in meters
        self.previous=[]    #list with the previous objects in the flow
        self.next=[]    #list with the next objects in the flow
        self.nextIds=[]     #list with the ids of the next objects in the flow. For the exit it is always empty!
        self.previousIds=[]     #list with the ids of the previous objects in the flow

        #lists to hold statistics of multiple runs
        self.Waiting=[]
        self.Working=[]
        self.Blockage=[]
        
    def initialize(self):
        Process.__init__(self)
        self.Res=Resource(capacity=infinity)         
        
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
        self.position=[]            #list that shows the position of the corresponding element in the conveyer
        self.timeLastMoveHappened=0   #holds the last time that the move was performed (in reality it is 
                                        #continued, in simulation we have to handle it as discrete)
                                        #so when a move is performed we can calculate where the entities should go
        self.timeToReachEnd=0           #if the conveyer has entities but none has reached the end of it, this calculates
                                        #the time when the first entity will reach the end and so it will be ready to be disposed
        self.timeToBecomeAvailable=0    #if the conveyer has entities on its back this holds the time that it will be again free
                                        #for an entity. of course this also depends on the length of the entity who requests it
        self.conveyerMover=ConveyerMover(self)      #process that is triggered at the times when an entity reached the end or
                                                    #a place is freed. It performs the move at this point, 
                                                    #so if there are actions to be carried they will
        self.call=False                             #flag that shows if the ConveyerMover should be triggered
        self.entityLastReachedEnd=None              #the entity that last reached the end of the conveyer
        self.timeBlockageStarted=now()              #the time that the conveyer reached the blocked state
                                                    #plant considers the conveyer blocked even if it can accept just one entity
                                                    #I think this is false 
        self.wasFull=False                          #flag that shows if the conveyer was full. So when an entity is disposed
                                                    #if this is true we count the blockage time and set it to false
        self.currentRequestedLength=0               #the length of the entity that last requested the conveyer
        self.currentAvailableLength=self.length     #the available length in the end of the conveyer
        
        
    def run(self):
        #these are just for the first Entity
        activate(self.conveyerMover,self.conveyerMover.run())
        yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity                                                             #and one predecessor requests it  
        self.getEntity()                                        #get the entity 
        self.timeLastMoveHappened=now()                         
         
        while 1:
            #calculate the time to reach end. If this is greater than 0 (we did not already have an entity at the end)
            #set it as the timeToWait of the conveyerMover and raise call=true so that it will be triggered 
            self.timeToReachEnd=0
            if(len(self.position)>0 and (not self.length-self.position[0]<0.000001)):
                self.timeToReachEnd=((self.length-self.position[0])/float(self.speed))/60                       
            if self.timeToReachEnd>0:
                self.conveyerMover.timeToWait=self.timeToReachEnd
                self.call=True
            
            #wait until the conveyer is in state to receive or dispose one entity
            yield waituntil, self, self.canAcceptAndIsRequestedORwaitToDispose     #wait for an important event in order to move the items
            if self.canAcceptAndIsRequested():
                self.getEntity()              
            if self.waitToDispose:
                pass

    #moves the entities in the line    
    #also counts the time the move required to assign it as working time
    def moveEntities(self):
        interval=now()-self.timeLastMoveHappened
        interval=(float(interval))*60.0     #the simulation time that passed since the last move was taken care
        moveTime1=0
        moveTime2=0
        #for the first entity
        if len(self.position)>0:
            if self.position[0]!=self.length:
                #if it does not reach the end of conveyer move it according to speed
                if self.position[0]+interval*self.speed<self.length:
                    moveTime1=interval
                    self.position[0]=self.position[0]+interval*self.speed
                #else move it to the end of conveyer
                else:
                    moveTime1=(self.length-self.position[0])/self.speed
                    self.position[0]=self.length
                    self.entityLastReachedEnd=self.Res.activeQ[0]
                    self.timeLastEntityReachedEnd=now()
        #for the other entities        
        for i in range(1,len(self.Res.activeQ)):
            #if it does not reach the preceding entity move it according to speed
            if self.position[i]+interval*self.speed<self.position[i-1]-self.Res.activeQ[i].length:
                moveTime2=interval
                self.position[i]=self.position[i]+interval*self.speed
            #else move it right before the preceding entity
            else:
                mTime=(self.position[i-1]-self.Res.activeQ[i].length-self.position[i])/self.speed
                if mTime>moveTime2:
                    moveTime2=mTime
                self.position[i]=self.position[i-1]-self.Res.activeQ[i-1].length
        self.timeLastMoveHappened=now()     #assign this time as the time of last move
        self.totalWorkingTime+=max(moveTime1/60.0, moveTime2/60.0)  #all the time of moving (the max since things move in parallel)
                                                                    #is considered as working time

    #checks if the Conveyer can accept an entity 
    def canAccept(self):
        #if there is no object in the predecessor just return false and set the current requested length to zero
        if len(self.previous[0].Res.activeQ)==0:
            self.currentRequestedLength=0
            return False
        
        requestedLength=self.previous[0].Res.activeQ[0].length      #read what length the entity has
        self.moveEntities()                                         #move the entities so that the available length can be calculated
        #in plant an entity can be accepted even if the available length is exactly zero
        #eg if the conveyer has 8m length and the entities 1m length it can have up to 9 entities.
        #i do not know if this is good but I kept is
        if len(self.Res.activeQ)==0:
            availableLength=self.length
        else:
            availableLength=self.position[-1]
            
        self.currentAvailableLength=availableLength
        self.currentRequestedLength=requestedLength    
        #if requestedLength<=availableLength:
        if availableLength-requestedLength>-0.00000001:
            return True
        else:       
            return False
        
    #checks if the Conveyer can accept an entity and there is a Frame waiting for it
    def canAcceptAndIsRequested(self):
        return self.canAccept() and self.previous[0].haveToDispose()

    #gets an entity from the predecessor     
    def getEntity(self): 
        self.Res.activeQ.append(self.previous[0].Res.activeQ[0])    #get the entity from the predecessor
        self.position.append(0)           #the entity is placed in the start of the conveyer
        self.previous[0].removeEntity()            #remove the entity from the previous object
        self.outputTrace(self.Res.activeQ[-1].name, "got into "+ self.objName) 
        #check if the conveyer became full to start counting blockage 
        if self.isFull():
            self.timeBlockageStarted=now()
            self.wasFull=True

    #removes an entity from the Conveyer
    def removeEntity(self):
        self.outputTrace(self.Res.activeQ[0].name, "releases "+ self.objName)              
        self.Res.activeQ.pop(0) 
        self.position.pop(0)
        self.waitToDispose=False  
        #if the conveyer was full, it means that it also was blocked
        #we count this blockage time 
        if self.wasFull:
            self.totalBlockageTime+=now()-self.timeBlockageStarted
            self.wasFull=False
            #calculate the time that the conveyer will become available again and trigger the conveyerMover
            self.timeToBecomeAvailable=((self.position[-1]+self.currentRequestedLength)/float(self.speed))/60 
            self.conveyerMover.timeToWait=self.timeToBecomeAvailable
            self.call=True
    
    #checks if the Conveyer can dispose an entity to the following object     
    def haveToDispose(self): 
        #it has meaning only if there are one or more entities in the conveyer
        if len(self.position)>0:
            return len(self.Res.activeQ)>0 and self.length-self.position[0]<0.000001    #the conveyer can dispose an object 
                                                                                        #only when an entity is at the end of it         
        else:
            return False

    #checks if the conveyer is full to count the blockage. for some reason Plant regards 
    #the conveyer full even when it has one place    
    def isFull(self):
        totalLength=0  
        for i in range(len(self.Res.activeQ)):
            totalLength+=self.Res.activeQ[i].length
        return self.length<totalLength
    
    #checks if the Mover shoul be called so that the move is performed
    def callMover(self):
        return self.call  
      
    #checks if the conveyer is ready to receive or dispose an entity  
    def canAcceptAndIsRequestedORwaitToDispose(self):
        if(len(self.position)>0):           
            if(self.length-self.position[0]<0.000001) and (not self.entityLastReachedEnd==self.Res.activeQ[0]):
                self.waitToDispose=True
                self.entityLastReachedEnd=self.Res.activeQ[0]
                return True
            else:
                return self.canAcceptAndIsRequested()
        else:
            return self.canAcceptAndIsRequested()
    
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):                      
        self.moveEntities()     #move the entities to count the working time
        #if the conveyer is full count the blockage time
        if self.isFull():
            self.totalBlockageTime+=now()-self.timeBlockageStarted+0.1

        #when the conveyer was nor working or blocked it was waiting
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime-self.totalBlockageTime 

        #update the lists to hold data for multiple runs
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)
        self.Blockage.append(100*self.totalBlockageTime/MaxSimtime)
        
    #outputs message to the trace.xls. Format is (Simulation Time | Entity or Frame Name | message)
    def outputTrace(self, name, message):
        from Globals import G
        if(G.trace=="Yes"):         #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,name)  
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1       #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)    


    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            G.outputSheet.write(G.outputIndex,0, "The percentage of Working of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWorkingTime/MaxSimtime)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The percentage of Blockage of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalBlockageTime/MaxSimtime)
            G.outputIndex+=1   
            G.outputSheet.write(G.outputIndex,0, "The percentage of Waiting of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWaitingTime/MaxSimtime)
            G.outputIndex+=1   
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value                 
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Working of "+self.objName +" is:")
            if self.checkIfArrayHasDifValues(self.Working): 
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1])  
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Working[0])
                G.outputSheet.write(G.outputIndex,2,self.Working[0])
                G.outputSheet.write(G.outputIndex,3,self.Working[0])          
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Blockage of "+self.objName +" is:")            
            if self.checkIfArrayHasDifValues(self.Blockage):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Blockage[0])
                G.outputSheet.write(G.outputIndex,2,self.Blockage[0])
                G.outputSheet.write(G.outputIndex,3,self.Blockage[0]) 
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+self.objName +" is:")            
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
            json['_class'] = 'Dream.Conveyer';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['blockage_ratio']=100*self.totalBlockageTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
        else: #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value           
            json={}
            json['_class'] = 'Dream.Conveyer';
            json['id'] = str(self.id)
            json['results'] = {}
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
    
#Process that handles the moves of the conveyer
class ConveyerMover(Process):
    def __init__(self, conveyer):
        Process.__init__(self)
        self.conveyer=conveyer      #the conveyer that owns the mover
        self.timeToWait=0           #the time to wait every time. This is calculated by the conveyer and corresponds
                                    #either to the time that one entity reaches the end or the time that one space is freed
    
    def run(self):
        while 1:
            yield waituntil,self,self.conveyer.callMover    #wait until the conveyer triggers the mover
            yield hold,self,self.timeToWait                 #wait for the time that the conveyer calculated
            self.conveyer.moveEntities()                    #move the entities of the conveyer
            self.conveyer.call=False                        #reset call so it will be triggered only when it is needed again
            

    