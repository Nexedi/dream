'''
Created on 8 Nov 2012

@author: George
'''

'''
models the source object that generates the entities
'''

from SimPy.Simulation import *
from Part import Part
from RandomNumberGenerator import RandomNumberGenerator

#The Source object is a Process
class Source(Process): 
    def __init__(self, id, name, dist, time, item):
        Process.__init__(self)
        self.id=id   
        self.objName=name   
        self.distType=dist      #label that sets the distribution type
        self.interArrivalTime=time     #the mean interarrival time 
        self.totalInterArrivalTime=0    #the total interarrival time 
        self.numberOfArrivals=0         #the number of entities that were created 
        self.next=[]        #list with the next objects in the flow
        self.type="Source"   #String that shows the type of object
        #self.waitToDispose=False
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=time
        self.item=item      #the type of object that the Source will generate
        
        #self.Res=Resource(capacity=infinity) 
        
    def initialize(self):
        Process.__init__(self) 
        self.Res=Resource(capacity=infinity)    
        self.Res.activeQ=[]  
        self.Res.waitQ=[]        
        
    def Run(self):
        i=0
        if(self.distType=="Fixed"): #if the distribution type is fixed
            from Globals import G            
            while 1:
                #self.waitToDispose=True
                self.numberOfArrivals+=1           #we have one new arrival     
                #entity=Entity("Ent"+str(i))        
                entity=self.item(self.item.type+str(i)) #create the Entity object and assign its name 
                entity.creationTime=now()          #assign the current simulation time as the Entity's creation time 
                self.outputTrace(self.item.type+str(i))     #output the trace
                self.Res.activeQ.append(entity)    #append the entity to the resource 
                i+=1        
                #yield hold,self,self.interArrivalTime       #one entity at every interArrivalTime   
                yield hold,self,self.rng.generateNumber()
        elif(self.distType=="Exp"): #if the distribution type is exponential
            from Globals import G
            while 1:
                #self.waitToDispose=True                
                self.numberOfArrivals+=1        #we have one new arrival
                #entity=Entity("Ent"+str(i))     #create the Entity object and assign its name 
                entity=self.item(self.item.type+str(i)) #create the Entity object and assign its name                 
                entity.creationTime=now()          #assign the current simulation time as the Entity's creation time
                self.outputTrace(self.item.type+str(i))      #output the trace
                i+=1
                self.Res.activeQ.append(entity)     #append the entity to the resource           
                timeTillNextArrival=G.Rnd.expovariate(1.0/(self.interArrivalTime))  #create a random number that follows the     
                                                                                    #exponential distribution                                                  
                #yield hold,self,timeTillNextArrival       #one entity at every interArrivalTime   
                yield hold,self,self.rng.generateNumber()
                self.totalInterArrivalTime+=timeTillNextArrival                                                
        else:   #if the distribution type is something else it is an error
            print "Distribution Error in Source "+str(self.id)   
            
    #sets the routing out element for the Source
    def defineRouting(self, n):
        self.next=n  
        
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        pass    #no actions for the Source

    #checks if the Source can dispose an entity to the following object     
    def haveToDispose(self): 
        #return self.waitToDispose 
        return len(self.Res.activeQ)>0
    
    #removes an entity from the Source 
    def removeEntity(self):     
        self.Res.activeQ.pop(0)      
        #if(len(self.Res.activeQ)==0):
            #self.waitToDispose=False
            
   #outputs message to the trace.xls. Format is (Simulation Time | Entity Name | "generated")            
    def outputTrace(self, message):
        from Globals import G
        
        if(G.trace=="Yes"):     #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,message)
            G.traceSheet.write(G.traceIndex,2,"generated")          
            G.traceIndex+=1      #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)     

    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime):
        pass
