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
BatchDecomposition is a Core Object that takes a batch and decomposes to sub-batches
'''


from SimPy.Simulation import Process, Resource
from SimPy.Simulation import waituntil, now, hold, waitevent

from Globals import G
from CoreObject import CoreObject
from RandomNumberGenerator import RandomNumberGenerator

from SubBatch import SubBatch
from Batch import Batch


# ===========================================================================
# the Batch-Decomposition Object
# ===========================================================================
class BatchDecomposition(CoreObject):
    # =======================================================================
    #initialize the id, the capacity of the object and the distribution
    # =======================================================================        
    def __init__(self, id, name, processingTime=None, numberOfSubBatches=1, operator='None'):
        CoreObject.__init__(self, id, name)
        self.type="BatchDecomposition"              #String that shows the type of object

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
        from Globals import G
        G.BatchWaitingList = []                     # batches waiting to be reassembled
        CoreObject.initialize(self)                 # using the default CoreObject Functionality
        self.Res=Resource(self.numberOfSubBatches)  # initialize the Internal resource (Queue) functionality
            
    # =======================================================================
    #     the run method of the BatchDecomposition
    # =======================================================================
    def run(self):
        while 1:
            # wait for an event or an interruption
            while 1:
                yield waitevent, self, [self.isRequested, self.interruptionStart]
                # if an interruption has occurred 
                if self.interruptionStart.signalparam==now():
                    # wait till it is over
                    yield waitevent, self, self.interruptionEnd
                    assert self==self.interruptionEnd.signalparam, 'the victim of the failure is not the object that received the interruptionEnd event'
                    if self.signalGiver():
                        break
                # otherwise proceed with getEntity
                else:
                    break
            requestingObject=self.isRequested.signalparam
            assert requestingObject==self.giver, 'the giver is not the requestingObject'
                                                              
            self.currentEntity=self.getEntity()
            # set the currentEntity as the Entity just received and initialize the timer timeLastEntityEntered
            self.nameLastEntityEntered=self.currentEntity.name      # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=now()                        #this holds the last time that an entity got into Machine  
            
            self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()
            
            yield hold,self,self.totalProcessingTimeInCurrentEntity
            self.decompose()
            
            # TODO: add failure control
            # as long as there are sub-Batches in the internal Resource
            for i in range(self.numberOfSubBatches):
                # added here temporarily, it is supposed to break when i==numberOfSubBatches
                if not self.getActiveObjectQueue():
                    break
                # if the loop is run for the first time (i=0)
                if i==0:
                    # try to signal the receiver
                    signaling=self.signalReceiver()
                    if not signaling:
                        # if there was no success wait till the receiver is available
                        while 1:
                            yield waitevent, self, self.canDispose
                            # signal the receiver again and break
                            if self.signalReceiver():
                                break
                # for the consecutive times wait till the receiver is available and then signalReceiver
                #     we know that the receiver is occupied with the previous sub-batch
                else:
                    while 1:
                        yield waitevent,self,self.canDispose
                        signaling=self.signalReceiver()
                        if signaling:
                            break
        
    # =======================================================================
    #     method that decomposes the activeEntity into subBatches
    # =======================================================================
    def decompose(self):                #, activeEntity=None):
        # maybe I can use as argument the activeEntity passing the getEntity as argument to this function in the run function
        # for example
        # self.decompose(self.getEntity)
#         assert activeEntity!=none, 'decompose method cannot decompose None'
        activeObject = self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()    #get the internal queue of the active core object
        activeEntity = activeObjectQueue.pop()
        
        batchNumberOfUnits = activeEntity.numberOfUnits
        alreadyAllocatedUnits=0

        #the number of units of its sub-batch is calculated
        #for example: 
        #if the total is 99 and we have 4 sub-batches it should be [25,25,25,24]
        #if the total is 94 and we have 4 sub-batches it should be [24,24,24,22]
        for i in range(self.numberOfSubBatches):
            if i==self.numberOfSubBatches-1:
                numberOfSubBatchUnits=batchNumberOfUnits-alreadyAllocatedUnits
            elif activeEntity.numberOfUnits%self.numberOfSubBatches==0:
                numberOfSubBatchUnits = batchNumberOfUnits//self.numberOfSubBatches
            else:
                numberOfSubBatchUnits = batchNumberOfUnits//self.numberOfSubBatches+1
            alreadyAllocatedUnits+=numberOfSubBatchUnits
            subBatch=SubBatch(str(activeEntity.id)+'_'+str(i), activeEntity.name+"_SB_"\
                            +str(i), numberOfUnits=numberOfSubBatchUnits,
                            parentBatch=activeEntity)    #create the sub-batch
            self.outputTrace(subBatch.name,'was created from '+ activeEntity.name)
            #===================================================================
            # TESTING
#             print now(), subBatch.name,'was created from '+ activeEntity.name
            #===================================================================
            G.EntityList.append(subBatch)
            activeObjectQueue.append(subBatch)                          #append the sub-batch to the active object Queue
            activeEntity.subBatchList.append(subBatch)
            subBatch.currentStation=self
            # if the activeEntity is hot then the subBatches should be also hot
            subBatch.hot=activeEntity.hot
            # if the activeEntity is in the pendingEntities list then place the subBatches there
            if activeEntity in G.pendingEntities:
                G.pendingEntities.append(subBatch)
                G.pendingEntities.remove(activeEntity)
        activeEntity.numberOfSubBatches=self.numberOfSubBatches
        self.timeLastEntityEnded=now()

    # =======================================================================
    #     canAccept logic
    # =======================================================================
    def canAccept(self,callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
#         giverObject=self.getGiverObject()
        if(len(activeObject.previous)==1 or callerObject==None):      
            return activeObject.Up and len(activeObjectQueue)==0
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        return activeObject.Up and len(activeObjectQueue)==0 and (thecaller in activeObject.previous)
    
    # =======================================================================
    #     haveToDispose logic
    # =======================================================================
    def haveToDispose(self,callerObject=None):
        # get active and the receiver object
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()    
        #if we have only one successor just check if object waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            return len(activeObjectQueue)>0 and activeObjectQueue[0].type!="Batch" and activeObject.Up
        
        thecaller=callerObject
        return len(activeObjectQueue)==self.numberOfSubBatches and \
            (thecaller in activeObject.next) and activeObjectQueue[0].type!="Batch" and activeObject.Up
    
    # =======================================================================
    #     canAcceptAndIsRequested logc
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        
        return activeObject.Up and len(activeObjectQueue)==0 and giverObject.haveToDispose(activeObject)
