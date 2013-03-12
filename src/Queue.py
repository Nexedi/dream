'''
Created on 8 Nov 2012

@author: George
'''

'''
Models a FIFO queue where entities can wait in order to get into a server
'''


from SimPy.Simulation import *

#the Queue object
class Queue(Process):
    
    def __init__(self, id, name, capacity, dummy):
        Process.__init__(self)
        self.id=id
        self.objName=name
        self.capacity=capacity
        self.nameLastEntityEntered=""   #keeps the name of the last entity that entered in the queue
        self.timeLastEntityEntered=0    #keeps the time of the last entity that entered in the queue

        self.next=[]        #list with the next objects in the flow
        self.previous=[]    #list with the previous objects in the flow
        self.type="Queue"   #String that shows the type of object
        self.isDummy=dummy  #Boolean that shows if it is the dummy first Queue
 
    def initialize(self):
        Process.__init__(self)
        self.Res=Resource(self.capacity)        
        self.nameLastEntityEntered=""   #keeps the name of the last entity that entered in the queue
        self.timeLastEntityEntered=0    #keeps the time of the last entity that entered in the queue
                
    def Run(self):  
        while 1:  
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity
                                                                    #and one predecessor requests it                                                  
            self.getEntity()                                                                
            
            #if entity just got to the dummyQ set its startTime as the current time         
            if self.isDummy:               
                self.Res.activeQ[0].startTime=now()

    #sets the routing in and out elements for the queue
    def defineRouting(self, p, n):
        self.next=n
        self.previous=p
            
    #checks if the Q has one available place       
    def checkIfQHasPlace(self): 
        return len(self.Q.activeQ)<self.capacity     
    
    #checks if the Queue can accept an entity       
    def canAccept(self): 
        return len(self.Res.activeQ)<self.capacity   
    
    #checks if the Queue can dispose an entity to the following object     
    def haveToDispose(self): 
        return len(self.Res.activeQ)>0 

    #checks if the Queue can accept an entity and there is an entity waiting for it
    def canAcceptAndIsRequested(self):
        return len(self.Res.activeQ)<self.capacity and self.previous[0].haveToDispose() 
    
    #gets an entity from the predecessor     
    def getEntity(self):
        self.Res.activeQ.append(self.previous[0].Res.activeQ[0])   #get the entity from the previous object
        self.previous[0].removeEntity()     #remove the entity from the previous object    
    
    #removes an entity from the Queue (this is FIFO for now)
    def removeEntity(self):
        self.Res.activeQ.pop(0)

    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        pass    #no actions for the Queue
             
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

    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime):
        pass