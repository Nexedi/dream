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
Created on 22 Nov 2012

@author: Ioannis
'''

'''
models an operator that operates a machine
'''

from SimPy.Simulation import Resource, now
from Repairman import Repairman

# ===========================================================================
#                 the resource that operates the machines
# ===========================================================================
class Operator(Repairman): # XXX isn't it the other way around ?
    class_name = 'Dream.Operator'

    def __init__(self, id, name, capacity=1, schedulingRule="FIFO"):
        Repairman.__init__(self, id=id, name=name, capacity=capacity)
        self.type="Operator"
        self.activeCallersList=[]               # the list of object that request the operator
        self.schedulingRule=schedulingRule      #the scheduling rule that the Queue follows
        self.multipleCriterionList=[]           #list with the criteria used to sort the Entities in the Queue
        SRlist = [schedulingRule]
        if schedulingRule.startswith("MC"):     # if the first criterion is MC aka multiple criteria
            SRlist = schedulingRule.split("-")  # split the string of the criteria (delimiter -)
            self.schedulingRule=SRlist.pop(0)   # take the first criterion of the list
            self.multipleCriterionList=SRlist   # hold the criteria list in the property multipleCriterionList
 
        for scheduling_rule in SRlist:
          if scheduling_rule not in ("FIFO", "Priority","WT", "EDD", "EOD",
            "NumStages", "RPC", "LPT", "SPT", "MS", "WINQ"):
            raise ValueError("Unknown scheduling rule %s for %s" %
              (scheduling_rule, id))
        # the station that the operator is assigned to
        self.operatorAssignedTo=None
        
        # variables to be used by OperatorRouter
        self.candidateEntities=[]               # list of the entities requesting the operator at a certain simulation Time
        self.candidateEntity=None               # the entity that will be chosen for processing
    
    # =======================================================================
    #    sorts the candidateEntities of the Operator according to the scheduling rule
    #     TODO: clean the comments
    #     TODO: maybe the argument is not needed. the candidate entities is a variable of the object
    # =======================================================================
    def sortCandidateEntities(self, candidateEntities=[]):
        pass
#         # TODO: have to consider what happens in case of a critical order
#         # FIFO sorting has no meaning when sorting candidateEntities
#         if self.schedulingRule=="FIFO":
#             self.activeCandidateQSorter('WT', candidateEntities=candidateEntities)
#         #if we have sorting according to multiple criteria we have to call the sorter many times
#         elif self.schedulingRule=="MC":
#             for criterion in reversed(self.multipleCriterionList):
#                self.activeCandidateQSorter(criterion=criterion, candidateEntities=candidateEntities) 
#         #else we just use the default scheduling rule
#         else:
#             self.activeCandidateQSorter(self.schedulingRule, candidateEntities=candidateEntities)

    # =======================================================================
    #    sorts the activeCallerrs of the Operator according to the scheduling rule
    #    TODO: change the name of the class (they are not entities)
    # =======================================================================
    def sortEntities(self):
        #if we have sorting according to multiple criteria we have to call the sorter many times
        if self.schedulingRule=="MC":
            for criterion in reversed(self.multipleCriterionList):
               self.activeQSorter(criterion=criterion) 
        #else we just use the default scheduling rule
        else:
            self.activeQSorter(self.schedulingRule)
    
    # =======================================================================
    #    sorts the activeCallers of the activeCallersList according to the scheduling rule
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
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().priority)
        #if the scheduling rule is time waiting (time waiting of machine
        # TODO: consider that the timeLastEntityEnded is not a 
        #     indicative identifier of how long the station was waiting
        elif criterion=='WT':
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().schedule[-1][1])
        #if the schedulingRule is earliest due date
        elif criterion=="EDD":
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().dueDate)   
        #if the schedulingRule is earliest order date
        elif criterion=="EOD":
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().orderDate)
        #if the schedulingRule is to sort Entities according to the stations they have to visit
        elif criterion=="NumStages":
            activeObjectQ.sort(key=lambda x: len(x.identifyEntityToGet().remainingRoute), reverse=True)  
        #if the schedulingRule is to sort Entities according to the their remaining processing time in the system
        elif criterion=="RPC":
            for object in activeObjectQ:
                entity=object.identifyEntityToGet()
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))           
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().remainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            for object in activeObjectQ:
                entity=object.identifyEntityToGet()
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().processingTimeInNextStation, reverse=True)             
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        elif criterion=="SPT":
            for object in activeObjectQ:
                entity=object.identifyEntityToGet()
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().processingTimeInNextStation) 
        #if the schedulingRule is to sort Entities based on the minimum slackness
        elif criterion=="MS":
            for object in activeObjectQ:
                object.identifyEntityToGet()
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))              
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: (x.identifyEntityToGet().dueDate-x.identifyEntityToGet().remainingProcessingTime))  
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        elif criterion=="WINQ":
            from Globals import G
            for object in activeObjectQ:
                entity=object.identifyEntityToGet()
                nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                for obj in G.ObjList:
                    if obj.id in nextObjIds:
                        nextObject=obj
                entity.nextQueueLength=len(nextObject.getActiveObjectQueue())           
            activeObjectQ.sort(key=lambda x: x.identifyEntityToGet().nextQueueLength)
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )


