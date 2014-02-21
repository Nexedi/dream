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
Created on 6 Dec 2012

@author: Ioannis
'''
'''
Class that acts as an abstract. All the compound Objects (i.e. compoundMachine) should inherit from it
The information about the objects that will constitute the compound object must be provided in the form of dictionaries
sample Dictionary argument:
        {
            'type':'Machine',
            'processingTime':{
                'distributionType':'Fixed',
                'mean':'0',
                'stdev':'0',
                'min':'0',
                'max':'0'
                },
            'failures':{
            'failureDistribution','Fixed',
            'MTTF':'0',
            'MTTR':'0',
            'availability':'0'
            }
        } 
The Compound object must also define the routing among the components.
If the routing type is 'Series' then the sequence objects provided is the sequence used to set successors
e.g. if the sequence given is -queue - machine then a queue must be placed in front of the machine 
'''

from SimPy.Simulation import Process, Resource, now, activate, passivate, waituntil, hold
from CoreObject import CoreObject
# from SimpleOperatedMachine2 import OperatedMachine
from OperatedMachine import OperatedMachine
from Queue import Queue
from Operator import Operator

class RoutingTypeError(Exception):
    def __init__(self, routingError):
        Exception.__init__(self, routingError) 

class ReceiverObjectError(Exception):
    def __init__(self, receiverError):
        Exception.__init__(self, receiverError) 
        
class NoneCallerObjectError(Exception):
    def __init__(self, callerError):
        Exception.__init__(self, callerError)        

# ===========================================================================
#                           the compound object 
# ===========================================================================
class CompoundObject(CoreObject,Queue):
    # object arguments may provide information on the type of the object, and the arguments needed to initiate it
    def __init__(self, id, name, capacity, routing='Series', *objects):  
        CoreObject.__init__(self, id, name)
                                            # it would be a good idea to have the arguments provided as dictionary
        self.type = 'CompoundObject'

        # variable that can hold according to this implementation two different values 
        #    'Parallel'
        #    'Series'
        self.routing = routing
        # assert that there are arguments provided, and that the type of the arguments provided is dictionary
        assert ((len(objects))>0), 'the number of objects provided is 0'
        assert (type(objects) is dict), 'the given arguments are not dictionaries'
        self.numberOfObjects = len(objects)
        # the capacity of the compound object
        # have to be careful, the capacity of the compound object should not exceed the 
        # combined capacity of the internal objects 
        self.capacity = capacity
        # a tuple that holds the arguments provided
        self.objects = objects
        # list of the objects that the compoundObject consists of
        self.coreObjects = []
        # list of the objects' IDs that constitute the compooundObject
        self.coreObjectIds = []
        # list of machines
        self.machines = []
        # list of queues
        self.queues = []
        # list with the resources assigned to the object
        self.resources = []
        # list with the repairmen assigned to the object
        self.repairmen = []
        # list with the operators assigned to the object
        self.operators = []
        # list with the inner objects that can receive from the compound object
        self.innerNext = []
        # list with the inner objects that can deliver to the compound object
        self.innerPrevious = []
#         # variable that shows if the entity received is to be processed internally 
#         # or if the internal processing is concluded and can now be handed in to the successor of the compoundOjbect
#         self.entityToBeProcessedInternally = False
        # variable which informs that a new entity was just received
        self.newEntityWillBeReceived = False
        # variables used to define the sorting of the entities in the internal queue
        self.schedulingRule=schedulingRule      #the scheduling rule that the Queue follows
        self.multipleCriterionList=[]           #list with the criteria used to sort the Entities in the Queue
        if schedulingRule.startswith("MC"):     # if the first criterion is MC aka multiple criteria
            SRlist = schedulingRule.split("-")  # split the string of the criteria (delimiter -)
            self.schedulingRule=SRlist.pop(0)   # take the first criterion of the list
            self.multipleCriterionList=SRlist   # hold the criteria list in the property multipleCriterionList


        
        # ===================================================================
        # first assign the operators to the compoundObject
        # if the operators are described as dictionaries 
        # in the arguments then create them
        # ===================================================================
        objectIndex=0
        for object in self.objects:         # check if there are repairmen or operators provided
            try:
                if object.type=='Operator':
                    object.coreObjectsIds.append(self.id)
                    object.coreObjects.append(self)
                    self.resources.append(object)
                    self.operators.append(object)
                # currently only one repairman can work on a machine (the capacity may vary) 
                elif object.type=='Repairman':
                    object.coreObjectsIds.append(self.id)
                    object.coreObjects.append(self)
                    self.resources.append(object)
                    self.repairmen.append(object)
            except:
                type = object.get('type','not found')
                if type=='Repairman':
                    capacity = object.get('capacity','1')
                    componentName = self.name+str(self.id)+'_'+type+'_'+str(objecIndex)
                    compoentId = str(self.id)+str(objectIndex)
                    r = Repairman(id=componentId,name=componentName,capacity=capacity)
                    r.coreObjectIds.append(self.id)
                    r.coreObjects.append(self)
                    self.resources.append(r)
                    self.repairmen.append(r)
                elif type=='Operator':
                    capacity = object.get('capacity','1')
                    componentName = self.name+str(self.id)+'_'+type+'_'+str(objecIndex)
                    compoentId = str(self.id)+str(objectIndex)
                    o = Operator(id=componentId,name=componentName,capacity=capacity)
                    o.coreObjectIds.append(self.id)
                    o.coreObjects.append(self)
                    self.resources.append(o)
                    self.operators.append(o)
                objectIndex+=1
        # =================================================================== 
        # walk through the objects of type Machine and Queue and initiate them
        # the simple objects making up the compoundOjbect 
        # can only be queues and machines for the moment
        # ===================================================================
        objectIndex=0
        for object in self.objects:
            # if the inner-objects are created out of the compound object then 
            # they will be passed to it ass they are
            try:
                if object.type == 'Machine':
                    self.machines.append(object)
                elif object.type == 'Queue':
                    self.queues.append(object)
                self.coreObjectIds.append(object.id)
                self.coreObjects.append(object)
            # if they are not created out of the composite object then they should
            # be created in the object
            except:
                type = object.get('type','not found')
                # object type machine
                if type=='Machine':
                    componentName = self.name+str(self.id)+'_'+type+'_'+str(objectIndex)
                    componentId = str(self.id)+str(objectIndex)
                    processingTime = object.get('processingTime','not found')
                    distributionType = processingTime.get('distributionType','Fixed')
                    mean = float(processingTime.get('mean','0'))
                    stdev = float(processingTime.get('stdev','0'))
                    min = float(processingTime.get('min','0'))
                    max = float(processingTime.get('max','0'))
                    failures = object.get('failures','not found')
                    failureDistribution = failures.get('failureDistribution','Fixed')
                    MTTF = float(failures.get('MTTF','0'))
                    MTTR = float(failures.get('MTTR','0'))
                    availability = float(failures.get('availability','0'))
                    for repairman in self.repairmen:
                        if (self.id in repairman.coreObjectIds):
                            R = repairman
                    O = []
                    for operator in self.operators:
                        if (self.id in operator.coreObjectIds):
                            O.append(operator)
                    # there must be an implementation of a machine where the failure is passed as argument
                    # this way it will be possible to have the same failure-interruption for all the inner objects
                    M=OperatedMachine(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                        MTTF=MTTF, MTTR=MTTR, availability=availability, repairman=R,
                                                        mean=mean,stdev=stdev,min=min,max=max,
                                                        operatorPool = O)
                    self.coreObjectIds.append(M.id)
                    self.coreObjects.append(M)
                    self.machines.append(M)
                # object type Queue
                if type=='Queue':
                    componentName = self.name+str(self.id)+'_'+type+'_'+str(objectIndex)
                    componentId = str(self.id)+str(objectIndex)
                    capacity=int(object.get('capacity','1'))
                    isDummy = bool(object.get('isDummy','0'))
                    schedulingRule = object.get('schedulingRule','FIFO')
                    Q=Queue(id=componentId, name=componentName, capacity=capacity, isDummy=isDummy, schedulingRule=schedulingRule)
                    self.coreObjectIds.append(Q.id)
                    self.coreObjects.append(Q)
                    self.queues.append(Q)
                objectIndex+=1
        # the total time the machine has been waiting for the operator
        self.totalTimeWaitingForOperator=0
        
    
    # =======================================================================
    # sets the routing in and out elements for the Object as well as
    # the inner routing (routing in and out for the constituting objects)
    # =======================================================================
    def defineRouting(self, predecessorList=[], successorList=[]):
        self.next=successorList
        self.previous=predecessorList
        # define the routing of each constituting object and initialize it
        try:
            objectIndex = 0
            for object in self.coreObjects:
                objectIndex+=1
                if self.routing == 'Series':
                    if objectIndex==1:
                        object.defineRouting([],[self.coreObjects[objectIndex]])
                        self.innerNext.append(object)
                    elif objectIndex==len(self.coreObjectIds):
                        object.defineRouting([self.coreObjects[objectIndex-2]],[self])
                        self.innerPrevious.append(object)
                    else:
                        object.defineRouting([self.coreObjects[objectIndex-2]],[self.coreObjects[objectIndex]])
                elif self.routing == 'Parallel':
                    object.defineRouting([],[self])
                    self.innerNext.append(object)
                    self.innerPrevious.append(object)
                else:
                    raise RoutingTypeError("The type of the routing is neither Parallel or Series")
        except RoutingTypeError as routingError:
            print "Routing type error: {0}".format(routingError)
        
    # =======================================================================
    # initialize the compound object
    # =======================================================================
    def initialize(self):
        CoreObject.initialize(self)
        # queue to hold the entities all through the stay of an entity in the composite object
        self.Res = Resource(self.capacity)
        # the inner Giver that will feed the compound object receiver 
        self.innerGiver = None
        # the inner object that will receive the object most recently added to the self.Res.activeQ
        self.innerReceiver = None
        # entity that will passed on to the innerReceiver
        self.entityForInternalProc = None
        
#         # inner queues that buffer the entities before they are handed in to the inner objects 
#         # and receive them again after the internal processing
#         self.entryRes = Resource(self.capacity)
#         self.exitRes = Resource(self.capacity)
        # initialize all resources
        # will have to reconsider as some of the resources may have been already initialized
        for resource in self.resources:
            if not resource.isInitialized():
                resource.initialize()
        # initialize all objects - and the entrance object
#         self.firstObject.initialize()
        for object in self.coreObjects:
            object.initialize() 

    # =======================================================================
    # the main process of the composite object object
    # it's main function is to activate the inner objects
    # =======================================================================
    def run(self):
        # activate every object in the coreOjbects list
        for object in self.coreObjects:
            activate(object, object.run())
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested
            
    
    # =======================================================================
    # get the entity from the previous object
    # has to update the inner receiver object 
    # and update its internal queue in a way
    # that its canAcceptAndIsRequested method 
    # will be updated 
    # =======================================================================
    def getEntity(self):
        activeEntity = coreObject.getEntity(self)
        self.entityForInternalProc = activeEntity
        return activeEntity
            
    # =======================================================================
    # removes an entity from the Object
    # it must be run on the last object if the routing is 'Series'
    # or on the object that has a kind of priority and is waiting to dispose
    # if the routing is 'Parallel'
    # =======================================================================
    def removeEntity(self): 
        actibeObject = self.getActiveObject()
        activeObjectQueue = self.getActiveObjectQueue()
        try:
            receiverObject = self.getReceiverObject()
            # internal logic ================================================
            # the activeEntity is not removed, the removeEntity method just returns the activeEntity
            # the entity remains in the activeObjectQueue till it is removed by the external logic
            # the entity's flag 'internal' is changed to True to signify the start of the internal processing
            if receiverObject in self.innerNext:
                activeEntity = next(entity==self.entityForInternalProc for entity in activeObjectQueue)
#                 activeIndex = activeObjectQueue.index(activeEntity)
                activeEntity.internal = True
                # empty the previous list of the innerReceiver so that its 
                # canAcceptAndIsRequested method can be controlled via 
                # the compoundObject's canAcceptAndIsRequested method
                self.innerReceiver.previous = []
            # external logic ================================================
            elif receiverObject in self.next:
                activeEntity = self.innerGiver.getActiveObjectQueue[0]
                # find the index of the entity to be removed in the activeObjectQueue
                activeIndex = activeObjectQueue.index(activeEntity)
                # remove the entity from the internal queue and from the innerGiver queue
                self.innerGiver.getActiveObjectQueue().pop(0)
                activeObjectQueue.pop(activeIndex)
                # update the time the last entity left
                self.timeLastEntityLeft = now()
            else:
                raise ReceiverObjectError("""the receiver has not been defined, the composite object needs info on the receiver\ 
                                            in order to decide where to deliver""")
        except ReceiverObjectError as receiverError:
            print "Receiver object error: {0}".format(receiverError)
            
        try:
            self.outputTrace(activeEntity.name, "released "+ self.objName)
        except TypeError:
            pass
        return activeEntity
    
    # =======================================================================
    # checks if the Object can dispose an entity to the following object 
    # =======================================================================
    def haveToDispose(self, callerObject=None): 
        # get the active object
        activeObject = self.getActiveOject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        theCaller = callerObject
        assert (theCaller!=None), 'the caller object of a compound cannot be None'
        try:
            if theCaller!=None:
                # internal logic ============================================
                if theCaller in self.innerNext:
                    if(len(activeObject.innerNext)==1):
                        return len(activeObjectQueue)>0\
                             and any(entity==self.entityForInternalProc for entity in activeObjectQueue) 
                    maxTimeWaiting=0
                    for object in activeObject.innerNext:
                        if(object.canAccept(self)):                                 # if the object can accept
                            timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting
                            if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                                maxTimeWaiting=timeWaiting
                                self.receiver=object
                    receiverObject = activeObject.getReceiverObject()
                    return len(activeObjectQueue)>0\
                         and any(entity==self.entityForInternalProc for entity in activeObjectQueue)\
                         and (theCaller is receiverObject)\
                         and self.innerReceiver==receiverObject
                # external logic ============================================
                elif theCaller in self.next:
                    innerObjectHaveToDispose = False
                    maxTimeWaiting = 0
                    # find which object from those have something to dispose 
                    # is waiting the most
                    for object in self.innerPrevious:
                        if(object.haveToDispose(activeObject)):
                            innerObjectHaveToDispose = True
                            if(object.downTimeInTryingToReleaseCurrentEntity>0):
                                timeWaiting=now()-object.timeLastFailureEnded
                            else:
                                timeWaiting=now()-object.timeLastFailureEnded
                            if(timeWaiting>=maxTimeWaiting):
                                activeObject.innerGiver=object
                                maxTimeWaiting=timeWaiting
                    # if there is only one successor then check if there is something to be moved on
                    # and if the entity to be moved on is in the object's activeObjectQueue
                    if(len(activeObject.Next)==1):
                        return (len(activeObjectQueue)>0)\
                                and innerObjectHaveToDispose\
                                and (self.innerGiver.getActiveObjectQueue()[0] in activeObjectQueue) 
                    # if there are more than one successors then find the one waiting the most and 
                    # assign it as receiver
                    maxTimeWaiting=0
                    for object in activeObject.next:
                        if(object.canAccept(self)):                                 # if the object can accept
                            timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                            if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                                maxTimeWaiting=timeWaiting
                                self.receiver=object                           # and update the receiver to the index of this object
                    #return true only to the predecessor from which the queue will take 
                    receiverObject=activeObject.getReceiverObject()
                    return len(activeObjectQueue)>0\
                         and innerObjectHaveToDispose\
                         and (self.innerGiver.getActiveObjectQueue()[0] in activeObjectQueue)\
                         and (thecaller is receiverObject)
            else:
                raise NoneCallerObjectError("The caller of a CompoundObject method have to dispose cannot be None")
        except NoneCallerObjectError as callerError:
            print "None-Caller object error: {0}".format(callerError)
    
    # =======================================================================
    # the canAcceptAndIsRequested method that implements the 
    # logic for both internal and external objects
    # =======================================================================
#     def canAcceptAndIsRequested(self):
        # get the active object
#         activeObject = self.getActiveObject()
#         # dummy boolean variable to check if any predecessor has something to hand in
#         isRequested=False
#         # the variable that checks weather there is an external entity to be received is reset each
#         # time the canAcceptAndIsRequested method is invoked 
#         self.newEntityWillBeReceived = False
#         # dummy boolean to check if the compound is requested internally
#         isRequestedInternally = False
#         # dummy timer to check which predecessor has been waiting the most
#         maxTimeWaiting=0
#         # check first if there are inner objects that have to dispose
#         for object in self.innerPrevious:
#             if(object.haveToDispose(activeObject) and object.receiver==self):
#                 isRequested=True
#                 isRequestedInternally = True
#                 if(object.downTimeInTryingToReleaseCurrentEntity>0):
#                     timeWaiting=now()-object.timeLastFailureEnded
#                 else:
#                     timeWaiting=now()-object.timeLastEntityEnded
#                 if (timeWaiting>=maxTimeWaiting):
#                     activeObject.giver=object
#                     maxTimeWaiting=timeWaiting
#         # if it is not requested internally then receive from the external predecessors
#         if not isRequestedInternally:
#              #loop through the predecessors to see which have to dispose and which is the one blocked for longer
#              for object in self.previous:
#                  if(object.haveToDispose(activeObject) and object.receiver==self):   # if they have something to dispose off
#                      isRequested=True
#                      if(object.downTimeInTryingToReleaseCurrentEntity>0):# if the predecessor has failed wile waiting
#                          timeWaiting=now()-object.timeLastFailureEnded   # then update according the timeWaiting to be compared with the ones
#                      else:                                               # of the other machines
#                          timeWaiting=now()-object.timeLastEntityEnded
#                      #if more than one predecessor have to dispose take the part from the one that is blocked longer
#                      if(timeWaiting>=maxTimeWaiting):
#                          activeObject.giver=object                       # pick the predecessor waiting the more
#                          maxTimeWaiting=timeWaiting  
#         # have to find out if the logic to be implemented is internal or external
#         if giverObject in self.previous:
#             self.newEntry()
#         # now that we now if it is a new entry we can implement the corresponding logic for the getActiveObjectQueue
#         activeObjectQueue=self.getActiveObjectQueue()
#         # if it is a new entry then perform the normal logic
#         if self.isNewEntry():
#             # return true when the Queue is not fully occupied and a predecessor is requesting it
#             return len(activeObjectQueue)<self.capacity and isRequested
#         # otherwise, if the object is returned from the internal logic
#         elif not self.isNewEntry():
#             assert ((giverObjectQueue[0] in self.Res.activeQ)\
#                     and isRequested),\
#                     "The entity to be returned from the internal logic is not present in the external queue/res"
#             return (giverObjectQueue[0] in self.Res.activeQ)\
#                     and isRequested
# ---------------------------------------------------------------------------
    def canAcceptAndIsRequested(self):
        activeObject = self.getActiveObject()
        giverObject = self.getGiverObject()
        giverObjectQueue = self.getGiverObjectQueue()
        # find the inner object that will get the entity ====================
        innerCanAccept = False
        maxTimeWaiting = 0
        for object in activeObject.innerNext:
            if object.canAccept():
                innerCanAccept = True
                timeWaiting=now()-object.timeLastEntityLeft
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                    maxTimeWaiting=timeWaiting
                    activeObject.innerReceiver=object
        activeObject.innerReceiver.previous.append(activeObject)
        # if there is only one predecessor assign it as giver ===============
        if(len(activeObject.previous)==1):
            return giverObject.haveToDispose(activeObject)\
                 and (len(activeObjectQueue)<activeObject.capacity)\
                 and innerCanAccept
        # find the giver object among the predecessors ======================
        maxTimeWaiting = 0
        isRequested = False
        for object in activeObject.previous:
            if object.haveToDispose(activeObject) and object.receiver == activeObject:
                isRequested = True
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# if the predecessor has failed wile waiting
                    timeWaiting=now()-object.timeLastFailureEnded   # then update according the timeWaiting to be compared with the ones
                else:                                               # of the other machines
                    timeWaiting=now()-object.timeLastEntityEnded
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting):
                    activeObject.giver=object                       # pick the predecessor waiting the more
                    maxTimeWaiting=timeWaiting  
        return isRequested\
             and innerCanAccept\
             and len(activeObjectQueue)<activeObject.capacity
        
        
    # =======================================================================
    # checks if the Object can accept an entity 
    # have to re-assess the invocation of this method
    # many times this method is called without callerObject argument
    # =======================================================================
#     def canAccept(self, callerObject=None):
#         # get the active object
#         activeObject = self.getActiveObject()
#         giverObject = self.getGiverObject()
#         theCaller = callerObject
#         try:
#             if(theCaller!=None):
#                 # dummy boolean to check if the compound is requested internally
#                 isRequestedInternally = any(object is theCaller for object in self.innerPrevious)
#                 if isRequestedInternally:
#                     return len(self.extRes.activeQ)<activeObject.capacity
#                 else:
#                     return len(self.Res.activeQ)<activeObject.capacity
#             else:
#                 raise NoneCallerObjectError("The caller of a CompoundObject method have to dispose cannot be None")
#         except NoneCallerObjectError as callerError:
#             print "None-CallerObject error: {0}".format(callerError)
            
# ---------------------------------------------------------------------------
    def canAccept(self, callerObject=None):
        activeObject = self.getActiveObject()
        activeObjectQueue = activeObject.getActiveObjectQueue()
        giverObject = activeObject.getGiverObject()
        theCaller = callerObject
        
        innerCanAccept = False
        maxTimeWaiting = 0
        if(len(activeObject.previous)==1 or callerObject == None):
            return any(object.canAccept() for object in activeObject.innerNext)\
                 and len(activeObjectQueue)<activeObject.capacity
                 
        return any(object.canAccept() for object in activeObject.innerNext)\
             and len(activeObjectQueue)<activeObject.capacity\
             and giverObject == theCaller
    
    
#     # =======================================================================
#     # check if the object has an entity to dispose externally 
#     # =======================================================================
#     def isNewEntry(self):
#         return self.newEntityWillBeReceived
#     
#     # =======================================================================
#     # define that a new entity was just received
#     # =======================================================================
#     def newEntry(self):
#         self.newEntityWillBeReceived = True
    
    
