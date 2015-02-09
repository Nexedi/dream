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

# from SimPy.Simulation import Process, Resource
# from SimPy.Simulation import waitevent, now, hold
import simpy
import xlwt
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject

#===============================================================================
# the Assembly object
#===============================================================================
class Assembly(CoreObject):
    class_name = 'Dream.Assembly'
    #===========================================================================
    # initialize the object      
    #===========================================================================
    def __init__(self, id='', name='', processingTime=None, inputsDict=None, **kw):
        self.type="Assembly"   #String that shows the type of object
        self.next=[]        #list with the next objects in the flow
        self.previous=[]     #list with the previous objects in the flow
        self.previousPart=[]    #list with the previous objects that send parts
        self.previousFrame=[]    #list with the previous objects that send frames 
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.previousIds=[]   #list with the ids of the previous objects in the flow
        
        #lists to hold statistics of multiple runs
        self.Waiting=[]
        self.Working=[]
        self.Blockage=[]

        if not processingTime:
            processingTime = {'Fixed':{'mean': 0 }}
        if 'Normal' in processingTime.keys() and\
                processingTime['Normal'].get('max', None) is None:
            processingTime['Normal']['max'] = float(processingTime['Normal']['mean']) + 5 * float(processingTime['Normal']['stdev'])
    
        CoreObject.__init__(self, id, name)
        self.rng=RandomNumberGenerator(self, processingTime)
        
         # ============================== variable that is used for the loading of machines =============
        self.exitAssignedToReceiver = False             # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 
        from Globals import G
        G.AssemblyList.append(self)

    # =======================================================================
    # parses inputs if they are given in a dictionary
    # =======================================================================       
    def parseInputs(self, inputsDict):
        CoreObject.parseInputs(self, inputsDict)
        processingTime=inputsDict.get('processingTime',{})
        if not processingTime:
            processingTime = {'distributionType': 'Fixed',
                            'mean': 0,
                            'stdev': 0,
                            'min': 0,
                            }
        if processingTime['distributionType'] == 'Normal' and\
              processingTime.get('max', None) is None:
            processingTime['max'] = float(processingTime['mean']) + 5 * float(processingTime['stdev'])

        self.rng=RandomNumberGenerator(self, **processingTime)
        
         # ============================== variable that is used for the loading of machines =============
        self.exitAssignedToReceiver = False             # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 
        from Globals import G
        G.AssemblyList.append(self)

    #===========================================================================
    # initialize method
    #===========================================================================
    def initialize(self):
#         Process.__init__(self)
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
        self.Res=simpy.Resource(self.env, 1)
        self.Res.users=[]  
#         self.Res.waitQ=[]
            
    #===========================================================================
    # class generator
    #===========================================================================
    def run(self):
        activeObjectQueue=self.getActiveObjectQueue()
        while 1:
            self.printTrace(self.id, waitEvent='')
            # wait until the Queue can accept an entity and one predecessor requests it
            
            self.expectedSignals['isRequested']=1
            
            yield self.isRequested     #[self.isRequested,self.canDispose, self.loadOperatorAvailable]
            if self.isRequested.value:
                transmitter, eventTime=self.isRequested.value
                self.printTrace(self.id, isRequested=transmitter.id)
                # reset the isRequested signal parameter
                self.isRequested=self.env.event()
                
                self.getEntity("Frame")                                 #get the Frame
                                                                    
                for i in range(self.getActiveObjectQueue()[0].capacity):         #this loop will be carried until the Frame is full with the parts
                    self.printTrace(self.id, waitEvent='(to load parts)')
                    self.expectedSignals['isRequested']=1
                    yield self.isRequested
                    if self.isRequested.value:
                        transmitter, eventTime=self.isRequested.value
                        self.printTrace(self.id, isRequested=transmitter.id)
                        # reset the isRequested signal parameter
                        self.isRequested=self.env.event()
                        # TODO: fix the getEntity 'Part' case
                        self.getEntity("Part")
                
                self.expectedSignals['isRequested']=0
                
                self.outputTrace(self.getActiveObjectQueue()[0].name, "is now full in "+ self.objName)
            
                self.isProcessing=True
                self.timeLastFrameWasFull=self.env.now
                self.nameLastFrameWasFull=self.getActiveObjectQueue()[0].name
                
                self.timeLastProcessingStarted=self.env.now
                self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()
                yield self.env.timeout(self.totalProcessingTimeInCurrentEntity)   #hold for the time the assembly operation is carried
                self.totalWorkingTime+=self.env.now-self.timeLastProcessingStarted
                self.isProcessing=False
            
                self.outputTrace(self.getActiveObjectQueue()[0].name, "ended processing in " + self.objName)
                self.timeLastEntityEnded=self.env.now
                self.nameLastEntityEnded=self.getActiveObjectQueue()[0].name
            
                self.timeLastBlockageStarted=self.env.now
                self.isBlocked=True
                self.completedJobs+=1                       #Assembly completed a job
                self.waitToDispose=True                     #since all the frame is full
            
            self.printTrace(self.id, attemptSignalReceiver='(generator)')
            # signal the receiver that the activeObject has something to dispose of
            if not self.signalReceiver():
            # if there was no available receiver, get into blocking control
                
                self.expectedSignals['canDispose']=1
                self.expectedSignals['interruptionStart']=1
                
                while 1:
#                     self.timeLastBlockageStarted=self.env.now       # blockage is starting
                    # wait the event canDispose, this means that the station can deliver the item to successor
                    self.printTrace(self.id, waitEvent='(canDispose or interruption start)')
                    receivedEvent=yield self.env.any_of([self.canDispose , self.interruptionStart])
                    # if there was interruption
                    # TODO not good implementation
                    if self.interruptionStart in receivedEvent:
                        transmitter, eventTime=self.interruptionStart.value
                        assert eventTime==self.env.now, 'the interruption has not been processed on the time of activation'
                        self.interruptionStart=self.env.event()
                    # wait for the end of the interruption
                        self.interruptionActions()                          # execute interruption actions
                        # loop until we reach at a state that there is no interruption
                        while 1:
                            
                            self.expectedSignals['interruptionEnd']=1
                            
                            yield self.interruptionEnd         # interruptionEnd to be triggered by ObjectInterruption
                            
                            self.expectedSignals['interruptionEnd']=0
                            
                            transmitter, eventTime=self.interruptionEnd.value
                            assert eventTime==self.env.now, 'the victim of the failure is not the object that received it'
                            self.interruptionEnd=self.env.event()
                            if self.Up and self.onShift:
                                break
                        self.postInterruptionActions()
                        if self.signalReceiver():
#                             self.timeLastBlockageStarted=self.env.now
                            break
                        else:
                            continue
                    if self.canDispose in receivedEvent:
                        transmitter, eventTime=self.canDispose.value
                        if eventTime!=self.env.now:
                            self.canDispose=self.env.event()
                            continue
                        assert eventTime==self.env.now,'canDispose signal is late'
                        self.canDispose=self.env.event()
                        # try to signal a receiver, if successful then proceed to get an other entity
                        if self.signalReceiver():
                            break
                    # TODO: router most probably should signal givers and not receivers in order to avoid this hold,self,0
                    #       As the receiver (e.g.) a machine that follows the machine receives an loadOperatorAvailable event,
                    #       signals the preceding station (e.g. self.machine) and immediately after that gets the entity.
                    #       the preceding machine gets the canDispose signal which is actually useless, is emptied by the following station
                    #       and then cannot exit an infinite loop.
                    if not self.haveToDispose():
                        break 
                    # notify that the station waits the entity to be removed
                    self.waitEntityRemoval=True
                    self.printTrace(self.id, waitEvent='(entityRemoved)')
                    
                    self.expectedSignals['entityRemoved']=1
                    
                    yield self.entityRemoved
                    
                    self.expectedSignals['entityRemoved']=0
                    
                    transmitter, eventTime=self.entityRemoved.value
                    self.printTrace(self.id, entityRemoved=eventTime)
                    assert eventTime==self.env.now,'entityRemoved event activated earlier than received'
                    self.waitEntityRemoval=False
                    self.entityRemoved=self.env.event()
                    # if while waiting (for a canDispose event) became free as the machines that follows emptied it, then proceed
                    if not self.haveToDispose():
                        break
                    
                self.expectedSignals['canDispose']=0
                self.expectedSignals['interruptionStart']=0
                
    #===========================================================================
    # checks if the Assembly can accept an entity 
    #===========================================================================
    def canAccept(self, callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        #if there is no caller then perform the default 
        if(callerObject==None):
            return len(activeObjectQueue)==0
        thecaller=callerObject
        # if the object holds nothing then return true
        if len(self.getActiveObjectQueue())==0:
            return not activeObject.entryIsAssignedTo()
        # if it holds already a frame then return true only for parts and if the frame has still space
        if len(activeObjectQueue[0].getFrameQueue())<activeObjectQueue[0].capacity:
            if callerObject.getActiveObjectQueue()[0].type=='Part':
                return not activeObject.entryIsAssignedTo()
        return False
            
    #===========================================================================
    # checks if the Assembly can accept a part or a Frame
    #===========================================================================
    def canAcceptAndIsRequested(self, callerObject=None):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        if(len(giverObject.getActiveObjectQueue())>0):
            #activate only if the caller carries Frame
            if(giverObject.getActiveObjectQueue()[0].type=='Frame'):
                return len(activeObjectQueue)==0 and giverObject.haveToDispose(activeObject)
            #activate only if the caller carries Part
            if(giverObject.getActiveObjectQueue()[0].type=='Part'):
                return len(activeObjectQueue)==1 and giverObject.haveToDispose(activeObject)
        return False

    #===========================================================================
    # checks if the Assembly can dispose an entity to the following object     
    #===========================================================================
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()     
        
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(callerObject==None):
            return len(activeObjectQueue)>0 
         
        thecaller=callerObject
        return len(activeObjectQueue)>0 and (thecaller in activeObject.next) and activeObject.waitToDispose
                                               
    #===========================================================================
    # removes an entity from the Assembly
    #===========================================================================
    def removeEntity(self, entity=None):
        activeEntity=CoreObject.removeEntity(self, entity)               #run the default method
        self.waitToDispose=False
        if self.canAccept():
            self.printTrace(self.id, attemptSignalGiver='(removeEntity)')
            self.signalGiver()
        return activeEntity
    
    #===========================================================================
    # gets an entity from the giver   
    # it may handle both Parts and Frames  
    #===========================================================================
    def getEntity(self, type):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        giverObject.sortEntities()      #sort the Entities of the giver according to the scheduling rule if applied
        giverObjectQueue=self.getGiverObjectQueue()
        # if the giverObject is blocked then unBlock it
        if giverObject.exitIsAssignedTo():
            giverObject.unAssignExit()
        # if the activeObject entry is blocked then unBlock it
        if activeObject.entryIsAssignedTo():
            activeObject.unAssignEntry()
        
        activeEntity=self.identifyEntityToGet()
        assert activeEntity.type==type, 'the type of the entity to get must be of type '+type+' while it is '+activeEntity.type
        #remove the entity from the previews object
        giverObject.removeEntity(activeEntity)     
        self.printTrace(activeEntity.name, enter=self.id)
        self.outputTrace(activeEntity.name, "got into "+ self.objName)
        # if the type is Frame 
        if(activeEntity.type=="Frame"):
            self.nameLastEntityEntered=activeEntity.name
            self.timeLastEntityEntered=self.env.now
        activeEntity.currentStation=self
        
        # if the frame is not fully loaded then signal a giver
        if len(activeObjectQueue[0].getFrameQueue())<activeObjectQueue[0].capacity:
            self.printTrace(self.id, attemptSignalGiver='(getEntity)')
            self.signalGiver()
        return activeEntity
    
    #===========================================================================
    # appends entity to the receiver object. to be called by the removeEntity of the giver
    # this method is created to be overridden by the Assembly class in its getEntity where Frames are loaded
    #===========================================================================
    def appendEntity(self,entity=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        assert entity, 'the entity to be appended cannot be None'
        if entity.type=='Part':
            activeObjectQueue[0].getFrameQueue().append(entity)       #get the part from the giver and append it to the frame!
        elif entity.type=='Frame':
            activeObjectQueue.append(entity)                                #get the frame and append it to the internal queue
  
        
       
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
