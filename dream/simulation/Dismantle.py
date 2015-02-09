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
Created on 21 May 2013

@author: George
'''
'''
Models a dismantle object 
it gathers frames that have parts loaded, unloads the parts and sends the frame to one destination and the parts to another
'''

# from SimPy.Simulation import Process, Resource
# from SimPy.Simulation import waitevent, now, hold, infinity
import simpy
import xlwt
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject

#===============================================================================
# the Dismantle object
#===============================================================================
class Dismantle(CoreObject):
    class_name = 'Dream.Dismantle'
    #===========================================================================
    # initialize the object
    #===========================================================================
    def __init__(self, id='', name='', processingTime=None,**kw):
        
        self.type='Dismantle'
        self.previous=[]        #list with the previous objects in the flow
        self.previousIds=[]     #list with the ids of the previous objects in the flow
        self.nextPart=[]    #list with the next objects that receive parts
        self.nextFrame=[]    #list with the next objects that receive frames 
        self.nextIds=[]     #list with the ids of the next objects in the flow
        self.nextPartIds=[]     #list with the ids of the next objects that receive parts 
        self.nextFrameIds=[]     #list with the ids of the next objects that receive frames 
        self.next=[]
        
        #lists to hold statistics of multiple runs
        self.Waiting=[]
        self.Working=[]
        self.Blockage=[]
        
        # variable that is used for the loading of machines 
        self.exitAssignedToReceiver = False             # by default the objects are not blocked 
                                                        # when the entities have to be loaded to operatedMachines
                                                        # then the giverObjects have to be blocked for the time
                                                        # that the machine is being loaded 
        CoreObject.__init__(self, id, name)
        from Globals import G
        if not processingTime:
            processingTime = {'Fixed':{'mean': 0 }}
        if 'Normal' in processingTime.keys() and\
                processingTime['Normal'].get('max', None) is None:
            processingTime['Normal']['max'] = float(processingTime['Normal']['mean']) + 5 * float(processingTime['Normal']['stdev'])

        self.rng=RandomNumberGenerator(self, processingTime)   
                                    
    #===========================================================================
    # the initialize method
    #===========================================================================
    def initialize(self):
        CoreObject.initialize(self)
        self.waitToDispose=False    #flag that shows if the object waits to dispose an entity    
        self.waitToDisposePart=False    #flag that shows if the object waits to dispose a part   
        self.waitToDisposeFrame=False    #flag that shows if the object waits to dispose a frame   
        
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
        self.Res=simpy.Resource(self.env, capacity='inf')    
        self.Res.users=[]  
#         self.Res.waitQ=[]
        
    #===========================================================================
    # the run method
    #===========================================================================
    def run(self):
        activeObjectQueue=self.getActiveObjectQueue()
        while 1:
#             self.printTrace(self.id, waitEvent='(frame)')
            # wait until the Queue can accept an entity and one predecessor requests it
            
            self.expectedSignals['isRequested']=1
            
            yield self.isRequested     #[self.isRequested,self.canDispose, self.loadOperatorAvailable]
            if self.isRequested.value:
#                 self.printTrace(self.id, isRequested=self.isRequested.value.id)
                # reset the isRequested signal parameter
                self.isRequested=self.env.event()
            
            
                self.getEntity()                                 #get the Frame with the parts 
                self.timeLastEntityEntered=self.env.now
                startWorkingTime=self.env.now
                self.isProcessing=True
                self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()
                #hold for the time the assembly operation is carried
                yield self.env.timeout(self.totalProcessingTimeInCurrentEntity)
                self.isProcessing=False
                self.totalWorkingTime+=self.env.now-startWorkingTime
                self.timeLastEntityEnded=self.env.now
                
                self.timeLastBlockageStarted=self.env.now
                self.isBlocked=True
                self.completedJobs+=1                       #Assembly completed a job
                
                self.waitToDispose=True
                self.waitToDisposePart=True     #Dismantle is in state to dispose a part
                # while the object still holds the frame
                flag=False
                while not self.isEmpty():
                    
                    self.expectedSignals['canDispose']=1
                    
                    # try and signal the receiver
                    if not self.signalReceiver():
                        # if not possible, then wait till a receiver is available
                        yield self.canDispose
                        self.canDispose=self.env.event()
                        # and signal it again
                        if not self.signalReceiver():
                            continue
                    # if the receiver was not responsive, release the control to let him remove the entity
                    self.waitEntityRemoval=True
                    
                    self.expectedSignals['entityRemoved']=1
                    
                    yield self.entityRemoved
                    self.waitEntityRemoval=False
                    self.entityRemoved=self.env.event()

                    if self.frameIsEmpty() and not self.waitToDisposeFrame:
                        self.waitToDisposePart=False
                        self.waitToDisposeFrame=True
                    # if the internal queue is empty then update the corresponding flags and proceed with getting a new entity
                    if self.isEmpty():
                        self.waitToDisposeFrame=False                     #the Dismantle has no Frame to dispose now
                        break

        
    #===========================================================================
    #    checks if the Dismantle can accept an entity and there is a Frame 
    #                             waiting for it
    #===========================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        return len(activeObjectQueue)==0 and giverObject.haveToDispose(activeObject) 
    
    #===========================================================================
    # checks if the Dismantle can accept an entity 
    #===========================================================================
    def canAccept(self, callerObject=None):
        thecaller=callerObject
        # if there is no caller return True only when the internal queue is empty
        if not thecaller:
            return len(self.getActiveObjectQueue())==0
        # otherrwise check additionally if the caller is in the previous list
        return len(self.getActiveObjectQueue())==0 and (callerObject in self.previous)
    
    #===========================================================================
    # defines where parts and frames go after they leave the object
    #===========================================================================               
    def definePartFrameRouting(self, successorPartList=[], successorFrameList=[]):
        self.nextPart=successorPartList
        self.nextFrame=successorFrameList
    
    #===========================================================================
    # checks if the caller waits for a part or a frame and if the Dismantle 
    # is in the state of disposing one it returnse true
    #===========================================================================     
    def haveToDispose(self, callerObject=None): 
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()     
        
        thecaller=callerObject
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(thecaller==None):
            return len(activeObjectQueue)>0 
        
        #according to the caller return true or false
        if thecaller in self.nextPart:
            if len(self.getActiveObjectQueue())>1 and self.waitToDisposePart:
                return True
        elif thecaller in self.nextFrame:
            if len(self.getActiveObjectQueue())==1 and self.waitToDisposeFrame:
                return True
        return False
    
    #===========================================================================
    # find possible receivers
    #===========================================================================
    @staticmethod
    def findReceiversFor(activeObject):
#         activeObject=self.getActiveObject()
        next=[]
        receivers=[]
        # if the parts are not yet disposed
        if not activeObject.frameIsEmpty():
            # search for receivers within the nextPart list
            next=activeObject.nextPart
        else:
            # otherwise search within the nextFrame list
            next=activeObject.nextFrame
        for object in [x for x in next if x.canAccept(activeObject)]:
            receivers.append(object)
        return receivers
    
    #===========================================================================
    # checks if the frame is emptied
    #===========================================================================
    def frameIsEmpty(self):
        return len(self.getActiveObjectQueue())==1
    
    #===========================================================================
    # checks if Dismantle is emptied
    #===========================================================================
    def isEmpty(self):
        return len(self.getActiveObjectQueue())==0
    
    # =======================================================================
    # gets a frame from the giver 
    # =======================================================================
    def getEntity(self):
        activeEntity=CoreObject.getEntity(self)     #run the default method
        activeObjectQueue=self.getActiveObjectQueue()
        #get also the parts of the frame so that they can be popped
        for part in activeEntity.getFrameQueue():         
            activeObjectQueue.append(part)
            part.currentStation=self
        activeEntity.getFrameQueue=[]           #empty the frame
        
        #move the frame to the end of the internal queue since we want the frame to be disposed first
        activeObjectQueue.append(activeEntity)
        activeObjectQueue.pop(0)        
        return activeEntity
    
    #===========================================================================
    # removes an entity from the Dismantle
    #===========================================================================
    def removeEntity(self, entity=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        #run the default method 
        activeEntity=CoreObject.removeEntity(self, entity, resetFlags=False, addBlockage=False)  
        #update the flags
        if(len(activeObjectQueue)==0):  
            activeObject.waitToDisposeFrame=False
            self.isBlocked=False
            self.isProcessing=False
            self.addBlockage() 
        else:
            if(len(activeObjectQueue)==1):   
               activeObject.waitToDisposePart=False
        # if the internal queue is empty then try to signal the giver that the object can now receive
        if activeObject.canAccept():
            activeObject.printTrace(self.id, attemptSignalGiver='(removeEntity)')
            activeObject.signalGiver()
        return activeEntity
               
    #===========================================================================
    #                  outputs message to the trace.xls. 
    #       Format is (Simulation Time | Entity or Frame Name | message)
    #===========================================================================
    def outputTrace(self, name, message):
        from Globals import G
        if(G.trace=="Yes"):         #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(self.env.now))
            G.traceSheet.write(G.traceIndex,1,name)  
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1       #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)  
        
    
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
