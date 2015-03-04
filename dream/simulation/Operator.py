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

# from SimPy.Simulation import Resource, now
import simpy
import xlwt
from ObjectResource import ObjectResource

# ===========================================================================
#                 the resource that operates the machines
# ===========================================================================
class Operator(ObjectResource):
    family='Operator'  
    
    def __init__(self, id, name, capacity=1, schedulingRule='FIFO', skillDict={}, skills=[], available=True,ouputSchedule=False,**kw):
        ObjectResource.__init__(self,id=id, name=name)
        self.objName=name
        self.capacity=int(capacity)      # repairman is an instance of resource
        self.type="Operator"
        # lists to hold statistics of multiple runs
        self.Waiting=[]             # holds the percentage of waiting time 
        self.Working=[]             # holds the percentage of working time 
        self.OffShift=[]             # holds the percentage of working time 

    
        # the following attributes are not used by the Repairman
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
        
        # the station that the operator is assigned to
        self.operatorAssignedTo=None
        # the station that the operator is dedicated to
        self.operatorDedicatedTo=None
        # the station the operator currently operating
        self.workingStation=None
        
        # variables to be used by OperatorRouter
        self.candidateEntities=[]               # list of the entities requesting the operator at a certain simulation Time
        self.candidateEntity=None               # the entity that will be chosen for processing
        self.candidateStations=[]               # list of candidateStations of the stations (those stations that can receive an entity)
        
        self.schedule=[]                        # the working schedule of the resource, the objects the resource was occupied by and the corresponding times
        # alias used by printRoute
        self.alias=self.id
        # list attribute that describes the skills of the operator in terms of stations he can operate
        self.skillsList=skills
        # skils dict (defining also if the skill is regarding different operations on the same technology)
        self.skillDict = skillDict
        # flag to show if the resource is available at the start of simulation
        self.available=available
        from Globals import G
        G.OperatorsList.append(self) 
        # flag to show if the operator will output his schedule in the results
        self.ouputSchedule=ouputSchedule
        
    def initialize(self):
        ObjectResource.initialize(self)
        # flag that shows if the resource is on shift
        self.onShift=True
        self.totalWorkingTime=0         #holds the total working time
        self.totalWaitingTime=0         #holds the total waiting time
        self.totalOffShiftTime=0        #holds the total off-shift time
        self.timeLastShiftStarted=0                     #holds the time that the last shift of the object started
        self.timeLastShiftEnded=0                       #holds the time that the last shift of the object ended
        self.candidateStation=None      #holds the candidate receiver of the entity the resource will work on - used by router
        
    @staticmethod
    def getSupportedSchedulingRules():
        return ("FIFO", "Priority", "WT", "EDD", "EOD",
            "NumStages", "RPC", "LPT", "SPT", "MS", "WINQ")
    
    #===========================================================================
    # assign an operator
    #===========================================================================
    def assignTo(self, callerObject=None):
        assert callerObject!=None, 'the operator cannot be assigned to None'
        self.operatorAssignedTo=callerObject
    
    #===========================================================================
    # un-assign an operator
    #===========================================================================
    def unAssign(self):
        self.operatorAssignedTo=None
    
    #===========================================================================
    # check whether the operator is assigned
    #===========================================================================
    def isAssignedTo(self):
        return self.operatorAssignedTo
    
    #===========================================================================
    # sort candidate stations
    #===========================================================================
    def sortStations(self):
        from Globals import G
        router=G.RouterList[0]
        candidateMachines=self.candidateStations
        # for the candidateMachines
        if candidateMachines:
            # choose the one that waits the most time and give it the chance to grasp the resource
            for machine in candidateMachines:
#                 machine.critical=False
                if machine.broker.waitForOperator:
                    machine.timeWaiting=self.env.now-machine.broker.timeWaitForOperatorStarted
                else:
                    machine.timeWaiting=self.env.now-machine.timeLastEntityLeft
        # sort the stations according their timeWaiting
        self.candidateStations.sort(key= lambda x: x.timeWaiting, reverse=True)
    
    #===========================================================================
    # sort entities provided in a list
    #===========================================================================
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
        activeObjectQ=self.candidateEntities
        
        if criterion==None:
            criterion=self.schedulingRule           
        #if the schedulingRule is first in first out
        if criterion=="FIFO": 
            # FIFO sorting has no meaning when sorting candidateEntities
            self.activeQSorter('WT')
        #if the schedulingRule is based on a pre-defined priority
        elif criterion=="Priority":
            
            activeObjectQ.sort(key=lambda x: x.priority)
        #if the scheduling rule is time waiting (time waiting of machine)
        elif criterion=='WT':
            
            for part in activeObjectQ:
                part.factor=0
                if part.schedule:
                   part.factor=self.env.now-part.schedule[-1][1] 
            
            activeObjectQ.sort(key=lambda x: x.factor, reverse=True)
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
                entity.remainingProcessingTime=RPT
            activeObjectQ.sort(key=lambda x: x.remainingProcessingTime, reverse=True)     
        #if the schedulingRule is to sort Entities according to longest processing time first in the next station
        elif criterion=="LPT":
            
            for entity in activeObjectQ:
                processingTime = entity.remainingRoute[0].get('processingTime',None)
                entity.processingTimeInNextStation=float(processingTime.get('Fixed',{}).get('mean',0))
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
    #            actions to be taken after the simulation ends
    # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime
            
        # if the Operator is currently working we have to count the time of this work    
        if len(self.getResourceQueue())>0:
            self.totalWorkingTime+=self.env.now-self.timeLastOperationStarted
        
        # if the Operator is currently off-shift we have to count the time of this work    
        if not self.onShift and len(self.getResourceQueue())==0:
            self.totalOffShiftTime+=self.env.now-self.timeLastShiftEnded
                
        # Operator was idle when he was not in any other state
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime-self.totalOffShiftTime   
        # update the waiting/working time percentages lists
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)
        self.OffShift.append(100*self.totalOffShiftTime/MaxSimtime)

    # =======================================================================
    #                    outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        json = {'_class': 'Dream.%s' % self.__class__.__name__,
                'id': self.id,
                'family': self.family,
                'results': {}}
        json['results']['working_ratio'] = self.Working
        json['results']['waiting_ratio'] = self.Waiting
        json['results']['off_shift_ratio'] = self.OffShift
        if self.ouputSchedule:
            json['results']['schedule']=[]
            for record in self.schedule:
                try:
                    stationId=record[0].id
                except AttributeError:
                    stationId=record[0]['id']                 
                if len(record)==3:
                    json['results']['schedule'].append({
                        'stationId':stationId,
                        'entranceTime':record[1],
                        'exitTime':record[2]})
                else:
                    json['results']['schedule'].append({
                        'stationId':stationId,
                        'entranceTime':record[1]})
        G.outputJSON['elementList'].append(json)
    
    #===========================================================================
    # print the route (the different stations the resource was occupied by)
    #===========================================================================
    def printRoute(self):
        if self.schedule:
            for record in self.schedule:
                # find the station of this step
                station=record[0]               # XXX should also hold a list with all the machines G.MachineList?
                # find the column corresponding to the machine
                from Globals import G
                # XXX each machine should have at least 3 columns, 2 for the jobs and one for operators
                if station in G.MachineList:
                    machine_index=G.MachineList.index(station)
                    # find the entrance time of this step
                    entrance_time=record[1]         # the time entity entered station
                    # find the row corresponding to the event and start placing the name of the Job in the G.cells_to_write
                    entrance_time_index=G.events_list.index(entrance_time)
                    # find the exit time of this step
                    if len(record)==3:
                        exit_time=record[2]             # the time the entity exited the station
                        # find the row corresponding to the event and place the name of the Job in the cell, this is the last cell of this processing
                        exit_time_index=G.events_list.index(exit_time)
                    elif len(record)!=3:
                        exit_time_index=len(G.events_list)
                    # for the rows with indices entrance_time_index to exit_time_index print the id of the Job in the column of the machine_index
                    for step in range(entrance_time_index,exit_time_index+1, 1):
                        col_to_write=station.op_col_indx
                        stepDone=False
                        # check if the cell is already written, if yes, then modify it adding the new jobs but not overwrite it
                        if not G.cells_to_write:
                            G.cells_to_write.append({'row':step+1,
                                                     'col':col_to_write,
                                                     'worker':self.alias})
                            G.routeTraceSheet.write(step+1, col_to_write, self.alias)
                            continue
                        for cell in G.cells_to_write:
                            if cell['row']==step+1 and cell['col']==col_to_write:
                                cell['worker']=cell['worker']+','+self.alias
                                G.routeTraceSheet.write(cell['row'], cell['col'], cell['worker'])
                                stepDone=True
                                break
                        if not stepDone:
                            G.cells_to_write.append({'row':step+1,
                                                     'col':col_to_write,
                                                     'worker':self.alias})
                            G.routeTraceSheet.write(step+1, col_to_write, self.alias)