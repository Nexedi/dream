# ===========================================================================
# Copyright 2013 Georgios Dagkakis
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
Created on 18 Feb 2013

@author: George
'''


'''
Models an assembly object 
it gathers frames and parts which are loaded to the frames
'''

from SimPy.Simulation import *
import xlwt
from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat

#the Assembly object
class Assembly(Process):

    #initialize the object      
    def __init__(self, id, name, dist, time):
        Process.__init__(self)
        self.id=id
        self.objName=name
        self.type="Assembly"   #String that shows the type of object
        self.distType=dist          #the distribution that the procTime follows  
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=time[0]
        self.rng.stdev=time[1]
        self.rng.min=time[2]
        self.rng.max=time[3]                    
        self.next=[]        #list with the next objects in the flow
        self.previous=[]     #list with the previous objects in the flow
        self.previousPart=[]    #list with the previous objects that send parts
        self.previousFrame=[]    #list with the previous objects that send frames 
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.previousIds=[]   #list with the ids of the previous objects in the flow
        self.previousPartIds=[]     #list with the ids of the previous objects in the flow that bring parts  
        self.previousFrameIds=[]     #list with the ids of the previous objects in the flow that bring frames
        
        #lists to hold statistics of multiple runs
        self.Waiting=[]
        self.Working=[]
        self.Blockage=[]
        
        self.predecessorIndex=0     #holds the index of the predecessor from which the Queue will take an entity next
               

    def initialize(self):
        Process.__init__(self)
        self.waitToDispose=False    #flag that shows if the object waits to dispose an entity    
        
        self.Up=True                    #Boolean that shows if the object is in failure ("Down") or not ("up")
        self.currentEntity=None      
          
        self.totalFailureTime=0         #holds the total failure time
        self.timeLastFailure=0          #holds the time that the last failure of the object started
        self.timeLastFailureEnded=0          #holds the time that the last failure of the object Ended
        self.downTimeProcessingCurrentEntity=0  #holds the time that the object was down while processing the current entity
        self.downTimeInTryingToReleaseCurrentEntity=0 #holds the time that the object was down while trying 
                                                      #to release the current entity  
        self.downTimeInCurrentEntity=0                  #holds the total time that the object was down while holding current entity
        self.timeLastEntityLeft=0        #holds the last time that an entity left the object
                                                
        self.processingTimeOfCurrentEntity=0        #holds the total processing time that the current entity required                                               
                                                      

        
        self.totalBlockageTime=0        #holds the total blockage time
        self.totalWaitingTime=0         #holds the total waiting time
        self.totalWorkingTime=0         #holds the total working time
        self.completedJobs=0            #holds the number of completed jobs   
        
        self.timeLastEntityEnded=0      #holds the last time that an entity ended processing in the object     
        self.timeLastEntityEntered=0      #holds the last time that an entity ended processing in the object   
        self.timeLastFrameWasFull=0     #holds the time that the last frame was full, ie that assembly process started  
        self.nameLastFrameWasFull=""    #holds the name of the last frame that was full, ie that assembly process started
        self.nameLastEntityEntered=""   #holds the name of the last frame that entered processing in the object
        self.nameLastEntityEnded=""     #holds the name of the last frame that ended processing in the object            
        self.Res=Resource(1)    
        self.Res.activeQ=[]  
        self.Res.waitQ=[]  
    
    
    def run(self):
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Assembly can accept a frame
                                                                    #and one "frame" predecessor requests it 
            self.getEntity("Frame")                                 #get the Frame
                                                                    
            for i in range(self.Res.activeQ[0].numOfParts):         #this loop will be carried until the Frame is full with the parts
                yield waituntil, self, self.isRequestedFromPart     #wait until a part is requesting for the assembly
                self.getEntity("Part")
               
            self.outputTrace(self.Res.activeQ[0].name, "is now full in "+ self.objName)               
            
            self.timeLastFrameWasFull=now()
            self.nameLastFrameWasFull=self.Res.activeQ[0].name    
                
            startWorkingTime=now()    
            yield hold,self,self.rng.generateNumber()   #hold for the time the assembly operation is carried    
            self.totalWorkingTime+=now()-startWorkingTime
            
            self.outputTrace(self.Res.activeQ[0].name, "ended processing in " + self.objName)
            self.timeLastEntityEnded=now()
            self.nameLastEntityEnded=self.Res.activeQ[0].name
            
            startBlockageTime=now()
            self.completedJobs+=1                       #Assembly completed a job            
            self.waitToDispose=True                     #since all the frame is full
            yield waituntil, self, self.next[0].canAccept       #wait until the next object is free
            self.totalBlockageTime+=now()-startBlockageTime     #add the blockage time
            
  
    #checks if the Assembly can accept an entity 
    def canAccept(self):
        return len(self.Res.activeQ)==0  
            
    #checks if the Assembly can accept an entity and there is a Frame waiting for it
    def canAcceptAndIsRequested(self):
        i=0
        #loop through the predecessors
        for coreObject in self.previous:
            #activate only if the predecessor is not empty
            if(len(coreObject.Res.activeQ)>0):
                #activate only if the caller carries Frame
                if(coreObject.Res.activeQ[0].type=='Frame'):
                    #update the predecessorIndex
                    self.predecessorIndex=i
                    return len(self.Res.activeQ)==0 and coreObject.haveToDispose()
            i=i+1 
        return False    
    
    #checks if the Assembly can accept an entity and there is a Frame waiting for it
    def isRequestedFromPart(self):
        i=0
        #loop through the predecessors
        for coreObject in self.previous:
            #activate only if the predecessor is not empty
            if(len(coreObject.Res.activeQ)>0):
                #activate only if the caller carries Part
                if(coreObject.Res.activeQ[0].type=='Part'):
                    #update the predecessorIndex
                    self.predecessorIndex=i
                    return len(self.Res.activeQ)==1 and coreObject.haveToDispose()
            i=i+1 
        return False 

        #activate only if the caller is not empty
        if(len(thecaller.Res.activeQ)>0):
            #activate only if the caller carries Part
            if(thecaller.Res.activeQ[0].type=='Part'):
                #update the predecessorIndex
                i=0
                for coreObject in self.previous:
                    if coreObject is thecaller:
                        self.predecessorIndex=i
                        i=i+1
                return len(self.Res.activeQ)==1 and thecaller.haveToDispose() 
        return False  
    
    #checks if the Assembly can dispose an entity to the following object     
    def haveToDispose(self): 
        return len(self.Res.activeQ)>0 and self.waitToDispose                                  
                                            
    #sets the routing in and out elements for the Assembly
    def defineRouting(self, p, n):
        self.next=n
        self.previous=p
    
    #removes an entity from the Assembly
    def removeEntity(self):
        self.outputTrace(self.Res.activeQ[0].name, "releases "+ self.objName)              
        self.Res.activeQ.pop(0)   
        self.waitToDispose=False

    
    #gets an entity from the predecessor   
    #it may handle both Parts and Frames  
    def getEntity(self, type):
        if(type=="Part"):
            self.Res.activeQ[0].Res.activeQ.append(self.previous[self.predecessorIndex].Res.activeQ[0])    #get the part from the predecessor and append it to the frame!
            self.previous[self.predecessorIndex].removeEntity()     #remove the part from the previews object
            self.outputTrace(self.Res.activeQ[0].Res.activeQ[-1].name, "got into "+ self.objName)                       
        elif(type=="Frame"):
            self.Res.activeQ.append(self.previous[self.predecessorIndex].Res.activeQ[0])    #get the frame from the predecessor
            self.previous[self.predecessorIndex].removeEntity()   #remove the frame from the previews object
            self.outputTrace(self.Res.activeQ[0].name, "got into "+ self.objName)
            self.nameLastEntityEntered=self.Res.activeQ[0].name  
            self.timeLastEntityEntered=now()
      
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        
        #if there is an entity that finished processing in Assembly but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Assembly
        if (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):              
            self.totalBlockageTime+=now()-self.timeLastEntityEnded       

        #if Assembly is currently processing an entity we should count this working time    
        if(len(self.Res.activeQ)>0) and (not (self.nameLastEntityEnded==self.nameLastFrameWasFull)):              
            self.totalWorkingTime+=now()-self.timeLastFrameWasFull
        
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime-self.totalBlockageTime 
        
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
            json['_class'] = 'Dream.Assembly';
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
            json['_class'] = 'Dream.Assembly';
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
                

        
    #takes the array and checks if all its values are identical (returns false) or not (returns true) 
    #needed because if somebody runs multiple runs in deterministic case it would crash!          
    def checkIfArrayHasDifValues(self, array):
        difValuesFlag=False 
        for i in range(1, len(array)):
           if(array[i]!=array[1]):
               difValuesFlag=True
        return difValuesFlag     
