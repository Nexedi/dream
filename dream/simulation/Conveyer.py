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

from SimPy.Simulation import Process, Resource, SimEvent
from SimPy.Simulation import waitevent, now, hold, infinity, activate
import xlwt
from CoreObject import CoreObject

#===============================================================================
# The conveyer object
#===============================================================================
class Conveyer(CoreObject):    
    class_name = 'Dream.Conveyer'
    #===========================================================================
    # the conveyer __init__ method
    #===========================================================================
    def __init__(self, id, name, length, speed):
        CoreObject.__init__(self, id, name)
        self.type="Conveyer"
        self.speed=speed    #the speed of the conveyer in m/sec
        self.length=length  #the length of the conveyer in meters
        # counting the total number of units to be moved through the whole simulation time
        self.numberOfMoves=0
        
        self.predecessorIndex=0     #holds the index of the predecessor from which the Conveyer will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Queue Conveyer dispose an entity next
        # ============================== variable that is used for the loading of machines =============
        self.exitAssignedToReceiver = False             # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 
        self.moveEnd=SimEvent('moveEnd')
        
    #===========================================================================
    # the initialize method
    #===========================================================================
    def initialize(self):
        Process.__init__(self)
        CoreObject.initialize(self)
        self.Res=Resource(capacity=infinity)         

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
        self.entityLastReachedEnd=None              #the entity that last reached the end of the conveyer
        self.timeBlockageStarted=now()              #the time that the conveyer reached the blocked state
                                                    #plant considers the conveyer blocked even if it can accept just one entity
                                                    #I think this is false
        self.wasFull=False                          #flag that shows if the conveyer was full. So when an entity is disposed
                                                    #if this is true we count the blockage time and set it to false
        self.currentRequestedLength=0               #the length of the entity that last requested the conveyer
        self.currentAvailableLength=self.length     #the available length in the end of the conveyer
        
        self.predecessorIndex=0     #holds the index of the predecessor from which the Conveyer will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Queue Conveyer dispose an entity next
    
    #===========================================================================
    # conveyer generator
    #===========================================================================
    def run(self):
        #these are just for the first Entity
        activate(self.conveyerMover,self.conveyerMover.run())
        # check if there is WIP and signal receiver
        self.initialSignalReceiver()
        while 1:
            #calculate the time to reach end. If this is greater than 0 (we did not already have an entity at the end)
            #set it as the timeToWait of the conveyerMover and raise call=true so that it will be triggered 
            self.timeToReachEnd=0
            if self.position:
                if (not self.length-self.position[0]<0.000001):
                    self.timeToReachEnd=((self.length-self.position[0])/float(self.speed))/60                       
                if self.timeToReachEnd>0:
                    self.conveyerMover.timeToWait=self.timeToReachEnd
                    self.conveyerMover.canMove.signal(now())
            
            self.printTrace(self.id, 'will wait for event')
            yield waitevent, self, [self.isRequested,self.canDispose, self.moveEnd] # , self.loadOperatorAvailable]
            # if the event that activated the thread is isRequested then getEntity
            if self.isRequested.signalparam:
                self.printTrace(self.id, 'received an is requested event')
                # reset the isRequested signal parameter
                self.isRequested.signalparam=None
                # get the entity
                self.getEntity()
                # this should be performed only the first time
                if not self.numberOfMoves:
                    self.timeLastMoveHappened=now()
#             # if the queue received an loadOperatorIsAvailable (from Router) with signalparam time
#             if self.loadOperatorAvailable.signalparam:
#                 self.loadOperatorAvailable.signalparam=None
            # if the queue received an canDispose with signalparam time, this means that the signals was sent from a MouldAssemblyBuffer
            if self.canDispose.signalparam:
                self.printTrace(self.id, 'received a canDispose event')
                self.canDispose.signalparam=None
            # if the object received a moveEnd signal from the ConveyerMover
            if self.moveEnd.signalparam:
                self.printTrace(self.id, 'received a moveEnd event')
                self.moveEnd.signalparam=None
                # check if there is a possibility to accept and signal a giver
                if self.canAccept():
                    self.printTrace(self.id, 'will try to signal Giver from removeEntity')
                    self.signalGiver()
            
#             # if there is an entity that finished its motion
#             if self.entityReachedEnd():
            # if the event that activated the thread is canDispose then signalReceiver
            if self.haveToDispose():
#                 self.printTrace(self.id, 'will try to signal a receiver from generator')
                if self.receiver:
                    if not self.receiver.entryIsAssignedTo():
                        self.printTrace(self.id, 'will try to signal receiver from generator1')
                        self.signalReceiver()
                    continue
                self.printTrace(self.id, 'will try to signal receiver from generator2')
                self.signalReceiver()
    
    #===========================================================================
    # checks if there is any entity at the exit
    #===========================================================================
    def entityAtExit(self):
        pass
    
    #===========================================================================
    # checks whether an entity has reached the end
    #===========================================================================
    def entityReachedEnd(self):
        if(len(self.position)>0):           
            if(self.length-self.position[0]<0.000001) and (not self.entityLastReachedEnd==self.getActiveObjectQueue()[0]):
                self.waitToDispose=True
                self.entityLastReachedEnd=self.getActiveObjectQueue()[0]
                self.printTrace(self.getActiveObjectQueue()[0].name, 'has reached the end'+'  !!  .  !!  .'*7)
                return True
        return False

    #===========================================================================
    # moves the entities in the line
    # also counts the time the move required to assign it as working time
    #===========================================================================
    def moveEntities(self):
        interval=now()-self.timeLastMoveHappened
        interval=(float(interval))*60.0     #the simulation time that passed since the last move was taken care
        moveTime1=0
        moveTime2=0
#         print [x for x in self.position]
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
                    self.entityLastReachedEnd=self.getActiveObjectQueue()[0]
                    self.timeLastEntityReachedEnd=now()
                    self.timeLastEntityEnded=now()
        #for the other entities
        for i in range(1,len(self.getActiveObjectQueue())):
            #if it does not reach the preceding entity move it according to speed
            if self.position[i]+interval*self.speed<self.position[i-1]-self.getActiveObjectQueue()[i].length:
                moveTime2=interval
                self.position[i]=self.position[i]+interval*self.speed
            #else move it right before the preceding entity
            else:
                mTime=(self.position[i-1]-self.getActiveObjectQueue()[i].length-self.position[i])/self.speed
                if mTime>moveTime2:
                    moveTime2=mTime
                self.position[i]=self.position[i-1]-self.getActiveObjectQueue()[i-1].length
#         print [x for x in self.position]
        #assign this time as the time of last move
        self.timeLastMoveHappened=now()
        #all the time of moving (the max since things move in parallel) is considered as working time
        self.totalWorkingTime+=max(moveTime1/60.0, moveTime2/60.0)
        # check again if there is any entity that has reached the exit of the conveyer
        self.entityReachedEnd()

    #===========================================================================
    # checks if the Conveyer can accept an entity
    #===========================================================================
    def canAccept(self, callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        #move the entities so that the available length can be calculated
#         print self.id, 'moving entities from canAccept'
        activeObject.moveEntities()
        # calculate available length
        availableLength=activeObject.calculateAvailableLength()
#         print 'available length', availableLength
#         print [x for x in self.position]
#         print [x.name for x in self.getActiveObjectQueue()]
        # if the callerObject is not defined then return true if the available length is not zero
        if(callerObject==None):
            return availableLength>0
        # if there is a caller then check if there is enough space and if it is in the previous list 
        thecaller=callerObject
        if self.enoughSpaceFor(thecaller):
            return (thecaller in activeObject.previous)
        else:
            return False
    
    #===========================================================================
    # calculate available length
    #===========================================================================
    def calculateAvailableLength(self):
        activeObjectQueue=self.getActiveObjectQueue()
        if len(activeObjectQueue)==0:
            availableLength=self.length
        else:
            availableLength=self.position[-1]
        self.currentAvailableLength=availableLength
        return availableLength
    
    #===========================================================================
    # check if there is space for the callerObject
    #===========================================================================
    def enoughSpaceFor(self, callerObject=None):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        assert callerObject, 'there must be a caller for enoughSpaceFor'
        thecaller=callerObject
        thecallerQueue=thecaller.getActiveObjectQueue()
        #if there is no object in the predecessor just return false and set the current requested length to zero
        if len(thecallerQueue)==0:
            self.currentRequestedLength=0
            return False
        activeEntity=thecallerQueue[0]
        requestedLength=activeEntity.length      #read what length the entity has
#         print self.id, 'requested length', requestedLength
        self.currentRequestedLength=requestedLength
        availableLength=self.currentAvailableLength
        #in plant an entity can be accepted even if the available length is exactly zero
        #eg if the conveyer has 8m length and the entities 1m length it can have up to 9 entities.
        #i do not know if this is good but I kept it
        return availableLength-requestedLength>-0.00000001
        
    #===========================================================================
    # checks if the Conveyer can accept an entity and there is a Frame waiting for it
    #===========================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        self.calculateAvailableLength()
        return self.enoughSpaceFor(giverObject)and\
                 giverObject.haveToDispose(activeObject) and\
                 giverObject in activeObject.previous

    #===========================================================================
    # gets an entity from the predecessor
    #===========================================================================
    def getEntity(self):       
        activeEntity=CoreObject.getEntity(self) 
        #the entity is placed in the start of the conveyer
        self.position.append(0)
        # counting the total number of units to be moved through the whole simulation time
        self.numberOfMoves+=1
        #check if the conveyer became full to start counting blockage 
        if self.isFull():
            self.timeBlockageStarted=now()
            self.wasFull=True
            self.printTrace(self.id, 'is now Full '+str(len(self.getActiveObjectQueue()))+' (*) '*20)
        return activeEntity
    
    #===========================================================================
    # removes an entity from the Conveyer
    #===========================================================================
    def removeEntity(self, entity=None):
        activeEntity=CoreObject.removeEntity(self, entity)      #run the default method  
        # remove the entity from the position list
        self.position.pop(0)
        # the object doesn't wait to dispose any more
        self.waitToDispose=False  
        #if the conveyer was full, it means that it also was blocked
        #we count this blockage time 
        if self.wasFull:
#             self.totalBlockageTime+=now()-self.timeBlockageStarted
            self.wasFull=False
            #calculate the time that the conveyer will become available again and trigger the conveyerMover
            self.timeToBecomeAvailable=((self.position[-1]+self.currentRequestedLength)/float(self.speed))/60
#             print self.id, 'time to become available', self.timeToBecomeAvailable
            self.conveyerMover.timeToWait=self.timeToBecomeAvailable
            self.conveyerMover.canMove.signal(now())
#         # if the available length is not zero then try to signal a giver
#         if self.canAccept():
#             self.printTrace(self.id, 'will try to signal Giver from removeEntity')
#             self.signalGiver()
        # if there is anything to dispose of then signal a receiver
        if self.haveToDispose():
            self.printTrace(self.id, 'will try to signal a receiver from removeEntity')
            self.signalReceiver()
        return activeEntity
    
    #===========================================================================
    # adds the blockage time to totalBlockageTime 
    # each time an Entity is removed
    #===========================================================================
    def addBlockage(self):
        if self.wasFull:
            self.totalBlockageTime+=now()-self.timeBlockageStarted
    
    #===========================================================================
    # checks if the Conveyer can dispose an entity to the following object     
    #===========================================================================
    def haveToDispose(self, callerObject=None): 
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        # if there is no caller defined no need to check if the caller is in previous
        callerInPrevious=False
        if(callerObject==None):
            callerInNext=True
        else:
            #move the entities so that the new position of the first entity can be calculated
#             print self.id, 'moving entities from haveToDispose'
            activeObject.moveEntities()
            callerInNext=(callerObject in activeObject.next)
        #it has meaning only if there are one or more entities in the conveyer
        if len(self.position)>0:
            #the conveyer can dispose an object only when an entity is at the end of it
            return len(self.getActiveObjectQueue())>0 and\
                     self.length-self.position[0]<0.000001 and\
                     callerInNext
        else:
            return False

    #===========================================================================
    # checks if the conveyer is full to count the blockage. for some reason Plant regards 
    # the conveyer full even when it has one place
    #===========================================================================
    def isFull(self):
        totalLength=0  
        for entity in self.getActiveObjectQueue():
            totalLength+=entity.length
        return self.length<totalLength
    
    #===========================================================================
    # actions to be taken after the simulation ends
    #===========================================================================
    def postProcessing(self, MaxSimtime=None):              
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime        
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

    #===========================================================================
    # outputs data to "output.xls"
    #===========================================================================
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G
        from Globals import getConfidenceIntervals
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
            working_ci = getConfidenceIntervals(self.Working)
            G.outputSheet.write(G.outputIndex, 1, working_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, working_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, working_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Blockage of "+ self.objName+" is:")
            blockage_ci = getConfidenceIntervals(self.Blockage)
            G.outputSheet.write(G.outputIndex, 1, blockage_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, blockage_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, blockage_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+ self.objName+" is:")
            waiting_ci = getConfidenceIntervals(self.Waiting)
            G.outputSheet.write(G.outputIndex, 1, waiting_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, waiting_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, waiting_ci['max'])
            G.outputIndex+=1
        G.outputIndex+=1

    #===========================================================================
    # outputs results to JSON File
    #===========================================================================
    def outputResultsJSON(self):
        from Globals import G
        from Globals import getConfidenceIntervals
        json = {'_class': self.class_name,
                'id': self.id,
                'results': {}}
        if (G.numberOfReplications == 1):
            # if we had just one replication output the results as numbers
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['blockage_ratio']=100*self.totalBlockageTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
        else:
            json['results']['working_ratio'] = getConfidenceIntervals(self.Working)
            json['results']['blockage_ratio'] = getConfidenceIntervals(self.Blockage)
            json['results']['waiting_ratio'] = getConfidenceIntervals(self.Waiting)

        G.outputJSON['elementList'].append(json)


#===============================================================================
# Process that handles the moves of the conveyer
#===============================================================================
class ConveyerMover(Process):
    #===========================================================================
    # ConveyerMover init method
    #===========================================================================
    def __init__(self, conveyer):
        Process.__init__(self)
        self.conveyer=conveyer      #the conveyer that owns the mover
        self.timeToWait=0           #the time to wait every time. This is calculated by the conveyer and corresponds
                                    #either to the time that one entity reaches the end or the time that one space is freed
        self.canMove=SimEvent('canMove')
    
    #===========================================================================
    # ConveyerMover generator
    #===========================================================================
    def run(self):
        while 1:
            self.conveyer.printTrace(self.conveyer.id, 'mover will wait for canMove event')
            yield waitevent,self,self.canMove      #wait until the conveyer triggers the mover
            self.conveyer.printTrace(self.conveyer.id, 'mover received canMove event')
            
            yield hold,self,self.timeToWait                 #wait for the time that the conveyer calculated
#             print '. .'*40
#             print 'conveyer moving entities'
            #     continue if interrupted
            self.conveyer.moveEntities()                    #move the entities of the conveyer
#             self.conveyer.call=False                        #reset call so it will be triggered only when it is needed again
            self.conveyer.moveEnd.signal(now())
            

    
