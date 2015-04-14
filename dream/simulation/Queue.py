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


import simpy
from CoreObject import CoreObject
# ===========================================================================
#                            the Queue object
# ===========================================================================
class Queue(CoreObject):
    family='Buffer'
    
    #===========================================================================
    # the __init__ method of the Queue
    #===========================================================================
    def __init__(self, id='', name='', capacity=1, isDummy=False, schedulingRule="FIFO", 
                 level=None, gatherWipStat=False, **kw):
        self.type="Queue"           # String that shows the type of object
        CoreObject.__init__(self, id, name)
        capacity=float(capacity)
        if capacity<0 or capacity==float("inf"):
            self.capacity=float("inf")
        else:
            self.capacity=int(capacity)

        self.isDummy=bool(int(isDummy))                    #Boolean that shows if it is the dummy first Queue
        self.schedulingRule=schedulingRule      #the scheduling rule that the Queue follows
        self.multipleCriterionList=[]           #list with the criteria used to sort the Entities in the Queue
        SRlist = [schedulingRule]
        if schedulingRule.startswith("MC"):     # if the first criterion is MC aka multiple criteria
            SRlist = schedulingRule.split("-")  # split the string of the criteria (delimiter -)
            self.schedulingRule=SRlist.pop(0)   # take the first criterion of the list
            self.multipleCriterionList=SRlist   # hold the criteria list in the property multipleCriterionList
 
        for scheduling_rule in SRlist:
          if scheduling_rule not in self.getSupportedSchedulingRules():
            raise ValueError("Unknown scheduling rule %s for %s" %
              (scheduling_rule, id))

        self.gatherWipStat=gatherWipStat
        # trigger level for the reallocation of operators
        if level:
            assert level<=self.capacity, "the level cannot be bigger than the capacity of the queue"
        self.level=level
        from Globals import G
        G.QueueList.append(self)
            
    @staticmethod
    def getSupportedSchedulingRules():
        return ("FIFO", "Priority", "EDD", "EOD",
            "NumStages", "RPC", "LPT", "SPT", "MS", "WINQ")
    
    #===========================================================================
    # the initialize method of the Queue class
    #===========================================================================
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        # initialise the internal Queue (type Resource) of the Queue object 
        self.Res=simpy.Resource(self.env, self.capacity)
        # event used by router
        self.loadOperatorAvailable=self.env.event()
        
        self.expectedSignals['isRequested']=1
        self.expectedSignals['canDispose']=1
        self.expectedSignals['loadOperatorAvailable']=1

    
    #===========================================================================
    # run method of the queue
    #===========================================================================
    def run(self):
        
        activeObjectQueue=self.Res.users
        # check if there is WIP and signal receiver
        self.initialSignalReceiver()
        while 1:
            self.printTrace(self.id, waitEvent='')
            # wait until the Queue can accept an entity and one predecessor requests it
            self.expectedSignals['canDispose']=1
            self.expectedSignals['isRequested']=1
            self.expectedSignals['loadOperatorAvailable']=1
            receivedEvent=yield self.env.any_of([self.isRequested, self.canDispose, self.loadOperatorAvailable])
            self.printTrace(self.id, received='')
            # if the event that activated the thread is isRequested then getEntity
            if self.isRequested in receivedEvent:
                transmitter, eventTime=self.isRequested.value
                self.printTrace(self.id, isRequested=transmitter.id)
                # reset the isRequested signal parameter
                self.isRequested=self.env.event()
                self.getEntity()
                #if entity just got to the dummyQ set its startTime as the current time
                if self.isDummy:
                    activeObjectQueue[0].startTime=self.env.now
            # if the queue received an loadOperatorIsAvailable (from Router) with signalparam time
            if self.loadOperatorAvailable in receivedEvent:
                transmitter, eventTime=self.loadOperatorAvailable.value
                self.loadOperatorAvailable=self.env.event()
            # if the queue received an canDispose with signalparam time, this means that the signals was sent from a MouldAssemblyBuffer
            if self.canDispose in receivedEvent:
                transmitter, eventTime=self.canDispose.value
                self.printTrace(self.id, canDispose='')
                self.canDispose=self.env.event()
            # if the event that activated the thread is canDispose then signalReceiver
            if self.haveToDispose():
                if self.receiver:
                    if not self.receiver.entryIsAssignedTo():
                        # try to signal receiver. In case of failure signal giver (for synchronization issues)
                        if not self.signalReceiver():
                            self.signalGiver()
                    continue
                self.signalReceiver()
            # signal the giver (for synchronization issues)
            self.signalGiver()
    
    # =======================================================================
    #               checks if the Queue can accept an entity       
    #             it checks also who called it and returns TRUE 
    #            only to the predecessor that will give the entity.
    # =======================================================================  
    def canAccept(self, callerObject=None): 
        activeObjectQueue=self.Res.users
        #if we have only one predecessor just check if there is a place available
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(callerObject==None):
            return len(activeObjectQueue)<self.capacity
        thecaller=callerObject
        return len(activeObjectQueue)<self.capacity and (self.isInRouteOf(thecaller))
    
    # =======================================================================
    #    checks if the Queue can dispose an entity to the following object
    #            it checks also who called it and returns TRUE 
    #           only to the receiver that will give the entity. 
    #              this is kind of slow I think got to check   
    # =======================================================================
    def haveToDispose(self, callerObject=None): 
        activeObjectQueue=self.Res.users     
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(callerObject==None):
            return len(activeObjectQueue)>0 
        thecaller=callerObject
        return len(activeObjectQueue)>0 and thecaller.isInRouteOf(self)
    
    # =======================================================================
    #                    removes an entity from the Object
    # =======================================================================
    def removeEntity(self, entity=None):
        activeEntity=CoreObject.removeEntity(self, entity)                  #run the default method
        if self.canAccept():
            self.signalGiver()
        # TODO: disable that for the mouldAssemblyBuffer
        if not self.__class__.__name__=='MouldAssemblyBufferManaged':
            if self.haveToDispose():
#                 self.printTrace(self.id, attemptSignalReceiver='(removeEntity)')
                self.signalReceiver()
        # reset the signals for the Queue. It be in the start of the loop for now
        # xxx consider to dothis in all CoreObjects
        self.expectedSignals['isRequested']=1
        self.expectedSignals['canDispose']=1
        self.expectedSignals['loadOperatorAvailable']=1
        # check if the queue is empty, if yes then try to signal the router, operators may need reallocation
        try:
            if self.level:
                if not len(self.getActiveObjectQueue()) and self.checkForDedicatedOperators():
                    self.requestAllocation()
        except:
            pass
        return activeEntity
    
    # =======================================================================
    #            checks if the Queue can accept an entity and 
    #        there is an entity in some predecessor waiting for it
    #   also updates the predecessorIndex to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        activeObjectQueue=self.Res.users
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        return len(activeObjectQueue)<self.capacity and giverObject.haveToDispose(self) 
    
    # =======================================================================
    #            gets an entity from the predecessor that 
    #                the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeEntity=CoreObject.getEntity(self)  #run the default behavior 
        # if the level is reached then try to signal the Router to reallocate the operators
        try:
            if self.level:
                if len(self.getActiveObjectQueue())==self.level and self.checkForDedicatedOperators():
                    self.requestAllocation()
        except:
            pass
        return activeEntity
    
    #===========================================================================
    # checks whether the entity can proceed to a successor object
    #===========================================================================
    def canDeliver(self, entity=None):
        assert self.isInActiveQueue(entity), entity.id +' not in the internalQueue of'+ self.id
        activeEntity=entity
        
        mayProceed=False
        # for all the possible receivers of an entity check whether they can accept and then set accordingly the canProceed flag of the entity 
        for nextObject in [object for object in self.next if object.canAcceptEntity(activeEntity)]:
            activeEntity.proceed=True
            activeEntity.candidateReceivers.append(nextObject)
            mayProceed=True
        return mayProceed
            
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
        activeObjectQ=self.Res.users
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
                        RPT+=float(processingTime.get('Fixed',{}).get('mean',0))               
                entity.totalRemainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.totalRemainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            for entity in activeObjectQ:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('Fixed',{}).get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.processingTimeInNextStation, reverse=True)             
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        elif criterion=="SPT":
            for entity in activeObjectQ:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('Fixed',{}).get('mean',0))
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
                        RPT+=float(processingTime.get('Fixed',{}).get('mean',0))              
                entity.totalRemainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: (x.dueDate-x.totalRemainingProcessingTime))  
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        elif criterion=="WINQ":
            from Globals import G
            for entity in activeObjectQ:
                if len(entity.remainingRoute)>1:
                    nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                    for obj in G.ObjList:
                        if obj.id in nextObjIds:
                            nextObject=obj
                    entity.nextQueueLength=len(nextObject.Res.users) 
                else:
                    entity.nextQueueLength=0          
            activeObjectQ.sort(key=lambda x: x.nextQueueLength)
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )

    def outputResultsJSON(self):
        from Globals import G
        json = {'_class': 'Dream.%s' % self.__class__.__name__,
                'id': str(self.id), 
                'family': self.family,
                'results': {} }
        if self.gatherWipStat:
            json['results']['wip_stat_list']=self.WipStat
        G.outputJSON['elementList'].append(json)
