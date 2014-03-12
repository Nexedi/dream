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
Created on 13 Feb 2013

@author: Ioannis
'''

'''
models a entity/job assigned operator (manager)
'''

from SimPy.Simulation import Resource, now
from Operator import Operator

# ===========================================================================
#                 the resource that operates the machines
# ===========================================================================
class OperatorManagedJob(Operator):
    
#     def __init__(self, id, name, capacity=1,schedulingRule="FIFO"):
#         Operator.__init__(self,id=id,name=name,capacity=capacity,schedulingRule=schedulingRule)
#         self.operatorAssignedTo=None
    
    # =======================================================================
    #                    checks if the worker is available
    #     it is called only by the have to dispose of a QueueManagedJob
    #                         and its sortEntities
    # =======================================================================       
    def checkIfResourceIsAvailable(self,callerObject=None):
        activeResourceQueue = self.getResourceQueue()
        # in case the operator has the flag operatorAssigned raised 
        #    (meaning the operator will explicitly be assigned to a machine)
        #    return false even if he is free
        # If there is no callerObject defined then do not check the operatorAssignedTo variable
        if callerObject:
            # if the operator is not yet assigned then return the default behaviour
            if self.operatorAssignedTo==None:
                return len(activeResourceQueue)<self.capacity
            # otherwise, in case the operator is occupied, check if the occupier is the 
            #     object the operator is assigned to
            else:
                if len(activeResourceQueue):
                    if self.operatorAssignedTo==activeResourceQueue[0].victim:
                        return self.operatorAssignedTo==callerObject
                return (self.operatorAssignedTo==callerObject) and len(self.Res.activeQ)<self.capacity
        # otherwise, (if the callerObject is None) check if the operator is assigned and if yes
        #     then perform the default behaviour
        else:
#             if self.operatorAssignedTo==None:
#                 return False
            return len(self.Res.activeQ)<self.capacity
        
    # =======================================================================
    #    sorts the candidateEntities of the Operator according to the scheduling rule
    # =======================================================================
    def sortCandidateEntities(self, candidateEntities=[]):
        # TODO: have to consider what happens in case of a critical order
        #if we have sorting according to multiple criteria we have to call the sorter many times
        if self.schedulingRule=="MC":
            for criterion in reversed(self.multipleCriterionList):
               self.activeCandidateQSorter(criterion=criterion, candidateEntities=candidateEntities) 
        #else we just use the default scheduling rule
        else:
            self.activeCandidateQSorter(self.schedulingRule, candidateEntities=candidateEntities)
            
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # =======================================================================
    # TODO: entityToGet is not updated for all stations, consider using it for all stations or withdraw the idea
    def activeCandidateQSorter(self, criterion=None, candidateEntities=[]):
        activeObjectQ=candidateEntities
        if not activeObjectQ:
            assert False, "empty candidate list"
        if criterion==None:
            criterion=self.schedulingRule           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            # FIFO sorting has no meaning when sorting candidateEntities
            self.activeCandidateQSorter('WT', candidateEntities=candidateEntities)
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
    #    sorts the Entities of the Queue according to the scheduling rule
    # =======================================================================
    # TODO: entityToGet is not updated for all stations, consider using it for all stations or withdraw the idea
    def activeQSorter(self, criterion=None):
        activeObjectQ=self.activeCallersList
        if criterion==None:
            criterion=self.schedulingRule           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            pass
        #if the schedulingRule is based on a pre-defined priority
        elif criterion=="Priority":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            # TODO: the entities should be also sort according to their waiting time in case the priority is the same
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].priority)
        #if the scheduling rule is time waiting (time waiting of machine
        # TODO: consider that the timeLastEntityEnded is not a 
        #     indicative identifier of how long the station was waiting
        elif criterion=='WT':
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
                
            
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].schedule[-1][1])
        #if the schedulingRule is earliest due date
        elif criterion=="EDD":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].dueDate)   
        #if the schedulingRule is earliest order date
        elif criterion=="EOD":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].orderDate)
        #if the schedulingRule is to sort Entities according to the stations they have to visit
        elif criterion=="NumStages":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            activeObjectQ.sort(key=lambda x: len(x.giver.getActiveObjectQueue()[0].remainingRoute), reverse=True)  
        #if the schedulingRule is to sort Entities according to the their remaining processing time in the system
        elif criterion=="RPC":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            for object in activeObjectQ:
                entity=object.giver.getActiveObjectQueue()[0]
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))           
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].remainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            for object in activeObjectQ:
                entity=object.giver.getActiveObjectQueue()[0]
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].processingTimeInNextStation, reverse=True)             
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        elif criterion=="SPT":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            for object in activeObjectQ:
                entity=object.giver.getActiveObjectQueue()[0]
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].processingTimeInNextStation) 
        #if the schedulingRule is to sort Entities based on the minimum slackness
        elif criterion=="MS":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            for object in activeObjectQ:
                entity=object.giver.getActiveObjectQueue()[0]
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))              
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: (x.giver.getActiveObjectQueue()[0].dueDate-x.giver.getActiveObjectQueue()[0].remainingProcessingTime))  
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        elif criterion=="WINQ":
            
            for object in activeObjectQ:
                object.giver.sortEntitiesForOperator(self)
            
            from Globals import G
            for object in activeObjectQ:
                entity=object.giver.getActiveObjectQueue()[0]
                nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                for obj in G.ObjList:
                    if obj.id in nextObjIds:
                        nextObject=obj
                entity.nextQueueLength=len(nextObject.getActiveObjectQueue())           
            activeObjectQ.sort(key=lambda x: x.giver.getActiveObjectQueue()[0].nextQueueLength)
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )