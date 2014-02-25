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
models a repairman that can fix a machine when it gets failures
'''

from SimPy.Simulation import Resource, now
from Repairman import Repairman

# ===========================================================================
#                 the resource that operates the machines
# ===========================================================================
class Operator(Repairman):
    
    def __init__(self, id, name, capacity=1, schedulingRule="FIFO"):
        Repairman.__init__(self,id=id,name=name,capacity=capacity)
        self.type="Operator"
        self.activeCallersList=[]
        self.schedulingRule=schedulingRule
#         #=======================================================================
#         # TESTING
#         print now(), self.objName, 'schedulingRule'
#         print self.schedulingRule
#         #=======================================================================

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
            self.activeQSorter(self.schedulingRule)
    
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # =======================================================================
    def activeQSorter(self, criterion=None):
        activeObjectQ=self.activeCallersList
        if criterion==None:
            criterion=self.schedulingRule           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            pass
        #if the schedulingRule is based on a pre-defined priority
        # TODO: entityToGet is not updated for all available Objects
        elif criterion=="Priority":
            activeObjectQ.sort(key=lambda x: x.entityToGet.priority)
        #if the scheduling rule is time waiting (time waiting of machine
        # TODO: consider that the timeLastEntityEnded is not a 
        #     indicative identifier of how long the station was waiting
        elif criterion=='WT':
            activeObjectQ.sort(key=lambda x: x.timeLastEntityEnded)
        #if the schedulingRule is earliest due date
        elif criterion=="EDD":
            activeObjectQ.sort(key=lambda x: x.entityToGet.dueDate)   
        #if the schedulingRule is earliest order date
        elif criterion=="EOD":
            activeObjectQ.sort(key=lambda x: x.entityToGet.orderDate)
        #if the schedulingRule is to sort Entities according to the stations they have to visit
        elif criterion=="NumStages":
            activeObjectQ.sort(key=lambda x: len(x.entityToGet.remainingRoute), reverse=True)  
        #if the schedulingRule is to sort Entities according to the their remaining processing time in the system
        # TODO: have to compare the entitiesToGet
        elif criterion=="RPC":
            for object in activeObjectQ:
                entity=object.entityToGet
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))           
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.entityToGet.remainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        # TODO: have to compare the entitiesToGet
        elif criterion=="LPT":
            for object in activeObjectQ:
                entity=object.entityToGet
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.entityToGet.processingTimeInNextStation, reverse=True)             
        #if the schedulingRule is to sort Entities according to shortest processing time first in the next station
        # TODO: have to compare the entitiesToGet
        elif criterion=="SPT":
            for object in activeObjectQ:
                entity=object.entityToGet
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                if processingTime:
                    entity.processingTimeInNextStation=float(processingTime.get('mean',0))
                else:
                    entity.processingTimeInNextStation=0
            activeObjectQ.sort(key=lambda x: x.entityToGet.processingTimeInNextStation) 
        #if the schedulingRule is to sort Entities based on the minimum slackness
        # TODO: have to compare the entitiesToGet
        elif criterion=="MS":
            for object in activeObjectQ:
                object.entityToGet
                RPT=0
                for step in entity.remainingRoute:
                    processingTime=step.get('processingTime',None)
                    if processingTime:
                        RPT+=float(processingTime.get('mean',0))              
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: (x.entityToGet.dueDate-x.entityToGet.remainingProcessingTime))  
        #if the schedulingRule is to sort Entities based on the length of the following Queue
        # TODO: have to compare the entitiesToGet
        elif criterion=="WINQ":
            from Globals import G
            for object in activeObjectQ:
                entity=object.entityToGet
                nextObjIds=entity.remainingRoute[1].get('stationIdsList',[])
                for obj in G.ObjList:
                    if obj.id in nextObjIds:
                        nextObject=obj
                entity.nextQueueLength=len(nextObject.getActiveObjectQueue())           
            activeObjectQ.sort(key=lambda x: x.entityToGet.nextQueueLength)
        else:
            assert False, "Unknown scheduling criterion %r" % (criterion, )


