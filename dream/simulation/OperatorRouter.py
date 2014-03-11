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
Created on 19 Feb 2013

@author: Ioannis
'''
'''
Models an Interruption that schedules the operation of the machines by different managers
'''

from SimPy.Simulation import Process, Resource
from ObjectInterruption import ObjectInterruption
from SimPy.Simulation import waituntil, now, hold, request, release


# ===========================================================================
#               Class that handles the Operator Behavior
# ===========================================================================
class Router(ObjectInterruption):
    
    # =======================================================================
    #   according to this implementation one machine per broker is allowed
    #     The Broker is initiated within the Machine and considered as 
    #                black box for the ManPy end Developer
    # ======================================================================= 
    def __init__(self):
        ObjectInterruption.__init__(self)
        self.type = "Router"
        # variable used to hand in control to the Broker
        self.call=False
        # list that holds all the objects that can receive
        self.pendingObjects=[]
        self.calledOperators=[]
        # TODO: consider if there must be an argument set for the schedulingRules of the Router
        self.schedulingRule=''
        # list of the operators that may handle a machine at the current simulation time
        self.candidateOperators=[]
        # list of criteria
        self.multipleCriterionList=[]
        
    # =======================================================================
    #                          the run method
    # =======================================================================
    '''
    all the pendingEntities that are hot should be examined if they can proceed to the next
    step of their route as they may not be first in the activeQueue of their currentStations (QueueManagedJob).
    If they can be disposed to the next object then the router should wait again till the machine to receive them
    returns canAcceptAndIsRequested (inPositionToGet is True)
    '''
    def run(self):
        from Globals import G
        while 1:
            # wait until the router is called
            yield waituntil,self,self.routerIsCalled
            # when the router is called for the first time wait till all the entities 
            #     finished all their moves in stations of non-Machine-type 
            #     before they can enter again a type-Machine object
            yield waituntil, self,self.entitiesFinishedMoving
            
            # update the objects to be served list (pendingObjects)
            self.pendingObjects=[object for object in G.MachineList if object.inPositionToGet]

            #===================================================================
#             # TESTING
#             print now(), '================================================================================'
#             print '        the pending objects are        ', [str(object.id) for object in self.pendingObjects]
            #===================================================================
            
            # update the calledOperators list
            self.calledOperators=[operator for operator in G.OperatorsList if len(operator.activeCallersList)]

            #===================================================================
#             # TESTING
#             print '        the called operators are        ', [str(operator.id) for operator in self.calledOperators]
#             print '        from callers                    ', [[str(x.id) for x in operator.activeCallersList] for operator in self.calledOperators]
#             print '        for entity                      ', [[str(x.giver.getActiveObjectQueue()[0].id)for x in operator.activeCallersList] for operator in self.calledOperators]
            #===================================================================
            
            # find the operators that can start working now even if they are not called
            self.findCandidateOperators()
            
            # sort the pendingEntities list
            self.sortPendingEntities()
            
            #===================================================================
#             # TESTING
#             if G.pendingEntities:
#                 print '                {} the pending entities that can proceed are:                            ',
#                 print [str(entity.id) for entity in G.pendingEntities if entity.canProceed]
#             if self.candidateOperators:
#                 print '                {} the candidate operators are:                                          ',
#                 print [str(candidate.id) for candidate in self.candidateOperators]
            #===================================================================
            
            # find the operators candidateEntities
            self.findCandidateEntities()
            
            # find the entity that will occupy the resource, and the station that will receive it (if any available)
            self.findCandidateReceivers()
            
            #===================================================================
#             # TESTING
#             print '                    after findReceivers',
#             print [(str(operator.id),[str(candidateEntity.id) for candidateEntity in operator.candidateEntities],)\
#                             for operator in self.candidateOperators]
#             print 'after find receivers'
#             print [str(op.id) for op in self.candidateOperators if op.candidateEntity.candidateReceiver]
#             print [(op.id, op.candidateEntity.id, op.candidateEntity.candidateReceiver.id)\
#                     for op in self.candidateOperators if op.candidateEntity.candidateReceiver]
            #===================================================================

            # sort the givers for the operators that will process the entities
            self.sortGiverQueue()
            
            #===================================================================
#             # TESTING
#             print 'after sortGiverQueue'
#             print [str(op.id) for op in self.candidateOperators if op.candidateEntity.candidateReceiver]
#             print [(op.id, op.candidateEntity.id, op.candidateEntity.candidateReceiver.id)\
#                     for op in self.candidateOperators if op.candidateEntity.candidateReceiver]
            #===================================================================
            
            # for all the operators that are requested
            for operator in self.calledOperators:
                priorityObject=None
                #===============================================================
#                 # TESTING
#                 print '        calledOperator prioritising',operator.id
#                 if operator.candidateEntity:
#                     if operator.candidateEntity.candidateReceiver:
#                         print '        its candidateReceiver',operator.candidateEntity.candidateReceiver.id
#                 print '        its activeCallers',[str(x.id) for x in operator.activeCallersList]
                #===============================================================
                
                # check if the candidateReceivers are inPositionToGet and  if they are already called
                try:
                    receiverIsActive=(operator.candidateEntity.candidateReceiver in operator.activeCallersList\
                                                  and operator.candidateEntity.candidateReceiver in self.pendingObjects )
                except:
                    receiverIsActive=True
                
                # check if the candidateOperators are available, if the are requested and reside in the pendingObjects list 
                if operator.checkIfResourceIsAvailable() and \
                        receiverIsActive:
                    #===========================================================
#                     # TESTING
#                     print now(), 'the active callers of', operator.objName, 'before sorting are            ',
#                     print [str(caller.id) for caller in operator.activeCallersList]
                    #===========================================================
                    
                    # sort the activeCallersList of the operator
                    operator.sortEntities()
                    #===========================================================
#                     # TESTING
#                     print now(), 'the active callers of', operator.objName, 'after sorting are            ',
#                     print [str(caller.id) for caller in operator.activeCallersList]
                    #===========================================================
                    
                    # find the activeCaller that has priority 
                    priorityObject=next(x for x in operator.activeCallersList if x in self.pendingObjects)
                    #===========================================================
#                     # TESTING
#                     print '                the PRIORITY object is', priorityObject.id
                    #===========================================================
                    
                    # and if the priorityObject is indeed pending
                    if priorityObject in self.pendingObjects:
                        
                        # assign an operator to the priorityObject
                        operator.operatorAssignedTo=priorityObject
                        #=======================================================
#                         # TESTING
#                         print now(), operator.objName, 'got assigned to', priorityObject.id
                        #=======================================================
                        
                        # and let it proceed withGetEntity
                        priorityObject.canProceedWithGetEntity=True
                        priorityObject.inPositionToGet=False
                # if the are not called and they are not in the pendingObjects list clear their activeCallersList
                elif not receiverIsActive:
                    operator.activeCallersList=[]
            # if an object cannot proceed with getEntity, unAssign the exit of its giver
            for object in self.pendingObjects:
                if not object.canProceedWithGetEntity:
                    object.giver.unAssignExit()
            #===================================================================
#             # TESTING
#             print '        these objects will proceed with getting entities',
#             print [str(object.id) for object in self.pendingObjects if object.canProceedWithGetEntity]
            #===================================================================
            
            self.exitRouter()
    
    #===========================================================================
    #     have the entities that have ended their processing when the router
    #     got first called finished their moves through queues?
    #===========================================================================
    def entitiesFinishedMoving(self):
        # check if the entities waiting to be disposed from different Machines
        #     the first time the Router is called, have reached the last queue (if any)
        #     before the next Machine in their route
        from Globals import G
        # pending entities are entities about to enter an other machine, updated by endProcessingActions()
        # if there are any pending entities
        if len(G.pendingEntities):
            # local variable
            allEntitiesMoved=False
            # for each one of them
            for entity in G.pendingEntities:
                # if they are residing in a machine which waits to dispose and is functional
                if entity.currentStation in G.MachineList:
                    if entity.currentStation.checkIfMachineIsUp()\
                         and entity.currentStation.waitToDispose:
                        # if the next step in the entity's route is machine with Load operationType then continue 
                        if (not (entity.currentStation.receiver in G.MachineList)\
                             and entity.currentStation.receiver.canAccept()\
                             or\
                           ((entity.currentStation.receiver.type in G.MachineList)\
                             and not any(type=='Load' for type in entity.currentStation.receiver.multOperationTypeList))):
                            return False
                # if the entity is in a Queue
                elif entity.currentStation in G.QueueList:
                    # if the hot flag of the entity is raised
                    if entity.hot:
                        allEntitiesMoved=True
#                         return True
                    else:
                        return False
                elif entity.currentStation in G.OrderDecompositionList:
                    return False
                # TODO: this list can check all the available object in G.objList
            # if no entity returned False then return True
            if allEntitiesMoved:
                return True
        return True
    
    # =======================================================================
    #                        call the Scheduler 
    #        filter for Broker - yield waituntil brokerIsCalled
    # =======================================================================
    def routerIsCalled(self):
        return self.call 
    
    # =======================================================================
    #         the broker returns control to OperatedMachine.Run
    #        filter for Machine - yield request/release operator
    # =======================================================================
    def routerIsSet(self):
        return not self.call
    
    # =======================================================================
    #               hand in the control to the Broker.run
    #                   to be called by the machine
    # =======================================================================
    def invokeRouter(self):
        self.call=True
        
    # =======================================================================
    #                 return control to the Machine.run
    # =======================================================================
    def exitRouter(self):
        from Globals import G
        # reset the variables that are used from the Router
        for operator in self.candidateOperators:
            operator.candidateEntities=[]
            operator.candidateEntity=None
        for entity in G.pendingEntities:
            entity.canProceed=False
            entity.candidateReceivers=[]
            entity.candidateReceiver=None    
        del self.candidateOperators[:]
        del self.calledOperators[:]
        del self.pendingObjects[:]
        del self.multipleCriterionList[:]
        self.call=False
        
    #=======================================================================
    #                             Sort pendingEntities
    # TODO: sorting them according to the operators schedulingRule
    #=======================================================================
    def sortPendingEntities(self):
        # TODO: to be used for sorting of operators
        if self.candidateOperators:
            for operator in self.candidateOperators:
                if operator.multipleCriterionList:
                    for criterion in operator.multipleCriterionList:
                        if not criterion in self.multipleCriterionList:
                            self.multipleCriterionList.append(criterion)
                else:
                    if not operator.schedulingRule in self.multipleCriterionList:
                        self.multipleCriterionList.append(operator.schedulingRule)
            # TODO: For the moment all operators should have only one scheduling rule and the same among them
            # added for testing
            assert len(self.multipleCriterionList)==1,'The operators must have the same (one) scheduling rule' 
        
            self.activePendingQSorter(criterion=self.multipleCriterionList[0])
        
    #=======================================================================
    #                             Sort candidateOperators
    # TODO: consider if there must be an argument set for the schedulingRules of the Router
    # TODO: consider if the scheduling rule for the operators must be global for all of them
    #=======================================================================
    def sortOperators(self):
        # TODO: there must be criteria for sorting the cadidateOperators
        #if we have sorting according to multiple criteria we have to call the sorter many times
        if self.multipleCriterionList:
            self.activeOperatorQSorter(criterion=self.multipleCriterionList[0])
        
    #========================================================================
    # Find candidate Operators
    # find the operators that can start working now even if they are not called
    #     to be found:
    #     .    the candidate operators
    #     .    their candidate entities (the entities they will process)
    #     .    the candidate receivers of the entities (the stations the operators will be working at)
    #========================================================================
    def findCandidateOperators(self):
        from Globals import G
        # if there are pendingEntities
        if len(G.pendingEntities):
        # for those pending entities that require a manager (MachineManagedJob case)
            for entity in [x for x in G.pendingEntities if x.manager]:
        # if the entity is ready to move to a machine and its manager is available
                if entity.hot and entity.manager.checkIfResourceIsAvailable():
                # for entities of type OrderComponent, if they reside at a conditionalBuffer, 
                #     they must wait till their basicsEnded flag is raised
                    if entity.type=='OrderComponent':
                        from ConditionalBuffer import ConditionalBuffer
                        if (entity.componentType=='Secondary'\
                            and type(entity.currentStation) is ConditionalBuffer\
                            and entity.order.basicsEnded==False):
                            continue
                # unassembled components of a mould must wait at a MouldAssemblyBuffer till the componentsReadyForAssembly flag is raised 
                    from MouldAssemblyBuffer import MouldAssemblyBuffer
                    if type(entity.currentStation) is MouldAssemblyBuffer:
                        if not entity.order.componentsReadyForAssembly:
                            continue
            # for all the possible receivers of an entity check whether they can accept and then set accordingly the canProceed flag of the entity 
                    for nextObject in [object for object in entity.currentStation.next if object.canAcceptEntity(entity)]:
                        entity.canProceed=True
                        entity.candidateReceivers.append(nextObject)
            # if the entity can proceed, add its manager to the candidateOperators list
                    if entity.canProceed and not entity.manager in self.candidateOperators:
                        self.candidateOperators.append(entity.manager)
    
    #=======================================================================
    #         Find the candidateEntities for each candidateOperator
    # find the candidateEntities of each candidateOperator and sort them according
    #     to the scheduling rules of the operator and choose an entity that will be served
    #     and by which machines
    #=======================================================================
    def findCandidateEntities(self):
        from Globals import G
        # TODO: sort according to the number of pending Jobs
        # TODO Have to sort again according to the priority used by the operators
        
        # initialise the operatorsWithOneOption and operatorsWithOneCandidateEntity lists
        operatorsWithOneOption=[]
        operatorsWithOneCandidateEntity=[]
        # for all the candidateOperators
        for operator in self.candidateOperators:
            # find which pendingEntities that can move to machines is the operator managing
            for entity in [x for x in G.pendingEntities if x.canProceed and x.manager==operator]:
                operator.candidateEntities.append(entity)
        # sort the candidate operators so that those who have only one option be served first
            if len(operator.candidateEntities)==1:
                operatorsWithOneCandidateEntity.append(operator)
                # if the candidate entity has only one receiver then append the operator to operatorsWithOneOption list
                if len(operator.candidateEntities[0].candidateReceivers)==1:
                    operatorsWithOneOption.append(operator)
        
        # sort the candidateEntities list of each operator according to its schedulingRule
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            operator.sortCandidateEntities(operator.candidateEntities)
            
        # if there operators that have only one option then sort the candidateOperators according to the first one of these
        # TODO: find out what happens if there are many operators with one option
        # TODO: incorporate that to sortOperators() method
        
        # sort the operators according to their waiting time
        self.candidateOperators.sort(key=lambda x: x.totalWorkingTime)
        if operatorsWithOneOption:
            self.candidateOperators.sort(key=lambda x: x in operatorsWithOneOption, reverse=True)   # sort according to the number of options
            
            
        #===================================================================
#         # TESTING
#         if self.candidateOperators:
#             print '                        findEntities',
#             print [(str(operator.id),[str(candidateEntity.id) for candidateEntity in operator.candidateEntities])\
#                      for operator in self.candidateOperators]
        #===================================================================
            
    #=======================================================================
    # Find candidate entities and their receivers
    # TODO: if there is a critical entity, its manager should be served first
    # TODO: have to sort again after choosing candidateEntity
    #=======================================================================
    def findCandidateReceivers(self):
        # initialise local variables occupiedReceivers and entitiesWithOccupiedReceivers
        occupiedReceivers=[]                    # occupied candidateReceivers of a candidateEntity
        entitiesWithOccupiedReceivers=[]        # list of entities that have no available receivers
        
        # finally we have to sort before giving the entities to the operators
        # If there is an entity which must have priority then it should be assigned first
        
        
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            operator.candidateEntity=operator.candidateEntities[0]
        #===================================================================
        # TESTING
#         print '        first assignment of candidateEntity'
#         print [(str(x.id), str(x.candidateEntity.id)) for x in self.candidateOperators if x.candidateEntity]
        #===================================================================
        # TODO: sorting again after choosing candidateEntity
        self.sortOperators()
        
        
        
        
        
        # for the candidateOperators that do have candidateEntities pick a candidateEntity
        for operator in [x for x in self.candidateOperators if x.candidateEntities]:
            # find the first available entity that has no occupied receivers
            availableEntity=next(x for x in operator.candidateEntities if not x in entitiesWithOccupiedReceivers)
            if availableEntity:
                operator.candidateEntity=availableEntity
        
                # initiate the local list variable available receivers
                availableReceivers=[x for x in operator.candidateEntity.candidateReceivers\
                                            if not x in occupiedReceivers]
                # and pick the object that is waiting for the most time
                if availableReceivers:
                    # TODO: must find the receiver that waits the most
                    maxTimeWaiting=0
                    for object in availableReceivers:
                        timeWaiting=now()-object.timeLastEntityLeft 
                        if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):
                            maxTimeWaiting=timeWaiting
                            availableReceiver=object
                        
                    operator.candidateEntity.candidateReceiver=availableReceiver
                    occupiedReceivers.append(availableReceiver)
                # if there is no available receiver add the entity to the entitiesWithOccupiedReceivers list
                else:
                    entitiesWithOccupiedReceivers.append(availableEntity)
                    operator.candidateEntity.candidateReceiver=None
#         # TODO: sorting again after choosing candidateEntity
#         self.sortOperators()
        #===================================================================
#         # TESTING
#         print '                    findReceivers',
#         print [(str(operator.id),[str(candidateEntity.id) for candidateEntity in operator.candidateEntities])\
#                         for operator in self.candidateOperators]
        #===================================================================
                    
    #=======================================================================
    # Sort Givers
    # TODO: the method currently checks only the first operator of the candidateOperators list
    #    consider populating the controls
    #=======================================================================
    def sortGiverQueue(self):
        # for those operators that do have candidateEntity
        for operator in [x for x in self.candidateOperators if x.candidateEntity]:
            # check whether are called by objects that require the resource
            operator.called = (operator in self.calledOperators)
            # if they are not called or are not in the pendingObjects list sort the queues of the 
            #     of the requesting the operator entities.  
            if not operator.called:
                operator.candidateEntity.currentStation.sortEntitiesForOperator(operator)
            # TODO: if the first candidate is not called then must run again
            #     if the first is called then this one must proceed with get entity 
            elif not operator.candidateEntity.candidateReceiver in self.pendingObjects:
                operator.candidateEntity.currentStation.sortEntitiesForOperator(operator)
            else:
                break
        
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # =======================================================================
    def activePendingQSorter(self, criterion=None):
        from Globals import G
        activeObjectQ=G.pendingEntities
        if not activeObjectQ:
            assert False, "empty candidate list"
        if criterion==None:
            criterion=self.schedulingRule           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            # FIFO sorting has no meaning when sorting candidateEntities
            self.activePendingQSorter('WT')
            # added for testing
#             print 'there is no point of using FIFO scheduling rule for operators candidateEntities,\
#                     WT scheduling rule used instead'
        #if the schedulingRule is based on a pre-defined priority
        elif criterion=="Priority":
            
            activeObjectQ.sort(key=lambda x: x.priority)
        #if the scheduling rule is time waiting (time waiting of machine
        # TODO: consider that the timeLastEntityEnded is not a 
        #     indicative identifier of how long the station was waiting
        elif criterion=='WT':
            
            activeObjectQ.sort(key=lambda x: x.schedule[-1][1])
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
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )
            
    # =======================================================================
    #    sorts the Operators of the Queue according to the scheduling rule
    # =======================================================================
    def activeOperatorQSorter(self, criterion=None):
        activeObjectQ=self.candidateOperators
        if not activeObjectQ:
            assert False, "empty candidateOperators list"
        if criterion==None:
            criterion=self.multipleCriterionList[0]           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            # FIFO sorting has no meaning when sorting candidateEntities
            self.activeOperatorQSorter('WT')
            # added for testing
#             print 'there is no point of using FIFO scheduling rule for operators candidateEntities,\
#                     WT scheduling rule used instead'
        #if the schedulingRule is based on a pre-defined priority
        elif criterion=="Priority":
            
            activeObjectQ.sort(key=lambda x: x.candidateEntity.priority)
        #if the scheduling rule is time waiting (time waiting of machine
        # TODO: consider that the timeLastEntityEnded is not a 
        #     indicative identifier of how long the station was waiting
        elif criterion=='WT':
            
            activeObjectQ.sort(key=lambda x: x.candidateEntity.schedule[-1][1])
        #if the schedulingRule is earliest due date
        elif criterion=="EDD":
            
            activeObjectQ.sort(key=lambda x: x.candidateEntity.dueDate)   
        #if the schedulingRule is earliest order date
        elif criterion=="EOD":
            
            activeObjectQ.sort(key=lambda x: x.candidateEntity.orderDate)
        #if the schedulingRule is to sort Entities according to the stations they have to visit
        elif criterion=="NumStages":
            
            activeObjectQ.sort(key=lambda x: len(x.candidateEntity.remainingRoute), reverse=True)  
        #if the schedulingRule is to sort Entities according to the their remaining processing time in the system
        elif criterion=="RPC":
            
            for entity in [operator.candidateEntity for operator in activeObjectQ]:
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))           
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.candidateEntity.remainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            
            for entity in [operator.candidateEntity for operator in activeObjectQ]:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.candidateEntity.processingTimeInNextStation, reverse=True)             
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        elif criterion=="SPT":
            
            for entity in [operator.candidateEntity for operator in activeObjectQ]:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.candidateEntity.processingTimeInNextStation) 
        #if the schedulingRule is to sort Entities based on the minimum slackness
        elif criterion=="MS":
            
            for entity in [operator.candidateEntity for operator in activeObjectQ]:
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))              
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: (x.candidateEntity.dueDate-x.candidateEntity.remainingProcessingTime))  
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        elif criterion=="WINQ":
            
            from Globals import G
            for entity in [operator.candidateEntity for operator in activeObjectQ]:
                nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                for obj in G.ObjList:
                    if obj.id in nextObjIds:
                        nextObject=obj
                entity.nextQueueLength=len(nextObject.getActiveObjectQueue())           
            activeObjectQ.sort(key=lambda x: x.candidateEntity.nextQueueLength)
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )