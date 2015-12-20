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


# from SimPy.Simulation import Process, Resource
# from SimPy.Simulation import waituntil, now, hold, waitevent
import simpy

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
    def __init__(self, id, name, processingTime=None, numberOfSubBatches=1, operator='None', **kw):
        CoreObject.__init__(self, id, name)
        self.type="BatchDecomposition"              #String that shows the type of object

        if not processingTime:
            processingTime = {'Fixed':{'mean': 0 }}
        if 'Normal' in processingTime.keys() and\
                processingTime['Normal'].get('max', None) is None:
            processingTime['Normal']['max'] = float(processingTime['Normal']['mean']) + 5 * float(processingTime['Normal']['stdev'])
        
        # holds the capacity of the object 
        self.numberOfSubBatches=int(numberOfSubBatches)
        # sets the operator resource of the Machine
        self.operator=operator         
        # Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, processingTime)
        from Globals import G
        G.BatchDecompositionList.append(self)

    # =======================================================================
    #     initialize the internal resource of the object
    # =======================================================================
    def initialize(self):
        from Globals import G
        G.BatchWaitingList = []                                     # batches waiting to be reassembled
        CoreObject.initialize(self)                                 # using the default CoreObject Functionality
        self.Res=simpy.Resource(self.env, self.numberOfSubBatches)  # initialize the Internal resource (Queue) functionality
        
        self.expectedSignals['isRequested']=1
        self.expectedSignals['interruptionStart']=1
        self.expectedSignals['initialWIP']=1
            
    # =======================================================================
    #     the run method of the BatchDecomposition
    # =======================================================================
    def run(self):
        while 1:
            # wait for an event or an interruption               
            while 1:
                self.expectedSignals['isRequested']=1
                self.expectedSignals['interruptionStart']=1
                self.expectedSignals['initialWIP']=1
                self.printTrace(self.id, waitEvent='(isRequested), interruptionStart, initialWIP')
                receivedEvent=yield self.env.any_of([self.isRequested , self.interruptionStart , self.initialWIP])
                # if an interruption has occurred 
                if self.interruptionStart in receivedEvent:
                    transmitter, eventTime=self.interruptionStart.value
                    assert eventTime==self.env.now, 'the interruption received by batchDecomposition was created earlier'
                    self.interruptionStart=self.env.event()
                    # wait till it is over
                    
                    self.expectedSignals['interruptionEnd']=1
                    self.printTrace(self.id, waitEvent='interruptionEnd')
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
                    self.printTrace(self.id, isRequested=requestingObject.id)
                    self.isRequested=self.env.event()
                    break
           
            if not self.isProcessingInitialWIP:     # if we are in the state of having initial wip no need to take an Entity
                self.currentEntity=self.getEntity()
                
            # set the currentEntity as the Entity just received and initialize the timer timeLastEntityEntered
            self.nameLastEntityEntered=self.currentEntity.name      # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=self.env.now                 #this holds the last time that an entity got into Machine  
            
            # if we have batch in the decomposition (initial wip may be in sub-batch)
            if self.getActiveObjectQueue()[0].__class__.__name__=='Batch':     
                self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()
                yield self.env.timeout(self.totalProcessingTimeInCurrentEntity)
                self.decompose()
            
            # reset the variable
            self.isProcessingInitialWIP=False
                      
            # TODO: add failure control
            # as long as there are sub-Batches in the internal Resource
            while len(self.getActiveObjectQueue()):
                if len(self.getActiveObjectQueue()) == 1 and self.next[0].isRequested.triggered:
                    break
                # if the entity was just obtained
                if self.timeLastEntityEntered == self.env.now:
                    # try to signal the receiver
                    signaling=self.signalReceiver()
                    if not signaling:
                        # if there was no success wait till the receiver is available
                        while 1:
                            self.printTrace(self.id, waitEvent='canDispose')
                            self.expectedSignals['canDispose']=1
                            yield self.canDispose
                            self.printTrace(self.id, canDispose='')
                            transmitter, eventTime=self.canDispose.value
                            self.canDispose=self.env.event()
                            # signal the receiver again and break
                            if self.signalReceiver():
                                self.waitEntityRemoval=True
                                
                                self.expectedSignals['entityRemoved']=1
                                self.printTrace(self.id, waitEvent='entityRemoved')
                                yield self.entityRemoved
                                self.printTrace(self.id, received='')
                                transmitter, eventTime=self.entityRemoved.value
                                self.waitEntityRemoval=False
                            break
                
                # for the consecutive times wait till the receiver is available and then signalReceiver
                #     we know that the receiver is occupied with the previous sub-batch
                else:
                    if not self.signalReceiver():
                        while 1:
                            self.printTrace(self.id, waitEvent='canDispose')# or entityRemoved')
                            self.expectedSignals['canDispose']=1
                            yield self.canDispose
                            self.printTrace(self.id, canDispose='')
                            transmitter, eventTime=self.canDispose.value
                            self.canDispose=self.env.event()
                            if not self.getActiveObjectQueue():
                                break
                            signaling=self.signalReceiver()
                            if signaling:
                                self.waitEntityRemoval=True
                                
                                self.expectedSignals['entityRemoved']=1
                                self.printTrace(self.id, waitEvent='entityRemoved')
                                yield self.entityRemoved
                                self.printTrace(self.id, received='entityRemoved')
                                transmitter, eventTime=self.entityRemoved.value
                                self.waitEntityRemoval=False
                                break

                self.entityRemoved=self.env.event()
            
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
#             print self.env.now, subBatch.name,'was created from '+ activeEntity.name
            #===================================================================
            G.EntityList.append(subBatch)
            activeObjectQueue.append(subBatch)                          #append the sub-batch to the active object Queue
            #activeEntity.subBatchList.append(subBatch)
            subBatch.currentStation=self
            # if the activeEntity is in the pendingEntities list then place the subBatches there
            if activeEntity in G.pendingEntities:
                G.pendingEntities.append(subBatch)
                G.pendingEntities.remove(activeEntity)
        activeEntity.numberOfSubBatches=self.numberOfSubBatches
        self.timeLastEntityEnded=self.env.now

    # =======================================================================
    #     canAccept logic
    # =======================================================================
    def canAccept(self,callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
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
    #     canAcceptAndIsRequested logic
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        return activeObject.Up and len(activeObjectQueue)==0 and giverObject.haveToDispose(activeObject)
  
