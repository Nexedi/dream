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
Models a FIFO queue where entities can wait in order to get into a server
'''


from SimPy.Simulation import Process, Resource
from SimPy.Simulation import waituntil, now, infinity
from CoreObject import CoreObject
# ===========================================================================
#                            the Queue object
# ===========================================================================
class Queue(CoreObject):
    
    def __init__(self, id, name, capacity=1, dummy=False, schedulingRule="FIFO"):
        CoreObject.__init__(self)
#         Process.__init__(self)
        # used for the routing of the entities
        self.predecessorIndex=0     # holds the index of the predecessor from which the Queue will take an entity next
        self.successorIndex=0       # holds the index of the successor where the Queue will dispose an entity next
        #     hold the id, name, and type of the Queue instance
        self.id=id
        self.objName=name
        self.type="Queue"           # String that shows the type of object
        #     holds the capacity of the Queue
        if capacity>0:
            self.capacity=capacity
        else:
            self.capacity=infinity
        # consider removing the following, the are restated in the initialize() method
#         self.nameLastEntityEntered=""   #keeps the name of the last entity that entered in the object
#         self.timeLastEntityEntered=0    #keeps the time of the last entity that entered in the object

        #     No failures are considered for the Queue
        
#         #     lists that hold the previous and next objects in the flow
#         self.next=[]                    #list with the next objects in the flow
#         self.previous=[]                #list with the previous objects in the flow
#         self.nextIds=[]                 #list with the ids of the next objects in the flow
#         self.previousIds=[]             #list with the ids of the previous objects in the flow

        self.isDummy=dummy                      #Boolean that shows if it is the dummy first Queue
        self.schedulingRule=schedulingRule      #the scheduling rule that the Queue follows
        self.multipleCriterionList=[]           #list with the criteria used to sort the Entities in the Queue
        if schedulingRule.startswith("MC"):     # if the first criterion is MC aka multiple criteria
            SRlist = schedulingRule.split("-")  # split the string of the criteria (delimiter -)
            self.schedulingRule=SRlist.pop(0)   # take the first criterion of the list
            self.multipleCriterionList=SRlist   # hold the criteria list in the property multipleCriterionList
 
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        # initialize the internal Queue (type Resource) of the Queue object 
        self.Res=Resource(self.capacity)   
             
    def run(self):  
        activeObjectQueue=self.getActiveObjectQueue()
        
        while 1:  
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity
                                                                    #and one predecessor requests it                                                  
            self.getEntity()                                                               
            
            #if entity just got to the dummyQ set its startTime as the current time         
            if self.isDummy:               
                activeObjectQueue[0].startTime=now() 
    # =======================================================================
    #               checks if the Queue can accept an entity       
    #             it checks also who called it and returns TRUE 
    #            only to the predecessor that will give the entity.
    # =======================================================================  
    def canAccept(self, callerObject=None): 
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        
        #if we have only one predecessor just check if there is a place available
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(len(activeObject.previous)==1 or callerObject==None):
            return len(activeObjectQueue)<activeObject.capacity   
    
#         if len(activeObjectQueue)==activeObject.capacity:
#             return False
        
        thecaller=callerObject
        
        #return true only to the predecessor from which the queue will take 
        #flag=False
        #if thecaller is self.previous[self.predecessorIndex]:
        #    flag=True
        return len(activeObjectQueue)<activeObject.capacity and thecaller==giverObject  
    # =======================================================================
    #    checks if the Queue can dispose an entity to the following object
    #            it checks also who called it and returns TRUE 
    #           only to the receiver that will give the entity. 
    #              this is kind of slow I think got to check   
    # =======================================================================
    def haveToDispose(self, callerObject=None): 
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()     
        
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(len(activeObject.next)==1 or callerObject==None):
            return len(self.Res.activeQ)>0 
        
#         #if the Queue is empty it returns false right away
#         if(len(activeObjectQueue)==0):
#             return False
         
        thecaller=callerObject
               
        #give the entity to the possible receiver that is waiting for the most time. 
        #plant does not do this in every occasion!       
        maxTimeWaiting=0     
                                                        # loop through the object in the successor list
        for object in activeObject.next:
            if(object.canAccept()):                                 # if the object can accept
                timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                    maxTimeWaiting=timeWaiting
                    self.receiver=object                           # and update the receiver to the index of this object
              
        #return true only to the predecessor from which the queue will take 
        receiverObject=activeObject.getReceiverObject()
        return len(self.Res.activeQ)>0 and (thecaller is receiverObject)    
    # =======================================================================
    #                    removes an entity from the Object
    # =======================================================================
    def removeEntity(self):        
        activeObject=self.getActiveObject()                                  
        activeEntity=CoreObject.removeEntity(self)                                      #run the default method     
        return activeEntity
    # =======================================================================
    #            checks if the Queue can accept an entity and 
    #        there is an entity in some predecessor waiting for it
    #   also updates the predecessorIndex to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get the active and the giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
               
        #if we have only one predecessor just check if there is a place available and the predecessor has an entity to dispose
        if(len(activeObject.previous)==1):
            
            return len(activeObjectQueue)<self.capacity and giverObject.haveToDispose(activeObject) 
    
        isRequested=False               # dummy boolean variable to check if any predecessor has something to hand in
        maxTimeWaiting=0                # dummy timer to check which predecessor has been waiting the most
        
        #loop through the predecessors to see which have to dispose and which is the one blocked for longer                                                      # loop through all the predecessors
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject) and object.receiver==self):                 # if they have something to dispose off
                isRequested=True                                    # then the Queue is requested to handle the entity
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# if the predecessor has failed wile waiting 
                    timeWaiting=now()-object.timeLastFailureEnded   # then update according the timeWaiting to be compared with the ones
                else:                                               # of the other machines
                    timeWaiting=now()-object.timeLastEntityEnded
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting):                    
                    activeObject.giver=object  
                    maxTimeWaiting=timeWaiting                                                                       # pick the predecessor waiting the more
        return len(activeObjectQueue)<self.capacity and isRequested # return true when the Queue is not fully occupied and a predecessor is requesting it
    # =======================================================================
    #            gets an entity from the predecessor that 
    #                the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeEntity=CoreObject.getEntity(self)  #run the default behavior 
        return activeEntity
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # =======================================================================
    def sortEntities(self):
        #if we have sorting according to multiple criteria we have to call the sorter many times
        if self.schedulingRule=="MC":
            for criterion in reversed(self.multipleCriterionList):
               self.activeQSorter(criterion=criterion) 
        #else we just use the default scheduling rule
        else:
            self.activeQSorter()
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # =======================================================================
    def activeQSorter(self, criterion=None):
        activeObjectQ=self.Res.activeQ
        if criterion==None:
            criterion=self.schedulingRule           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            pass
        #if the schedulingRule is based on a pre-defined priority
        elif criterion=="Priority":
            activeObjectQ.sort(key=lambda x: x.priority)
        #if the schedulingRule is earliest due date
        elif criterion=="EDD":
            activeObjectQ.sort(key=lambda x: x.dueDate)   
        #if the schedulingRule is earliest order date
        elif criterion=="EOD":
            activeObjectQ.sort(key=lambda x: x.orderDate)      
        #if the schedulingRule is to sort Entities according to the stations they have to visit
        elif criterion=="NumStages":
            activeObjectQ.sort(key=lambda x: len(x.remainingRoute), reverse=True)  
        #if the schedulingRule is to sort Entities according to the their remaining processing time in the system
        elif criterion=="RPC":
            for entity in activeObjectQ:
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))               
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.remainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            for entity in activeObjectQ:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.processingTimeInNextStation, reverse=True)             
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        elif criterion=="SPT":
            for entity in activeObjectQ:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.processingTimeInNextStation) 
        #if the schedulingRule is to sort Entities based on the minimum slackness
        elif criterion=="MS":
            for entity in activeObjectQ:
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))              
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: (x.dueDate-x.remainingProcessingTime))  
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        elif criterion=="WINQ":
            from Globals import G
            for entity in activeObjectQ:
                nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                for obj in G.ObjList:
                    if obj.id in nextObjIds:
                        nextObject=obj
                entity.nextQueueLength=len(nextObject.getActiveObjectQueue())           
            activeObjectQ.sort(key=lambda x: x.nextQueueLength)
        #if the schedulingRule is set to ConditionalBuffer scheduling rule "CB" where orderComponents of type "Secondary"
        #are moved to the end of the queue if their parent order.basicsEnded property is set to False
        elif criterion=='CB':
            # if the componentType is Basic then don't move it to the end of the activeQ
            # else if the componentType is Secondary and it's basics are not ended then move it to the back
            activeObjectQ.sort(key=lambda x: not ((x.componentType=='Basic')\
                                                  or ((x.order.basicsEnded)\
                                                      and (x.componentType=='Secondary'))))