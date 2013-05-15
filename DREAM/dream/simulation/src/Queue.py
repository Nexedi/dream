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
        self.predecessorIndex=0     #holds the index of the predecessor from which the Queue will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Queue will dispose an entity next
    
        self.id=id
        self.objName=name
        self.capacity=capacity
        self.nameLastEntityEntered=""   #keeps the name of the last entity that entered in the queue
        self.timeLastEntityEntered=0    #keeps the time of the last entity that entered in the queue

        self.next=[]        #list with the next objects in the flow
        self.previous=[]    #list with the previous objects in the flow
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.previousIds=[]     #list with the ids of the previous objects in the flow
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
    #it checks also who called it and returns TRUE only to the predecessor that will give the entity. 
    #this is kind of slow I think got to check      
    def canAccept(self): 
        if(len(self.previous)==1):
            return len(self.Res.activeQ)<self.capacity   
    
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
    
    #checks if the Queue can dispose an entity to the following object
    #it checks also who called it and returns TRUE only to the successor that will give the entity. 
    #this is kind of slow I think got to check   
    def haveToDispose(self): 
        if(len(self.next)==1):
            return len(self.Res.activeQ)>0 
        
        #if the Queue is empty it returns false right away
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
        return len(self.Res.activeQ)>0 and flag   

    #checks if the Queue can accept an entity and there is an entity in some predecessor waiting for it
    #also updates the predecessorIndex to the one that is to be taken
    def canAcceptAndIsRequested(self):
        if(len(self.previous)==1):
            return len(self.Res.activeQ)<self.capacity and self.previous[0].haveToDispose() 
    
        isRequested=False
        maxTimeWaiting=0
        for i in range(len(self.previous)):
            if(self.previous[i].haveToDispose()):
                isRequested=True
                #timeWaiting=now()-(self.previous[i].timeLastEntityEnded+self.previous[i].downTimeInTryingToReleaseCurrentEntity)
                
                if(self.previous[i].downTimeInTryingToReleaseCurrentEntity>0):
                    timeWaiting=now()-self.previous[i].timeLastFailureEnded
                else:
                    timeWaiting=now()-self.previous[i].timeLastEntityEnded
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): #or maxTimeWaiting==0):
                    self.predecessorIndex=i  
                    maxTimeWaiting=timeWaiting                                     
        return len(self.Res.activeQ)<self.capacity and isRequested  
    
    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):
        self.Res.activeQ=[self.previous[self.predecessorIndex].Res.activeQ[0]]+self.Res.activeQ   #get the entity from the previous object
                                                                                                      #and put it in front of the activeQ       
        self.previous[self.predecessorIndex].removeEntity()     #remove the entity from the previous object  
    
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