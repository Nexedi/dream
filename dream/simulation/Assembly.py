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
Created on 18 Feb 2013

@author: George
'''
'''
Models an assembly object 
it gathers frames and parts which are loaded to the frames
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import waituntil, now, hold
import xlwt
from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat
from CoreObject import CoreObject

#the Assembly object
class Assembly(CoreObject):

    #initialize the object      
    def __init__(self, id, name, distribution='Fixed', mean=1, stdev=0.1, min=0, max=5):
        CoreObject.__init__(self)
        self.id=id
        self.objName=name
        self.type="Assembly"   #String that shows the type of object
        self.distType=distribution          #the distribution that the procTime follows  
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=mean
        self.rng.stdev=stdev
        self.rng.min=min
        self.rng.max=max                    
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
        
         # ============================== variable that is used for the loading of machines =============
        self.exitAssignedToReceiver = False             # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 

    def initialize(self):
        Process.__init__(self)
        CoreObject.initialize(self)
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
                                                                    #and one "frame" giver requests it 
            self.getEntity("Frame")                                 #get the Frame
                                                                    
            for i in range(self.getActiveObjectQueue()[0].capacity):         #this loop will be carried until the Frame is full with the parts
                yield waituntil, self, self.isRequestedFromPart     #wait until a part is requesting for the assembly
                self.getEntity("Part")
               
            self.outputTrace(self.getActiveObjectQueue()[0].name, "is now full in "+ self.objName)               
            
            self.timeLastFrameWasFull=now()
            self.nameLastFrameWasFull=self.getActiveObjectQueue()[0].name    
                
            startWorkingTime=now()
            self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()   
            yield hold,self,self.totalProcessingTimeInCurrentEntity   #hold for the time the assembly operation is carried    
            self.totalWorkingTime+=now()-startWorkingTime
            
            self.outputTrace(self.getActiveObjectQueue()[0].name, "ended processing in " + self.objName)
            self.timeLastEntityEnded=now()
            self.nameLastEntityEnded=self.getActiveObjectQueue()[0].name
            
            startBlockageTime=now()
            self.completedJobs+=1                       #Assembly completed a job            
            self.waitToDispose=True                     #since all the frame is full
            while 1:
                yield waituntil, self, self.next[0].canAccept       #wait until the next object is free
                if self.next[0].getGiverObject()==self:                         #if the free object can accept from this Assembly
                                                                                #break. Else continue
                    break
            #self.totalBlockageTime+=now()-startBlockageTime     #add the blockage time
            
  
    #checks if the Assembly can accept an entity 
    def canAccept(self, callerObject=None):
        return len(self.getActiveObjectQueue())==0  
            
    #checks if the Assembly can accept an entity and there is a Frame waiting for it
    def canAcceptAndIsRequested(self):
        activeObjectQueue=self.getActiveObjectQueue()

        #loop through the possible givers
        for object in self.previous:
            #activate only if the possible giver is not empty
            if(len(object.getActiveObjectQueue())>0):
                #activate only if the caller carries Frame
                if(object.getActiveObjectQueue()[0].type=='Frame'):
                    #update the giver
                    self.giver=object
                    return len(activeObjectQueue)==0 and object.haveToDispose(self)
        return False    
    
    #checks if the Assembly can accept an entity and there is a Frame waiting for it
    def isRequestedFromPart(self):
        activeObjectQueue=self.getActiveObjectQueue()

        #loop through the possible givers
        for object in self.previous:
            #activate only if the possible giver is not empty
            if(len(object.getActiveObjectQueue())>0):
                #activate only if the caller carries Part
                if(object.getActiveObjectQueue()[0].type=='Part'):
                    #update giver
                    self.giver=object
                    return len(activeObjectQueue)==1 and object.haveToDispose(self)
        return False 

    #checks if the Assembly can dispose an entity to the following object     
    def haveToDispose(self, callerObject=None): 
        return len(self.getActiveObjectQueue())>0 and self.waitToDispose                                  
                                               
    #removes an entity from the Assembly
    def removeEntity(self, entity=None):
        activeEntity=CoreObject.removeEntity(self, entity)               #run the default method     
        self.waitToDispose=False  
        return activeEntity                                              #the object does not wait to dispose now
    
    #gets an entity from the giver   
    #it may handle both Parts and Frames  
    def getEntity(self, type):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        giverObject.sortEntities()      #sort the Entities of the giver according to the scheduling rule if applied
        giverObjectQueue=self.getGiverObjectQueue()
        activeEntity=giverObjectQueue[0]
        
        if(type=="Part"):
            activeObjectQueue[0].getFrameQueue().append(activeEntity)    #get the part from the giver and append it to the frame!
            giverObject.removeEntity(activeEntity)     #remove the part from the previews object
            self.outputTrace(activeEntity.name, "got into "+ self.objName)                       
        elif(type=="Frame"):
            activeObjectQueue.append(giverObjectQueue[0])    #get the frame from the giver
            giverObject.removeEntity(activeEntity)   #remove the frame from the previews object
            self.outputTrace(activeEntity.name, "got into "+ self.objName)
            self.nameLastEntityEntered=activeEntity.name  
            self.timeLastEntityEntered=now()
        activeEntity.currentStation=self
        return activeEntity   
      
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime=None):
        
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime
        activeObjectQueue=self.getActiveObjectQueue()
        
        #checks all the successors. If no one can accept an Entity then the machine might be blocked
        mightBeBlocked=True
        for nextObject in self.next:
            if nextObject.canAccept():
                mightBeBlocked=False
        
        #if there is an entity that finished processing in Assembly but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Assembly
        if (mightBeBlocked) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):              
            self.totalBlockageTime+=now()-self.timeLastEntityEnded       

        #if Assembly is currently processing an entity we should count this working time    
        if(len(activeObjectQueue)>0) and (not (self.nameLastEntityEnded==self.nameLastFrameWasFull)):              
            self.totalWorkingTime+=now()-self.timeLastFrameWasFull
        
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime-self.totalBlockageTime 
        
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)
        self.Blockage.append(100*self.totalBlockageTime/MaxSimtime)
    
    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
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
                