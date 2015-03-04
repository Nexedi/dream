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
Created on 29 Oct 2013

@author: Ioannis
'''
'''
BatchReassembly is a Core Object that takes a number of subBatches and reassembles them to the parent Batch
'''

# from SimPy.Simulation import Process, Resource
# from SimPy.Simulation import activate, waituntil, now, hold, waitevent
import simpy

from Globals import G
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject
# from Entity import Entity

from SubBatch import SubBatch
from Batch import Batch

# ===========================================================================
# the Batch-Reassembly Object
# ===========================================================================
class BatchReassembly(CoreObject):
    family='Server'
    # =======================================================================
    #initialize the id, the capacity of the object and the distribution
    # =======================================================================        
    def __init__(self, id, name, numberOfSubBatches=1, processingTime=None, operator='None', outputResults=False, **kw):
        CoreObject.__init__(self,id, name)
        self.type="BatchRassembly"              #String that shows the type of object
        if not processingTime:
            processingTime = {'Fixed':{'mean': 0 }}
        if 'Normal' in processingTime.keys() and\
                processingTime['Normal'].get('max', None) is None:
            processingTime['Normal']['max'] = float(processingTime['Normal']['mean']) + 5 * float(processingTime['Normal']['stdev'])
          
        # holds the capacity of the object 
        self.numberOfSubBatches=numberOfSubBatches
        # sets the operator resource of the Machine
        self.operator=operator         
        # Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, processingTime)
        from Globals import G
        G.BatchReassemblyList.append(self)
        # flag to show if the objects outputs results
        self.outputResults=bool(int(outputResults))

    # =======================================================================
    #     initialize the internal resource of the object
    # =======================================================================
    def initialize(self):
        CoreObject.initialize(self)                 # using the default CoreObject Functionality
        self.Res=simpy.Resource(self.env, self.numberOfSubBatches)  # initialize the Internal resource (Queue) functionality
        
        self.expectedSignals['isRequested']=1
        self.expectedSignals['interruptionStart']=1
        self.expectedSignals['initialWIP']=1
            
    # =======================================================================
    #     the main method of the object
    # =======================================================================
    def run(self):
        activeObjectQueue=self.getActiveObjectQueue()
        while 1:           
            while 1:
                self.expectedSignals['isRequested']=1
                self.expectedSignals['interruptionStart']=1
                self.expectedSignals['initialWIP']=1
                receivedEvent=yield self.env.any_of([self.isRequested , self.interruptionStart , self.initialWIP])
                if self.interruptionStart in receivedEvent:
                    transmitter, eventTime=self.interruptionStart.value
                    assert eventTime==self.env.now, 'the interruptionStart received by BatchReassembly later than created'
                    self.interruptionStart=self.env.event()
                    
                    self.expectedSignals['interruptionEnd']=1
                    
                    yield self.interruptionEnd
                    
                    transmitter, eventTime=self.interruptionEnd.value
                    assert self==transmitter, 'the victim of the failure is not the object that received the interruptionEnd event'
                    self.interruptionEnd=self.env.event()
                    if self.signalGiver():
                        break
                # if we have initial wip
                elif self.initialWIP in receivedEvent:
                    transmitter, eventTime=self.initialWIP.value
                    assert transmitter==self.env, 'initial wip was not sent by the Environment'
                    self.initialWIP=self.env.event()
                    self.isProcessingInitialWIP=True
                    break  
                # otherwise proceed with getEntity
                else:
                    requestingObject, eventTime=self.isRequested.value
                    assert requestingObject==self.giver, 'the giver is not the requestingObject'
                    self.isRequested=self.env.event()
                    self.isProcessingInitialWIP=False
                    break
            
            if not self.isProcessingInitialWIP:     # if we are in the state of having initial wip no need to take an Entity
                self.currentEntity=self.getEntity()            
                
            # initialize the timer timeLastEntityEntered
            self.nameLastEntityEntered=self.currentEntity.name              # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=self.env.now                         #this holds the last time that an entity got into Machine  
                       
            if (len(self.getActiveObjectQueue())==self.numberOfSubBatches and self.currentEntity.type!='Batch')\
                    or (self.isProcessingInitialWIP and self.currentEntity.type=='Batch'):  # this needed for initial 
                                                                                            # WIP that may be batch
                # Reassemble only if current entity is SubBatch
                if self.currentEntity.type=='SubBatch':
                    yield self.env.timeout(self.calculateProcessingTime())
                    self.reassemble()
                self.isProcessingInitialWIP=False
                # signal the receiver that the activeObject has something to dispose of
                self.timeLastBlockageStarted=self.env.now 
                self.isBlocked=True                  
                if not self.signalReceiver():
                # if there was no available receiver, get into blocking control
                    while 1:
    #                     self.timeLastBlockageStarted=self.env.now       # blockage is starting
                        # wait the event canDispose, this means that the station can deliver the item to successor
                        self.printTrace(self.id, waitEvent='(canDispose or interruption start)')
                        self.expectedSignals['interruptionStart']=1
                        self.expectedSignals['canDispose']=1
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
                        # notify that the station waits the entity to be removed
                        if not self.haveToDispose():
                            break
                        self.waitEntityRemoval=True
                        self.printTrace(self.id, waitEvent='(entityRemoved)')
                        
                        self.expectedSignals['entityRemoved']=1
                        
                        yield self.entityRemoved
                        
                        transmitter, eventTime=self.entityRemoved.value
                        self.printTrace(self.id, entityRemoved=eventTime)
                        assert eventTime==self.env.now,'entityRemoved event activated earlier than received'
                        self.waitEntityRemoval=False
                        self.entityRemoved=self.env.event()
                        # if while waiting (for a canDispose event) became free as the machines that follows emptied it, then proceed
                        if not self.haveToDispose():
                            break

    # =======================================================================
    # removes an entity from the Machine
    # =======================================================================
    def removeEntity(self, entity=None):
        activeObject=self.getActiveObject()
        activeEntity=CoreObject.removeEntity(self, entity)          # run the default method     
        activeObject.waitToDispose=False                            # update the waitToDispose flag
        if activeObject.canAccept():
            activeObject.signalGiver()
        return activeEntity
        
    # =======================================================================
    #     reassemble method that assembles the subBatches back together to a Batch
    # =======================================================================
    def reassemble(self):
        activeObject = self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()    # get the internal queue of the active core object
        
        curSubBatchId = 0
        nextSubBatchId = 0
        for i in range(len(activeObjectQueue)-1):
            curSubBatchId = activeObjectQueue[i].batchId
            nextSubBatchId = activeObjectQueue[i+1].batchId
            assert curSubBatchId == nextSubBatchId,\
             'The subBatches in the re-assembly station are not of the same Batch'
        
        #calculate the number of units of the Batch
        numberOfUnits=0
        for subBatch in activeObjectQueue:
            numberOfUnits+=subBatch.numberOfUnits
        # the batch to be reassembled
        batchToBeReassembled = activeObjectQueue[0].parentBatch
        # if the activeEntity is in the pendingEntities list then place the subBatches there
        if activeObjectQueue[0] in G.pendingEntities:
            G.pendingEntities.append(batchToBeReassembled)
            if G.RouterList:
                for entity in activeObjectQueue:
                    G.pendingEntities.remove(entity)
        
        del activeObjectQueue[:]
        batchToBeReassembled.numberOfSubBatches = 1
        batchToBeReassembled.numberOfUnits=numberOfUnits
        activeObjectQueue.append(batchToBeReassembled)
        batchToBeReassembled.currentStation=self
        self.timeLastEntityEnded=self.env.now
        self.outputTrace(batchToBeReassembled.name, 'was reassembled')
        
    # =======================================================================
    #     returns True if the object doensn't hold entities of type Batch
    # and if the subBatches in the its internal queue and the one of the giver
    # hold subBatches of the same batchId
    # =======================================================================
    def canAccept(self,callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        # if there is only one predecessor
        if(len(activeObject.previous)==1):
            # find the predecessor object and its queue
            predecessor=activeObject.previous[0]
            predecessorQueue=predecessor.getActiveObjectQueue()
            if len(activeObjectQueue)==0:
                return activeObject.Up
            elif len(predecessorQueue)==0:
                return False
            else:
                return activeObject.Up\
                     and activeObjectQueue[0].type!='Batch'\
                     and len(activeObjectQueue)<self.numberOfSubBatches\
                     and predecessorQueue[0].batchId==activeObjectQueue[0].batchId
        # if there is no caller defined - self.canAccept from getEntity         
        if not callerObject:
            return activeObject.Up\
                and len(activeObjectQueue)<self.numberOfSubBatches
        
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQueue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        if len(activeObjectQueue)==0:
            return activeObject.Up\
                and (thecaller in activeObject.previous)
        else:
            return activeObject.Up\
                and len(activeObjectQueue)<self.numberOfSubBatches\
                and (thecaller in activeObject.previous)\
                and activeObjectQueue[0].type != 'Batch'\
                and thecaller.getActiveObjectQueue()[0].batchId==activeObjectQueue[0].batchId

    # =======================================================================
    #     returns True if it holds an entity of type Batch
    # =======================================================================
    def haveToDispose(self,callerObject=None):
        # get active and the receiver object
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()    
        #if we have only one successor just check if object waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            return len(activeObjectQueue)==1\
                    and activeObjectQueue[0].type=="Batch" # the control of the length of the queue is not needed
        
        thecaller=callerObject 
        return len(activeObjectQueue)==1\
                and (thecaller in activeObject.next)\
                and activeObjectQueue[0].type!="Batch" # the control of the length of the queue is not needed
            
    # =======================================================================
    #     returns true if the giver has an entity to dispose 
    # which is of the same batchId as the ones that the assembler currently holds 
    # (if it holds any), and if doesn't hold any entities of type Batch 
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
#         giverObject=self.getGiverObject()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        giverObjectQueue=giverObject.getActiveObjectQueue()
        
        if (len(activeObjectQueue)==0):
            return activeObject.Up and giverObject.haveToDispose(activeObject)
        else:
            return activeObject.Up and giverObject.haveToDispose(activeObject)\
                and len(activeObjectQueue)<activeObject.numberOfSubBatches\
                and activeObjectQueue[0].type!='Batch'\
                and giverObjectQueue[0].batchId==activeObjectQueue[0].batchId
                
    # =======================================================================
    # outputs results to JSON File 
    # =======================================================================
    def outputResultsJSON(self):
        if self.outputResults:
            from Globals import G
            json = {'_class': 'Dream.%s' % self.__class__.__name__,
                    'id': self.id,
                    'family': self.family,
                    'results': {}}
            json['results']['failure_ratio'] = self.Failure
            json['results']['working_ratio'] = self.Working
            json['results']['blockage_ratio'] = self.Blockage
            json['results']['waiting_ratio'] = self.Waiting
            json['results']['off_shift_ratio'] = self.OffShift
            G.outputJSON['elementList'].append(json)
        
        
        