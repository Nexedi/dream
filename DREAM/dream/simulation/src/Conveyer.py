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

#The conveyer object
class Conveyer(Process):    
          
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
                                        #continues, in simulation we have to handle it as discrete)
        self.justDisposed=False
        self.timeToReachEnd=0
        self.timeToBecomeAvailable=0
        self.justReachedEnd=False
        self.conveyerMover=ConveyerMover(self)
        self.call=False
        self.entityLastReachedEnd=None
        self.timeBlockageStarted=now()
        self.wasFull=False
        self.lastLengthRequested=0
        self.currenRequestedLength=0
        self.currentAvailableLength=self.length
        
        
    def run(self):
        #these are just for the first Entity
        activate(self.conveyerMover,self.conveyerMover.run())
        yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity                                                             #and one predecessor requests it  
        self.getEntity()                                        #get the entity 
        self.timeLastMoveHappened=now()
         
        while 1:
            self.timeToReachEnd=0
            #self.timeToBecomeAvailable=0
            if(len(self.position)>0 and (not self.length-self.position[0]<0.000001)):
                self.timeToReachEnd=((self.length-self.position[0])/float(self.speed))/60                       
            #if len(self.position)>0 and self.currentAvailableLength<=self.currenRequestedLength:
            #    self.timeToBecomeAvailable=((self.position[-1]+self.currenRequestedLength)/float(self.speed))/60 
            
            #print now(), self.timeToReachEnd,self.timeToBecomeAvailable  
            if self.timeToReachEnd>0:
                self.conveyerMover.timeToWait=self.timeToReachEnd
                self.call=True
            '''if max(self.timeToReachEnd,self.timeToBecomeAvailable)>0.0000001:       
                if self.timeToReachEnd<0.0000001:
                    self.conveyerMover.timeToWait=self.timeToBecomeAvailable
                elif self.timeToBecomeAvailable<0.0000001:
                    self.conveyerMover.timeToWait=self.timeToReachEnd
                else:                
                    self.conveyerMover.timeToWait=min(self.timeToReachEnd,self.timeToBecomeAvailable) 
                self.call=True
                #print self.conveyerMover.timeToWait'''
            
            yield waituntil, self, self.somethingHappened     #wait for an important event in order to move the items
            #print now(), "something happened in run"
            if self.canAcceptAndIsRequested():
                self.getEntity()              
            if self.waitToDispose:
                yield waituntil, self, self.entityJustDisposed
                self.justDisposed=False

            '''
            now we have to wait until something happens. The things that are important are (may be not a full list)
            one item reaches the end
            one item is received
            one predecessor requests to dispose
            one item is disposed
            '''

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
        self.timeLastMoveHappened=now()   
        self.totalWorkingTime+=max(moveTime1/60.0, moveTime2/60.0)

    #checks if the Conveyer can accept an entity 
    def canAccept(self):
        #if there is no object in the predecessor just return false
        if len(self.previous[0].Res.activeQ)==0:
            self.currenRequestedLength=0
            return False
        
        interval=now()-self.timeLastMoveHappened
        interval=(float(interval))*60.0     #the simulation time that passed since the last move was taken care
        requestedLength=self.previous[0].Res.activeQ[0].length      #read what length the entity has
        '''
        if len(self.Res.activeQ)==0:
            availableLength=self.length                             #if the conveyer is empty it is all available
        elif len(self.Res.activeQ)==1:
            if self.position[0]+interval*self.speed<self.length:          
                availableLength=self.length-self.Res.activeQ[0].length   #else calculate what length is available at the end of the line
            else:
                availableLength=self.position[0]+interval*self.speed-self.Res.activeQ[0].length   #else calculate what length is available at the end of the line
        else:
            if self.position[-1]+interval*self.speed<self.position[-2]-self.Res.activeQ[-1].length:
                availableLength=(self.position[-1]+interval*self.speed)-self.Res.activeQ[-1].length
            else:
                availableLength=(self.position[-2]-self.Res.activeQ[-2].length)-self.Res.activeQ[-1].length
        print now(), requestedLength, availableLength
        '''
        self.moveEntities()
        if len(self.Res.activeQ)==0:
            availableLength=self.length
        else:
            availableLength=self.position[-1]
            
        self.currentAvailableLength=availableLength
        self.currenRequestedLength=requestedLength    
        #print availableLength
        if requestedLength<=availableLength:
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
        #self.position.append(self.previous[0].Res.activeQ[0].length)  
        self.previous[0].removeEntity()            #remove the entity from the previous object
        self.outputTrace(self.Res.activeQ[-1].name, "got into "+ self.objName)  
        if self.isFull():
            self.timeBlockageStarted=now()
            self.wasFull=True

    #removes an entity from the Conveyer
    def removeEntity(self):
        self.outputTrace(self.Res.activeQ[0].name, "releases "+ self.objName)              
        self.Res.activeQ.pop(0) 
        self.position.pop(0)
        self.justDisposed=True
        self.waitToDispose=False   
        if self.wasFull:
            self.totalBlockageTime+=now()-self.timeBlockageStarted
            #print now(), "adding to blockage", now()-self.timeBlockageStarted
            self.wasFull=False
            self.timeToBecomeAvailable=((self.position[-1]+self.currenRequestedLength)/float(self.speed))/60 
            self.conveyerMover.timeToWait=self.timeToBecomeAvailable
            self.call=True
    
    #checks if the Conveyer can dispose an entity to the following object     
    def haveToDispose(self): 
        if len(self.position)>0:
            return len(self.Res.activeQ)>0 and self.length-self.position[0]<0.000001    #the conveyer can dispose an object only when an entity is at the end of it         
        else:
            return False
        
    #sets the routing in and out elements for the Conveyer
    def defineRouting(self, p, n):
        self.next=n
        self.previous=p

    #checks if the first Entity just reached the end of the conveyer
    def entityJustReachedEnd(self):
        interval=now()-self.timeLastMoveHappened
        interval=(float(interval))*60.0     #the simulation time that passed since the last move was taken care
        if(len(self.position)==0):
            return False
        if ((self.position[0]+interval*self.speed>=self.length) and (not self.position[0]==self.length)):
            self.waitToDispose=True
            return True
        else:
            return False        
    '''   
    #checks if the first one place was made available in the conveyer    
    def onePlaceJustMadeAvailable(self):
        interval=now()-self.timeLastMoveHappened
        interval=(float(interval))/60.0     #the simulation time that passed since the last move was taken care
        if self.position[0]+interval*self.speed>=self.length:
            self.waitToDispose=True
            return True
        else:
            return False   
    '''
    
    def isFull(self):
        totalLength=0  
        for i in range(len(self.Res.activeQ)):
            totalLength+=self.Res.activeQ[i].length
        return self.length<totalLength
    
    def callMover(self):
        return self.call  
      
    def somethingHappened(self):
        if(len(self.position)>0):           
            if(self.length-self.position[0]<0.000001) and (not self.entityLastReachedEnd==self.Res.activeQ[0]):
                self.waitToDispose=True
                self.entityLastReachedEnd=self.Res.activeQ[0]
                return True
            else:
                return self.canAcceptAndIsRequested()
        else:
            return self.canAcceptAndIsRequested()

    #checks if the Conveyer is requested by the predecessor
    def isRequested(self):
        return self.previous[0].haveToDispose    
    
    def entityJustDisposed(self):
        return self.justDisposed
    
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):        
        '''
        #if there is an entity that finished processing in Conveyer but did not get to reach 
        #the following Object
        #till the end of simulation, we have to add this blockage to the percentage of blockage in Assembly
        if (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):              
            self.totalBlockageTime+=now()-self.timeLastEntityEnded       

        #if Assembly is currently processing an entity we should count this working time    
        if(len(self.Res.activeQ)>0) and (not (self.nameLastEntityEnded==self.nameLastFrameWasFull)):              
            self.totalWorkingTime+=now()-self.timeLastFrameWasFull
        
        '''
        
        
        self.moveEntities()
        if self.isFull():
            #print now()-self.timeBlockageStarted
            self.totalBlockageTime+=now()-self.timeBlockageStarted+0.1


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
        

    #takes the array and checks if all its values are identical (returns false) or not (returns true) 
    #needed because if somebody runs multiple runs in deterministic case it would crash!          
    def checkIfArrayHasDifValues(self, array):
        difValuesFlag=False 
        for i in range(1, len(array)):
           if(array[i]!=array[1]):
               difValuesFlag=True
        return difValuesFlag    
    
#Process that handles the moves of the conveyer
class ConveyerMover(Process):
    def __init__(self, conveyer):
        Process.__init__(self)
        self.conveyer=conveyer
        self.timeToWait=0
    
    def run(self):
        while 1:
            yield waituntil,self,self.conveyer.callMover
            yield hold,self,self.timeToWait
            self.conveyer.moveEntities()
            self.conveyer.call=False
            

    