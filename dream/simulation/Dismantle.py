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
Created on 21 May 2013

@author: George
'''
'''
Models a dicmantle object 
it gathers frames that have parts loaded, unloads the parts and sends the frame to one destination and the parts to another
'''

from SimPy.Simulation import *
import xlwt
from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat
from CoreObject import CoreObject

#the Dismantle object
class Dismantle(CoreObject):

    #initialize the object      
    def __init__(self, id, name, dist, time):
        self.id=id
        self.objName=name
        self.type="Dismantle"   #String that shows the type of object
        self.distType=dist          #the distribution that the procTime follows  
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=time[0]
        self.rng.stdev=time[1]
        self.rng.min=time[2]
        self.rng.max=time[3]                    
        self.previous=[]        #list with the previous objects in the flow
        self.previousIds=[]     #list with the ids of the previous objects in the flow
        self.nextPart=[]    #list with the next objects that receive parts
        self.nextFrame=[]    #list with the next objects that receive frames 
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.nextPartIds=[]     #list with the ids of the next objects that receive parts 
        self.nextFrameIds=[]     #list with the ids of the next objects that receive frames 
        self.next=[]
        
        #lists to hold statistics of multiple runs
        self.Waiting=[]
        self.Working=[]
        self.Blockage=[]
        
    def initialize(self):
        Process.__init__(self)
        self.waitToDispose=False    #flag that shows if the object waits to dispose an entity    
        self.waitToDisposePart=False    #flag that shows if the object waits to dispose a part   
        self.waitToDisposeFrame=False    #flag that shows if the object waits to dispose a frame   
        
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
        self.Res=Resource(capacity=Infinity)    
        self.Res.activeQ=[]  
        self.Res.waitQ=[]     
        
        
    def run(self):
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Assembly can accept a frame
                                                                    #and one "frame" predecessor requests it   
            self.getEntity()                                 #get the Frame with the parts 
            self.timeLastEntityEntered=now()
            
            self.outputTrace(self.Res.activeQ[0].name, "got into "+ self.objName)   
            
            startWorkingTime=now()   
            yield hold,self,self.rng.generateNumber()   #hold for the time the dismantle operation is carried 
            self.totalWorkingTime+=now()-startWorkingTime
            
            self.timeLastEntityEnded=now()
                      
            startBlockageTime=now()          
            self.waitToDisposePart=True     #Dismantle is in state to dispose a part
            yield waituntil, self, self.frameIsEmpty       #wait until all the parts are disposed
            self.waitToDisposePart=False     #Dismantle has no parts now
            self.waitToDisposeFrame=True     #Dismantle is in state to dispose a part
            yield waituntil, self, self.isEmpty       #wait until all the frame is disposed            
                        
            self.completedJobs+=1                       #Dismantle completed a job            
            self.waitToDisposeFrame=False                     #the Dismantle has no Frame to dispose now
            self.totalBlockageTime+=now()-startBlockageTime     #add the blockage time
            
            
    #checks if the Dismantle can accept an entity and there is a Frame waiting for it
    def canAcceptAndIsRequested(self):
        return len(self.Res.activeQ)==0 and self.previous[0].haveToDispose()  
    
    #checks if the Dismantle can accept an entity 
    def canAccept(self):
        return len(self.Res.activeQ)==0  
            
    #defines where parts and frames go after they leave the object                          
    def definePartFrameRouting(self, np, nf):
        self.nextPart=np
        self.nextFrame=nf              

    #checks if the caller waits for a part or a frame and if the Dismantle is in the state of disposing one it returnse true     
    def haveToDispose(self): 
        #identify the caller method
        frame = sys._getframe(1)
        arguments = frame.f_code.co_argcount
        if arguments == 0:
            print "Not called from a method"
            return
        caller_calls_self = frame.f_code.co_varnames[0]
        thecaller = frame.f_locals[caller_calls_self]    
        
        #according to the caller return true or false
        if thecaller in self.nextPart:
            return len(self.Res.activeQ)>1 and self.waitToDisposePart
        elif thecaller in self.nextFrame:
            return len(self.Res.activeQ)==1 and self.waitToDisposeFrame
                 
    #checks if the frame is emptied
    def frameIsEmpty(self):
        return len(self.Res.activeQ)==1
    
    #checks if Dismantle is emptied
    def isEmpty(self):
        return len(self.Res.activeQ)==0
    
    #gets a frame from the predecessor that the predecessor index points to     
    def getEntity(self):
        self.Res.activeQ.append(self.previous[0].Res.activeQ[0])    #get the frame from the predecessor
        self.previous[0].removeEntity()
        #append also the parts in the res so that they can be popped
        for i in range(self.Res.activeQ[0].numOfParts):         
            #self.Res.activeQ.append(self.Res.activeQ[0].Res.activeQ[self.Res.activeQ[0].numOfParts-1-i])
            self.Res.activeQ.append(self.Res.activeQ[0].Res.activeQ[i])
        self.Res.activeQ[0].Res.activeQ=[]
        self.Res.activeQ.append(self.Res.activeQ[0])
        self.Res.activeQ.pop(0)        
    
    #removes an entity from the Dismantle
    def removeEntity(self):
        #to release the Frame if it is empty
        if(len(self.Res.activeQ)==1):
            self.outputTrace(self.Res.activeQ[0].name, " releases "+ self.objName)              
            self.Res.activeQ.pop(0)   
            self.waitToDisposeFrame=False
        elif(len(self.Res.activeQ)>1):
            self.outputTrace(self.Res.activeQ[0].name, " releases "+ self.objName)              
            self.Res.activeQ.pop(0)
            if(len(self.Res.activeQ)==1):   
               self.waitToDisposePart=False
                

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


    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        
        #if there is an entity that finished processing in Dismantle but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Dismantle
        if (len(self.Res.activeQ)>0) and (self.waitToDisposeFrame) or (self.waitToDisposePart):         
            self.totalBlockageTime+=now()-self.timeLastEntityEnded       
        
        #if Dismantle is currently processing an entity we should count this working time    
        if(len(self.Res.activeQ)>0) and (not ((self.waitToDisposeFrame) or (self.waitToDisposePart))):       
            self.totalWorkingTime+=now()-self.timeLastEntityEntered
        
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
        else:   #if we had multiple replications we output confidence intervals to excel
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
            json['_class'] = 'Dream.Dismantle';
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
            json['_class'] = 'Dream.Dismantle';
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
    
    