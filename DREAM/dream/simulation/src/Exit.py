'''
Created on 6 Feb 2013

@author: George
'''
'''
models the exit of the model
'''

from SimPy.Simulation import *
import xlwt
import scipy.stats as stat

#The exit object
class Exit(Process):    
          
    def __init__(self, id, name):
        Process.__init__(self)
        self.predecessorIndex=0   #holds the index of the predecessor from which the Exit will take an entity next
        self.id=id        
        self.objName=name
        self.type="Exit"
        self.previous=[]    #list with the previous objects in the flow
        self.nextIds=[]     #list with the ids of the next objects in the flow. For the exit it is always empty!
        self.previousIds=[]     #list with the ids of the previous objects in the flow
        
        #lists to hold statistics of multiple runs
        self.Exits=[]
        self.Lifespan=[]
        
    def initialize(self):
        Process.__init__(self)
        self.Res=Resource(capacity=infinity)         
        self.numOfExits=0
        self.totalLifespan=0
        
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
        
        self.totalTaktTime=0        #the total time between to consecutive exits    
        self.TaktTime=[]        #list that holds the avg time between to consecutive exits                                       
                                                      
        self.waitToDispose=False    #shows if the object waits to dispose an entity  
        
    def run(self):
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity
                                                                    #and one predecessor requests it  
            self.getEntity()                                                                                                  
            self.numOfExits+=1      #increase the exits by one
            self.totalTaktTime+=now()-self.timeLastEntityLeft   #add the takt time
            self.timeLastEntityLeft=now()   #update the time that the last entity left from the Exit

    #sets the routing in element for the Exit
    def defineRouting(self, p):
        self.previous=p
                
    #checks if the Exit can accept an entity       
    def canAccept(self): 
        return True   #the exit always can accept an entity
    
    #checks if the Exit can accept an entity and there is an entity waiting for it
    def canAcceptAndIsRequested(self):
        if(len(self.previous)==1):  
            return self.previous[0].haveToDispose()    
    
        isRequested=False
        for i in range(len(self.previous)):
            if(self.previous[i].haveToDispose()):
                isRequested=True
                self.predecessorIndex=i
        return isRequested
    
    #gets an entity from the predecessor     
    def getEntity(self): 
        name=self.previous[self.predecessorIndex].Res.activeQ[0].name   #get the name of the entity for the trace
        self.totalLifespan+=now()-self.previous[self.predecessorIndex].Res.activeQ[0].startTime  #Add the entity's lifespan to the total one. 
        self.previous[self.predecessorIndex].removeEntity()            #remove the entity from the previous object
        self.outputTrace(name)          
    
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        from Globals import G
        self.Exits.append(self.numOfExits)
        try:
            self.Lifespan.append(((self.totalLifespan)/self.numOfExits)/G.Base)
        except ZeroDivisionError:
            self.Lifespan.append(0)
        try:
            self.TaktTime.append(((self.totalTaktTime)/self.numOfExits)/G.Base)
        except ZeroDivisionError:
            self.TaktTime.append(0)

    
   #outputs message to the trace.xls. Format is (Simulation Time | Entity Name | "generated")            
    def outputTrace(self, message): 
        from Globals import G      
        if(G.trace=="Yes"):     #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,message)
            G.traceSheet.write(G.traceIndex,2,"exited the system")          
            G.traceIndex+=1      #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)     
                
    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime):
        from Globals import G   
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            G.outputSheet.write(G.outputIndex,0, "The Throughput in " +self.objName + " is:")
            G.outputSheet.write(G.outputIndex,1,self.numOfExits)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The average lifespan of an entity that exited from "+ self.objName  +" is:")
            try:
                G.outputSheet.write(G.outputIndex,1,((self.totalLifespan)/self.numOfExits)/G.Base)
            except ZeroDivisionError:
                G.outputSheet.write(G.outputIndex,1,0)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The average tatk time in "+ self.objName  +" is:")            
            try:
                G.outputSheet.write(G.outputIndex,1,((self.totalTaktTime)/self.numOfExits)/G.Base)
            except ZeroDivisionError:
                G.outputSheet.write(G.outputIndex,1,0)
            G.outputIndex+=1            
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value                 
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean Throughput in " +self.objName + " is:")
            if self.checkIfArrayHasDifValues(self.Exits): 
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][1][1])  
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Exits[0])
                G.outputSheet.write(G.outputIndex,2,self.Exits[0])
                G.outputSheet.write(G.outputIndex,3,self.Exits[0])                            
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean Lifespan of an entity that exited from "+ self.objName  + " is:")            
            if self.checkIfArrayHasDifValues(self.Lifespan):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Lifespan[0])
                G.outputSheet.write(G.outputIndex,2,self.Lifespan[0])
                G.outputSheet.write(G.outputIndex,3,self.Lifespan[0]) 
            G.outputIndex+=1
            
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the avg takt time in "+ self.objName  + " is:")            
            if self.checkIfArrayHasDifValues(self.TaktTime):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.TaktTime[0])
                G.outputSheet.write(G.outputIndex,2,self.TaktTime[0])
                G.outputSheet.write(G.outputIndex,3,self.TaktTime[0]) 
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