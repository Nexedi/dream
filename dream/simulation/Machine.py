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
Created on 8 Nov 2012

@author: George
'''
'''
Models a machine that can also have failures
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold

from Failure import Failure
from CoreObject import CoreObject

from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat

# ===========================================================================
# the Machine object
# ===========================================================================
class Machine(CoreObject):
            
    #initialize the id the capacity, of the resource and the distribution        
    def __init__(self, id, name, capacity=1, distribution='Fixed', mean=1, stdev=0, min=0, max=10,\
                  failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None'):
#         Process.__init__(self)
        CoreObject.__init__(self)
        # used for the routing of the entities
        self.predecessorIndex=0                     #holds the index of the predecessor from which the Machine will take an entity next
        self.successorIndex=0                       #holds the index of the successor where the Machine will dispose an entity next
        #     hold the id, name, and type of the Machine instance
        self.id=id
        self.objName=name
        self.type="Machine"                         #String that shows the type of object
        #     holds the capacity of the machine 
        self.capacity=capacity
        #     define the distribution types of the processing and failure times respectively
        self.distType=distribution                  #the distribution that the procTime follows      
        self.failureDistType=failureDistribution    #the distribution that the failure follows   
        #     sets the repairman resource of the Machine
        self.repairman=repairman         
        #     Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=mean
        self.rng.stdev=stdev
        self.rng.min=min
        self.rng.max=max
        self.MTTF=MTTF
        self.MTTR=MTTR
        self.availability=availability        
#         #     lists that hold the previous and next objects in the flow
#         self.next=[]                                #list with the next objects in the flow
#         self.previous=[]                            #list with the previous objects in the flow
#         self.nextIds=[]                             #list with the ids of the next objects in the flow
#         self.previousIds=[]                         #list with the ids of the previous objects in the flow
#         #     lists to hold statistics of multiple runs
#         self.Failure=[]
#         self.Working=[]
#         self.Blockage=[]
#         self.Waiting=[]

    # =======================================================================
    # initialize the Machine object
    # =======================================================================        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        
        #if the failure distribution for the object is fixed, activate the failure       
        if(self.failureDistType=="Fixed" or self.failureDistType=="Availability"):  
            MFailure=Failure(self,  self.failureDistType, self.MTTF, self.MTTR, self.availability, self.id, self.repairman)
            activate(MFailure,MFailure.run())
        
        # initialize the internal Queue (type Resource) of the Machine 
        self.Res=Resource(self.capacity)      
    
    # =======================================================================
    # the main process of the machine
    # =======================================================================
    def run(self):
        #execute all through simulation time
        while 1:
            # wait until the machine can accept an entity and one predecessor requests it 
            # canAcceptAndIsRequested is invoked to check when the machine requested to receive an entity  
            yield waituntil, self, self.canAcceptAndIsRequested          
            # get the entity from the predecessor                                                                            
            self.currentEntity=self.getEntity()    
            # set the currentEntity as the Entity just received and initialize the timer timeLastEntityEntered
#             self.currentEntity=self.getActiveObjectQueue()[0]       # entity is the current entity processed in Machine
            self.nameLastEntityEntered=self.currentEntity.name      # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=now()                        #this holds the last time that an entity got into Machine  
            # variables dedicated to hold the processing times, the time when the Entity entered, 
            # and the processing time left 
            timeEntered=now()                                       # timeEntered dummy Timer that holds the time the last Entity Entered
            tinMStart=self.calculateProcessingTime()                # get the processing time, tinMStarts holds the processing time of the machine 
            tinM=tinMStart                                          # timer to hold the processing time left
            self.processingTimeOfCurrentEntity=tinMStart            # processing time of the machine 
                                                                     
            # variables used to flag any interruptions and the end of the processing     
            interruption=False    
            processingEndedFlag=True 
            # timers to follow up the failure time of the machine while on current Entity
            failureTime=0                                           # dummy variable keeping track of the failure time 
                                                                    # might be feasible to avoid it
            self.downTimeInCurrentEntity=0                          #holds the total time that the 
                                                                    #object was down while holding current entity
            # this loop is repeated until the processing time is expired with no failure
            # check when the processingEndedFlag switched to false              
            while processingEndedFlag:
                # tBefore : dummy variable to keep track of the time that the processing starts after 
                #           every interruption                        
                tBefore=now()
                # wait for the processing time left tinM, if no interruption occurs then change the 
                # processingEndedFlag and exit loop,
                # else (if interrupted()) set interruption flag to true (only if tinM==0),
                # and recalculate the processing time left tinM,
                # passivate while waiting for repair.             
                yield hold,self,tinM                                # getting processed for remaining processing time tinM
                if self.interrupted():                              # if a failure occurs while processing the machine is interrupted.
                    # output to trace that the Machine (self.objName) got interrupted                                                                  
                    self.outputTrace(self.getActiveObjectQueue()[0].name, "Interrupted at "+self.objName)
                    # recalculate the processing time left tinM
                    tinM=tinM-(now()-tBefore)
                    if(tinM==0):            # sometimes the failure may happen exactly at the time that the processing would finish
                                            # this may produce disagreement with the simul8 because in both SimPy and Simul8
                                            # it seems to be random which happens 1st
                                            # this should not appear often to stochastic models though where times are random
                        interruption=True
                    # passivate the Machine for as long as there is no repair
                    # start counting the down time at breatTime dummy variable
                    breakTime=now()                                 # dummy variable that the interruption happened
                    yield passivate,self                            # if there is a failure in the machine it is passivated
                    # use the timers to count the time that Machine is down and related 
                    self.downTimeProcessingCurrentEntity+=now()-breakTime       # count the time that Machine is down while processing this Entity
                    self.downTimeInCurrentEntity+=now()-breakTime               # count the time that Machine is down while on currentEntity
                    self.timeLastFailureEnded=now()                             # set the timeLastFailureEnded
                    failureTime+=now()-breakTime                                # dummy variable keeping track of the failure time 
                    # output to trace that the Machine self.objName was passivated for the current failure time
                    self.outputTrace(self.getActiveObjectQueue()[0].name, "passivated in "+self.objName+" for "+str(now()-breakTime))              
                # if no interruption occurred the processing in M1 is ended 
                else:
                    processingEndedFlag=False
            # output to trace that the processing in the Machine self.objName ended 
            self.outputTrace(self.getActiveObjectQueue()[0].name,"ended processing in "+self.objName)
            # set the variable that flags an Entity is ready to be disposed 
            self.waitToDispose=True
            # update the total working time 
            self.totalWorkingTime+=tinMStart                        # the total processing time for this entity 
                                                                    # is what the distribution initially gave
                                                                    
            # update the variables keeping track of Entity related attributes of the machine    
            self.timeLastEntityEnded=now()                          # this holds the time that the last entity ended processing in Machine 
            self.nameLastEntityEnded=self.currentEntity.name        # this holds the name of the last entity that ended processing in Machine
            self.completedJobs+=1                                   # Machine completed one more Job
            # re-initialize the downTimeProcessingCurrentEntity.
            # a new machine is about to enter
            self.downTimeProcessingCurrentEntity=0
               
            # dummy variable requests the successor object now
            reqTime=now()                                           # entity has ended processing in Machine and requests for the next object 
            # initialize the timer downTimeInTryingToReleaseCurrentEntity, we have to count how much time 
            # the Entity will wait for the next successor to be able to accept (canAccept)
            self.downTimeInTryingToReleaseCurrentEntity=0      
                
            while 1:
                # wait until the next Object is available or machine has failure
                yield waituntil, self, self.ifCanDisposeOrHaveFailure  
                
                # if Next object available break      
                if self.Up:   
                    break
                # if M1 had failure, we want to wait until it is fixed and also count the failure time. 
                else:
                    failTime=now()                                  # dummy variable holding the time failure happened
                    # passivate until machine is up
                    yield waituntil, self, self.checkIfMachineIsUp  
                    failureTime+=now()-failTime                     # count the failure while on current entity time with failureTime variable
                    # calculate the time the Machine was down while trying to dispose the current Entity, 
                    # and the total down time while on current Entity
                    self.downTimeInTryingToReleaseCurrentEntity+=now()-failTime         
                    self.downTimeInCurrentEntity+=now()-failTime    # already updated from failures during processing
                    # update the timeLastFailureEnded   
                    self.timeLastFailureEnded=now()           
                            
            totalTime=now()-timeEntered                             # dummy variable holding the total time the Entity spent in the Machine
            blockageTime=totalTime-(tinMStart+failureTime)          # count the time the Machine was blocked subtracting the failureTime 
                                                                    #    and the processing time from the totalTime spent in the Machine
            # might be possible to avoid using blockageTime
            #    self.totalBlockageTime+=blockageTime
            self.totalBlockageTime+=totalTime-(tinMStart+failureTime)   #the time of blockage is derived from 
                                                                                         #the whole time in the machine
                                                                                         #minus the processing time and the failure time
    # =======================================================================
    # checks if the machine is Up
    # =======================================================================
    def checkIfMachineIsUp(self):
        return self.Up

    # =======================================================================
    # checks if the Machine can accept an entity       
    # it checks also who called it and returns TRUE only to the predecessor 
    # that will give the entity.
    # =======================================================================  
    def canAccept(self, callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        
        # if we have only one predecessor just check if there is a place and the machine is up
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(len(activeObject.previous)==1 or callerObject==None):      
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity
                      
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        return len(activeObjectQueue)<activeObject.capacity and (thecaller is giverObject) and self.Up
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some predecessor waiting for it
    # also updates the predecessorIndex to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
                
        # if we have only one predecessor just check if there is a place, 
        # the machine is up and the predecessor has an entity to dispose
        # this is done to achieve better (cpu) processing time
        if(len(activeObject.previous)==1):
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                 and giverObject.haveToDispose(activeObject) 
        
        # dummy variables that help prioritize the objects requesting to give objects to the Machine (activeObject)
        isRequested=False                                           # is requested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked
        
        # loop through the predecessors to see which have to dispose and which is the one blocked for longer
        i=0                                                         # index used to set the predecessorIndex to the giver waiting the most
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject)):
                isRequested=True                                    # if the predecessor objects have entities to dispose of
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the predecessor has been down while trying to give away the Entity
                    timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                else:
                    timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.predecessorIndex=i                 # the object to deliver the Entity to the activeObject is set to the ith member of the previous list
                    maxTimeWaiting=timeWaiting    
            i+=1                                                    # in the next loops, check the other predecessors in the previous list
        return activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested               
    
    # =======================================================================
    # checks if the machine down or it can dispose the object
    # =======================================================================
    def ifCanDisposeOrHaveFailure(self):
        try:
            return self.Up==False or self.getReceiverObject().canAccept(self) or len(self.getActiveObjectQueue())==0  
        except AttributeError:
            return False
  
    # =======================================================================
    # removes an entity from the Machine
    # =======================================================================
    def removeEntity(self):
        activeObject=self.getActiveObject()  
        #activeObject.outputTrace("releases "+activeObject.objName)  # output to trace that the Entity was released from the currentObject
        activeEntity=CoreObject.removeEntity(self)                               #run the default method     
        activeObject.timeLastEntityLeft=now()                       # set the time that the last Entity was removed from this object
        activeObject.waitToDispose=False                            # update the waitToDispose flag
        activeObject.downTimeInTryingToReleaseCurrentEntity=0       # re-initialize the timer downTimeInTryingToReleaseCurrentEntity
        return activeEntity
        
    # ======================================================================= 
    # checks if the Machine can dispose an entity to the following object
    # =======================================================================
    def haveToDispose(self, callerObject=None):
        # get active and the receiver object
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()    
        receiverObject=activeObject.getReceiverObject() 
        #if we have only one successor just check if machine waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            return len(activeObjectQueue)>0 and activeObject.waitToDispose and activeObject.Up
        
#         # if the Machine is empty it returns false right away
#         if(len(activeObjectQueue)==0):
#             return False
   
        thecaller=callerObject
        # give the entity to the successor that is waiting for the most time. 
        # (plant simulation does not do this in every occasion!)       
        maxTimeWaiting=0                                            # dummy variable counting the time a successor is waiting
        i=0                                                         # index used to set the successorIndex to the giver waiting the most
        for object in activeObject.next:
            if(object.canAccept(activeObject)):                     # if a successor can accept an object
                timeWaiting=now()-object.timeLastEntityLeft         # the time it has been waiting is updated and stored in dummy variable timeWaiting
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# if the timeWaiting is the maximum among the ones of the successors 
                    maxTimeWaiting=timeWaiting
                    activeObject.successorIndex=i                   # set the successorIndex equal to the index of the longest waiting successor
            i+=1                                                    # in the next loops, check the other successors in the previous list
        return len(activeObjectQueue)>0 and activeObject.waitToDispose\
             and activeObject.Up and (thecaller is receiverObject)       
    
   # =======================================================================
   # actions to be taken after the simulation ends
   # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime
        
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        alreadyAdded=False                      # a flag that shows if the blockage time has already been added
        
        # checks all the successors. If no one can accept an Entity then the machine might be blocked
        mightBeBlocked=True
        for nextObject in self.next:
            if nextObject.canAccept():
                mightBeBlocked=False
           
        # if there is an entity that finished processing in a Machine but did not get to reach 
        # the following Object till the end of simulation, 
        # we have to add this blockage to the percentage of blockage in Machine
        # we should exclude the failure time in current entity though!
        # if (len(self.Res.activeQ)>0) and (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):       
        if (len(activeObjectQueue)>0) and (mightBeBlocked)\
             and ((activeObject.nameLastEntityEntered == activeObject.nameLastEntityEnded)):
            # be carefull here, might have to reconsider
            activeObject.totalBlockageTime+=now()-(activeObject.timeLastEntityEnded+activeObject.downTimeInTryingToReleaseCurrentEntity)
            if activeObject.Up==False:
                activeObject.totalBlockageTime-=now()-activeObject.timeLastFailure
                alreadyAdded=True

        #if Machine is currently processing an entity we should count this working time    
        if(len(activeObject.Res.activeQ)>0) and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered)):           
            #if Machine is down we should add this last failure time to the time that it has been down in current entity 
            if self.Up==False:
#             if(len(activeObjectQueue)>0) and (self.Up==False):                         
                activeObject.downTimeProcessingCurrentEntity+=now()-activeObject.timeLastFailure             
            activeObject.totalWorkingTime+=now()-activeObject.timeLastEntityEntered-activeObject.downTimeProcessingCurrentEntity 
        
        # if Machine is down we have to add this failure time to its total failure time
        # we also need to add the last blocking time to total blockage time     
        if(activeObject.Up==False):
            activeObject.totalFailureTime+=now()-activeObject.timeLastFailure
            # we add the value only if it hasn't already been added
            #if((len(self.next[0].Res.activeQ)>0) and (self.nameLastEntityEnded==self.nameLastEntityEntered) and (not alreadyAdded)):
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(now()-activeObject.timeLastEntityEnded)-(now()-activeObject.timeLastFailure)-activeObject.downTimeInTryingToReleaseCurrentEntity 
        
        #Machine was idle when it was not in any other state    
        activeObject.totalWaitingTime=MaxSimtime-activeObject.totalWorkingTime-activeObject.totalBlockageTime-activeObject.totalFailureTime   
        
        if activeObject.totalBlockageTime<0 and activeObject.totalBlockageTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalBlockageTime=0  
        
        if activeObject.totalWaitingTime<0 and activeObject.totalWaitingTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalWaitingTime=0  
        
        activeObject.Failure.append(100*self.totalFailureTime/MaxSimtime)    
        activeObject.Blockage.append(100*self.totalBlockageTime/MaxSimtime)  
        activeObject.Waiting.append(100*self.totalWaitingTime/MaxSimtime)    
        activeObject.Working.append(100*self.totalWorkingTime/MaxSimtime)  
     
    # =======================================================================
    # outputs the the "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
        
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
    
    # =======================================================================    
    # outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            json={}
            json['_class'] = 'Dream.Machine';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['failure_ratio']=100*self.totalFailureTime/G.maxSimTime
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['blockage_ratio']=100*self.totalBlockageTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
        else: #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value           
            json={}
            json['_class'] = 'Dream.Machine';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['failure_ratio']={}
            if self.checkIfArrayHasDifValues(self.Failure):
                json['results']['failure_ratio']['min']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][0]
                json['results']['failure_ratio']['avg']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][0]
                json['results']['failure_ratio']['max']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][1]
            else:
                json['results']['failure_ratio']['min']=self.Failure[0]
                json['results']['failure_ratio']['avg']=self.Failure[0]
                json['results']['failure_ratio']['max']=self.Failure[0] 
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
    