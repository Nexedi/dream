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
from SimPy.Simulation import activate, waituntil, now, hold

import scipy.stats as stat

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
    def __init__(self, id, name, numberOfSubBatches=1, distribution='Fixed', \
                 mean=1, stdev=0, min=0, max=10,operator='None'):
        Process.__init__(self)
        # hold the id, name, and type of the Machine instance
        self.id=id
        self.objName=name
        self.type="BatchRassembly"              #String that shows the type of object
        # holds the capacity of the object 
        self.numberOfSubBatches=numberOfSubBatches
        # define the distribution types of the processing and failure times respectively
        self.distType=distribution                  #the distribution that the procTime follows      
        # sets the operator resource of the Machine
        self.operator=operator         
        # Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=mean
        self.rng.stdev=stdev
        self.rng.min=min
        self.rng.max=max
        # for routing purposes 
        self.next=[]                                #list with the next objects in the flow
        self.previous=[]                            #list with the previous objects in the flow
        self.nextIds=[]                             #list with the ids of the next objects in the flow
        self.previousIds=[]                         #list with the ids of the previous objects in the flow

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
        
        while 1:  
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity
                                                                    #and one predecessor requests it
            self.getEntity()
            
            # self.outputTrace("got into "+self.objName)
            
            # set the currentEntity as the Entity just received and initialize the timer timeLastEntityEntered
            self.currentEntity=self.getActiveObjectQueue()[0]       # entity is the current entity processed in object
            self.nameLastEntityEntered=self.currentEntity.name      # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=now()                        #this holds the last time that an entity got into Machine  
            
            if len(self.getActiveObjectQueue())==self.numberOfSubBatches and self.currentEntity.type!='Batch':
                yield hold,self,self.calculateProcessingTime()
                self.reassemble()
        
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
        
    # =======================================================================
    #     returns True if the object doensn't hold entities of type Batch
    # and if the subBatches in the its internal queue and the one of the giver
    # hold subBatches of the same batchId
    # =======================================================================
    def canAccept(self,callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        giverObjectQueue = self.getGiverObjectQueue()

        if(len(activeObject.previous)==1 or callerObject==None):
            if len(activeObjectQueue)==0:
                return activeObject.Up
            elif len(giverObjectQueue)==0:
                return False
            else:
                return activeObject.Up\
                     and activeObjectQueue[0].type!='Batch'\
                     and len(activeObjectQueue)<self.numberOfSubBatches\
                     and giverObjectQueue[0].batchId==activeObjectQueue[0].batchId
        
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQueue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        return len(activeObjectQueue)<self.numberOfSubBatches\
                and (thecaller is giverObject)\
                and activeObjectQueue[0].type != 'Batch'\
                and giverObjectQueue[0].batchId==activeObjectQueue[0].batchId

    # =======================================================================
    #     returns True if it holds an entity of type Batch
    # =======================================================================
    def haveToDispose(self,callerObject=None):
        # get active and the receiver object
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()    
        receiverObject=activeObject.getReceiverObject() 
        #if we have only one successor just check if object waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            return len(activeObjectQueue)==1\
                    and activeObjectQueue[0].type=="Batch" # the control of the length of the queue is not needed
        
        thecaller=callerObject 
        #give the entity to the receiver that is waiting for the most time. 
        #plant does not do this in every occasion!       
        maxTimeWaiting=0     
        for object in activeObject.next:
            if(object.canAccept()):                                 # if the object can accept
                timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                    maxTimeWaiting=timeWaiting
                    self.receiver=object                           # and update the successorIndex to the index of this object
              
        #return true only to the predecessor from which the queue will take 
        receiverObject=activeObject.getReceiverObject()
        return len(self.getActiveObjectueue)==1\
                and (thecaller is receiverObject)\
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
        #if we have only one predecessor just check if there is a place available and the predecessor has an entity to dispose
        if(len(activeObject.previous)==1):
            if len(activeObjectQueue)==0:
                return activeObject.Up and giverObject.haveToDispose(activeObject)
            else:
                return activeObject.Up and giverObject.haveToDispose(activeObject)\
                     and activeObjectQueue[0].type!='Batch'\
                     and len(activeObjectQueue)<self.numberOfSubBatches\
                     and giverObjectQueue[0].batchId==activeObjectQueue[0].batchId 
    
        isRequested=False               # dummy boolean variable to check if any predecessor has something to hand in
        maxTimeWaiting=0                # dummy timer to check which predecessor has been waiting the most
        
        #loop through the predecessors to see which have to dispose and which is the one blocked for longer                                                    # loop through all the predecessors
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject)):                 # if they have something to dispose off
                isRequested=True                                    # then the Queue is requested to handle the entity
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# if the predecessor has failed wile waiting 
                    timeWaiting=now()-object.timeLastFailureEnded   # then update according the timeWaiting to be compared with the ones
                else:                                               # of the other machines
                    timeWaiting=now()-object.timeLastEntityEnded
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting):                    
                    activeObject.giver=object  
                    maxTimeWaiting=timeWaiting                   
        return isRequested\
                and activeObject.Up\
                and len(activeObjectQueue<self.numberOfSubBatches)\
                and (len(activeObjectQueue)==0 or activeObjectQueue[0].type!='Batch')\
                and activeObject.getGiverObjectQueue()[0].batchId==activeObjectQueue[0].batchId
        # return true when the Queue is not fully occupied and a predecessor is requesting it
