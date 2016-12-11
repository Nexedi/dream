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

# from SimPy.Simulation import Process, Resource, SimEvent
# from SimPy.Simulation import waitevent, now, hold, infinity, activate
import simpy
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
    def __init__(self, id, name, length, speed,**kw):
        CoreObject.__init__(self, id, name)
        self.type="Conveyer"
        self.speed=float(speed)    #the speed of the conveyer in m/sec
        self.length=float(length)  #the length of the conveyer in meters
        # counting the total number of units to be moved through the whole simulation time
        self.numberOfMoves=0
        
        self.predecessorIndex=0     #holds the index of the predecessor from which the Conveyer will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Queue Conveyer dispose an entity next
        # ============================== variable that is used for the loading of machines =============
        self.exitAssignedToReceiver = False             # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 
        from Globals import G
        G.ConveyerList.append(self)
       
    #===========================================================================
    # the initialize method
    #===========================================================================
    def initialize(self):
#         Process.__init__(self)
        CoreObject.initialize(self)
        self.Res=simpy.Resource(self.env, capacity='inf')             

        self.position=[]            #list that shows the position of the corresponding element in the conveyer
        self.timeLastMoveHappened=0   #holds the last time that the move was performed (in reality it is 
                                        #continued, in simulation we have to handle it as discrete)
                                        #so when a move is performed we can calculate where the entities should go
        self.conveyerMover=ConveyerMover(self)      #process that is triggered at the times when an entity reached the end or
                                                    #a place is freed. It performs the move at this point, 
                                                    #so if there are actions to be carried they will
        self.entityLastReachedEnd=None              #the entity that last reached the end of the conveyer
        self.timeBlockageStarted=self.env.now       #the time that the conveyer reached the blocked state
                                                    #plant considers the conveyer blocked even if it can accept just one entity
                                                    #I think this is false
        self.wasFull=False                          #flag that shows if the conveyer was full. So when an entity is disposed
                                                    #if this is true we count the blockage time and set it to false
        self.currentRequestedLength=0               #the length of the entity that last requested the conveyer
        self.currentAvailableLength=self.length     #the available length in the end of the conveyer
        
        self.predecessorIndex=0     #holds the index of the predecessor from which the Conveyer will take an entity next
        self.successorIndex=0       #holds the index of the successor where the Queue Conveyer dispose an entity next
        
        self.requestingEntities=[]                  # list of the entities requesting space on the conveyer
        # signal that notifies the conveyer that its move is completed
        self.moveEnd=self.env.event()
    
    #===========================================================================
    # conveyer generator
    #===========================================================================
    def run(self):
        #these are just for the first Entity
#         activate(self.conveyerMover,self.conveyerMover.run())
        self.env.process(self.conveyerMover.run())
        while 1:
            #calculate the time to reach end. If this is greater than 0 (we did not already have an entity at the end)
            #set it as the timeToWait of the conveyerMover and raise call=true so that it will be triggered 
            if self.updateMoveTime() and self.conveyerMover.expectedSignals['canMove']: 
#                 print self.id, 'time to move', self.conveyerMover.timeToWait
                succeedTuple=(self,self.env.now)
                self.conveyerMover.canMove.succeed(succeedTuple)

            self.printTrace(self.id, waitEvent='')
            
            self.expectedSignals['isRequested']=1
            self.expectedSignals['canDispose']=1
            self.expectedSignals['moveEnd']=1
            
            receivedEvent=yield self.env.any_of([self.isRequested , self.canDispose , self.moveEnd]) # , self.loadOperatorAvailable]
            # if the event that activated the thread is isRequested then getEntity
            if self.isRequested in receivedEvent:
                transmitter, eventTime=self.isRequested.value
                self.printTrace(self.id, isRequested='')
                # reset the isRequested signal parameter
                self.isRequested=self.env.event()
                # get the entity
                self.getEntity()
                # this should be performed only the first time
                if not self.numberOfMoves:
                    self.timeLastMoveHappened=self.env.now
#             # if the queue received an loadOperatorIsAvailable (from Router) with signalparam time
#             if self.loadOperatorAvailable.value:
#                 self.loadOperatorAvailable.value=None
            # if the queue received an canDispose with signalparam time, this means that the signals was sent from a MouldAssemblyBuffer
            if self.canDispose in receivedEvent:
                transmitter, eventTime=self.canDispose.value
                self.printTrace(self.id, canDispose='')
                self.canDispose=self.env.event()
            # if the object received a moveEnd signal from the ConveyerMover
            if self.moveEnd in receivedEvent:
                transmitter, eventTime=self.moveEnd.value
                self.printTrace(self.id, moveEnd='')
                self.moveEnd=self.env.event()
                # check if there is a possibility to accept and signal a giver
                if self.canAccept():
                    self.printTrace(self.id, attemptSignalGiver='(removeEntity)')
                    self.signalGiver()
            
            self.expectedSignals['isRequested']=0
            self.expectedSignals['canDispose']=0
            self.expectedSignals['moveEnd']=0
            
            # if the event that activated the thread is canDispose then signalReceiver
            if self.haveToDispose():
                self.printTrace(self.id, attemptSignalReceiver='(generator)')
                if self.receiver:
                    if not self.receiver.entryIsAssignedTo():
                        self.printTrace(self.id, attemptSignalReceiver='(generator1)')
                        self.signalReceiver()
                    continue
                self.printTrace(self.id, attemptSignalReceiver='(generator2)')
                self.signalReceiver()
    
    #===========================================================================
    # calculate move time
    #===========================================================================
    def updateMoveTime(self):
        # calculate time to reach end
        timeToReachEnd=0
        if self.position:
            if (not self.length-self.position[0]<0.000001):
                timeToReachEnd=((self.length-self.position[0])/float(self.speed))/60
        # find the requested length
        requestedLength=self.findRequestedLength()
        # calculate time to become available
        timeToBecomeAvailable=0
        if self.position:
            if requestedLength>self.position[-1]:
                timeToBecomeAvailable=((requestedLength-self.position[-1])/float(self.speed))/60
        # pick the smallest but not zero
        timeToWait=0
        if timeToReachEnd>0:
            timeToWait=timeToReachEnd
        if timeToBecomeAvailable>0:
            if timeToBecomeAvailable<timeToWait:
                timeToWait=timeToBecomeAvailable
        self.conveyerMover.timeToWait=timeToWait
        if timeToWait>0.000001:
            return True
        return False
    
    #===========================================================================
    # calculate the requested length
    #===========================================================================
    def findRequestedLength(self):
        minRequestedLength=0
        requestedLength=0
        # search ammong the predecessors that have something to give
        for object in [x for x in self.previous if x.haveToDispose()]:
            #update the requested Length
            requestedLength=object.getActiveObjectQueue()[0].length
            # if the min requested length is not zero check if the current requested is smaller
            if minRequestedLength:
                if requestedLength<minRequestedLength and requestedLength!=0:
                    minRequestedLength=requestedLength
            # otherwise check if current requested length is not zero
            else:
                if requestedLength>0:
                    minRequestedLength=requestedLength
        return minRequestedLength
    
    #===========================================================================
    # checks whether an entity has reached the end
    #===========================================================================
    def entityReachedEnd(self):
        if(len(self.position)>0):           
            if(self.length-self.position[0]<0.000001) and (not self.entityLastReachedEnd==self.getActiveObjectQueue()[0]):
                self.waitToDispose=True
                self.entityLastReachedEnd=self.getActiveObjectQueue()[0]
                self.printTrace(self.getActiveObjectQueue()[0].name, conveyerEnd='')
                return True
        return False

    #===========================================================================
    # moves the entities in the line
    # also counts the time the move required to assign it as working time
    #===========================================================================
    def moveEntities(self):
        interval=self.env.now-self.timeLastMoveHappened
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
                    self.timeLastEntityReachedEnd=self.env.now
                    self.timeLastEntityEnded=self.env.now
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
        self.timeLastMoveHappened=self.env.now
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
            return False
        activeEntity=thecallerQueue[0]
        requestedLength=activeEntity.length      #read what length the entity has
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
        if self.enoughSpaceFor(giverObject)and\
                 giverObject.haveToDispose(activeObject) and\
                 giverObject in activeObject.previous:
            # if the conveyer can accept an entity is not blocked and thus the requested length has to be reset
#             print 'reseting requested length'
            # reset the currentRequestedLength
            self.currentRequestedLength=0
            return True
        return False

    #===========================================================================
    # gets an entity from the predecessor
    #===========================================================================
    def getEntity(self):       
        #the entity is placed in the start of the conveyer
        self.position.append(0)
        activeEntity=CoreObject.getEntity(self) 
        # counting the total number of units to be moved through the whole simulation time
        self.numberOfMoves+=1
        #check if the conveyer became full to start counting blockage 
        if self.isFull():
            self.timeBlockageStarted=self.env.now
            self.wasFull=True
            self.printTrace(self.id, conveyerFull=str(len(self.getActiveObjectQueue())))
        return activeEntity
    
    #===========================================================================
    # removes an entity from the Conveyer
    #===========================================================================
    def removeEntity(self, entity=None):
        activeEntity=CoreObject.removeEntity(self, entity)      #run the default method  
        self.addBlockage()
        # remove the entity from the position list
        self.position.pop(0)
        # the object doesn't wait to dispose any more
        self.waitToDispose=False  
        #if the conveyer was full, it means that it also was blocked
        #we count this blockage time 
        if self.wasFull:
#             self.totalBlockageTime+=self.env.now-self.timeBlockageStarted
            self.wasFull=False
        #calculate the time that the conveyer will become available again and trigger the conveyerMover
        if self.updateMoveTime() and self.conveyerMover.expectedSignals['canMove']:
            succeedTuple=(self,self.env.now)
            self.conveyerMover.canMove.succeed(succeedTuple)
        # if there is anything to dispose of then signal a receiver
        if self.haveToDispose():
            self.printTrace(self.id, attemptSingalReceiver='(removeEntity)')
            self.signalReceiver()
        return activeEntity
    
    #===========================================================================
    # adds the blockage time to totalBlockageTime 
    # each time an Entity is removed
    #===========================================================================
    def addBlockage(self):
        if self.wasFull:
            self.totalBlockageTime+=self.env.now-self.timeBlockageStarted
    
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
            self.totalBlockageTime+=self.env.now-self.timeBlockageStarted+0.1

        #when the conveyer was nor working or blocked it was waiting
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime-self.totalBlockageTime 
        
        #update the lists to hold data for multiple runs
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)
        self.Blockage.append(100*self.totalBlockageTime/MaxSimtime)

    #===========================================================================
    # outputs results to JSON File
    #===========================================================================
    def outputResultsJSON(self):
        from Globals import G
        json = {'_class': self.class_name,
                'id': self.id,
                'results': {}}
        json['results']['working_ratio'] = self.Working
        json['results']['blockage_ratio'] = self.Blockage
        json['results']['waiting_ratio'] = self.Waiting

        G.outputJSON['elementList'].append(json)


#===============================================================================
# Process that handles the moves of the conveyer
#===============================================================================
class ConveyerMover(object):
    #===========================================================================
    # ConveyerMover init method
    #===========================================================================
    def __init__(self, conveyer):
#         Process.__init__(self)
        from Globals import G
        self.env=G.env
        self.conveyer=conveyer      #the conveyer that owns the mover
        self.timeToWait=0           #the time to wait every time. This is calculated by the conveyer and corresponds
                                    #either to the time that one entity reaches the end or the time that one space is freed
        self.canMove=self.env.event()
        self.expectedSignals={'canMove': 1}

    #===========================================================================
    # ConveyerMover generator
    #===========================================================================
    def run(self):
        while 1:
            self.conveyer.printTrace(self.conveyer.id, waitEvent='(canMove)')
            self.expectedSignals['canMove']=1
            yield self.canMove      #wait until the conveyer triggers the mover
            transmitter, eventTime=self.canMove.value
            self.expectedSignals['canMove']=0
            self.canMove=self.env.event()
            self.conveyer.printTrace(self.conveyer.id, received='(canMove)')
            
            yield self.env.timeout(self.timeToWait)                 #wait for the time that the conveyer calculated
            #     continue if interrupted
            self.conveyer.moveEntities()                    # move the entities of the conveyer
            if self.conveyer.expectedSignals['moveEnd']:
                succeedTuple=(self,self.env.now)
                self.conveyer.moveEnd.succeed(succeedTuple)     # send a signal to the conveyer that the move has ended
                self.conveyer.expectedSignals['moveEnd']=0

    
