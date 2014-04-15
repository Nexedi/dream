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

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, waituntil, now, hold, waitevent


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
    # =======================================================================
    #initialize the id, the capacity of the object and the distribution
    # =======================================================================        
    def __init__(self, id, name, numberOfSubBatches=1, processingTime=None, operator='None'):
        CoreObject.__init__(self,id, name)
        self.type="BatchRassembly"              #String that shows the type of object
        if not processingTime:
          processingTime = { 'distributionType': 'Fixed',
                             'mean': 1, }
        if processingTime['distributionType'] == 'Normal' and\
              processingTime.get('max', None) is None:
          processingTime['max'] = processingTime['mean'] + 5 * processingTime['stdev']
          
        # holds the capacity of the object 
        self.numberOfSubBatches=numberOfSubBatches
        # sets the operator resource of the Machine
        self.operator=operator         
        # Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, **processingTime)

    # =======================================================================
    #     initialize the internal resource of the object
    # =======================================================================
    def initialize(self):
        CoreObject.initialize(self)                 # using the default CoreObject Functionality
        self.Res=Resource(self.numberOfSubBatches)  # initialize the Internal resource (Queue) functionality
            
    # =======================================================================
    #     the main method of the object
    # =======================================================================
    def run(self):
        activeObjectQueue=self.getActiveObjectQueue()
        # check if there is WIP and signal receiver
        self.initialSignalReceiver()
        while 1:
            while 1:
                yield waitevent, self, [self.isRequested, self.interruptionStart]
                if self.interruptionStart.signalparam==now():
                    yield waitevent, self, self.interruptionEnd
                    assert self==self.interruptionEnd.signalparam, 'the victim of the failure is not the object that received the interruptionEnd event'
                    if self.signalGiver():
                        break
                else:
                    break
            requestingObject=self.isRequested.signalparam
            assert requestingObject==self.giver, 'the giver is not the requestingObject'
            
#             self.operatorWaitTimeCurrentEntity = 0
#             self.loadOperatorWaitTimeCurrentEntity = 0
#             self.loadTimeCurrentEntity = 0
#             self.setupTimeCurrentEntity = 0
            
#             yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity
#                                                                     #and one predecessor requests it
            self.currentEntity=self.getEntity()
            
            # self.outputTrace("got into "+self.objName)
            
            # set the currentEntity as the Entity just received and initialize the timer timeLastEntityEntered
#             self.currentEntity=self.getActiveObjectQueue()[0]       # entity is the current entity processed in object
            self.nameLastEntityEntered=self.currentEntity.name      # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=now()                        #this holds the last time that an entity got into Machine  
            
#             self.tinM=self.totalProcessingTimeInCurrentEntity                                          # timer to hold the processing time left
            
            if len(self.getActiveObjectQueue())==self.numberOfSubBatches and self.currentEntity.type!='Batch':
                yield hold,self,self.calculateProcessingTime()
                self.reassemble()
                if not self.signalReceiver():
                    while 1:
                        event=yield waitevent, self, [self.canDispose, self.interruptionStart]
                        if self.interruptionStart.signalparam==now():
                            yield waitevent, self, self.interruptionEnd
                            assert self==self.interruptionEnd.signalparam
                        if self.signalReceiver():
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
        # if the activeEntity is hot then the subBatches should be also hot
        batchToBeReassembled.hot=activeObjectQueue[0].hot
        # if the activeEntity is in the pendingEntities list then place the subBatches there
        if activeObjectQueue[0] in G.pendingEntities:
            G.pendingEntities.append(batchToBeReassembled)
            for entity in activeObjectQueue:
                G.pendingEntities.remove(entity)
        
        del activeObjectQueue[:]
        batchToBeReassembled.numberOfSubBatches = 1
        batchToBeReassembled.numberOfUnits=numberOfUnits
        activeObjectQueue.append(batchToBeReassembled)
        batchToBeReassembled.currentStation=self
        self.timeLastEntityEnded=now()
        self.outputTrace(batchToBeReassembled.name, 'was reassembled')
        
    # =======================================================================
    #     returns True if the object doensn't hold entities of type Batch
    # and if the subBatches in the its internal queue and the one of the giver
    # hold subBatches of the same batchId
    # =======================================================================
    def canAccept(self,callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        if len(activeObject.previous)!=1:
            assert callerObject!=None, 'the callerObject cannot be None for canAccept of BatchReassembly'
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
        
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQueue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        return len(activeObjectQueue)<self.numberOfSubBatches\
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
    def canAcceptAndIsRequested(self):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        giverObjectQueue=self.getGiverObjectQueue()
        
        if (len(activeObjectQueue)==0):
            return activeObject.Up and giverObject.haveToDispose(activeObject)
        else:
            return activeObject.Up and giverObject.haveToDispose(activeObject)\
                and len(activeObjectQueue)<activeObject.numberOfSubBatches\
                and activeObjectQueue[0].type!='Batch'\
                and giverObjectQueue[0].batchId==activeObjectQueue[0].batchId
        