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
Created on 01 Oct 2013

@author: George
'''
'''
Job is an Entity that implements the logic of a job shop. Job carries attributes for its route 
in the system and also in the processing times at each station
'''

from Globals import G
from Entity import Entity

# =======================================================================
# The job object 
# =======================================================================
class Job(Entity):                                  # inherits from the Entity class   
    type="Job"
    
    def __init__(self, id=None, name=None, route=[], priority=0, dueDate=None, orderDate=None, extraPropertyDict=None,isCritical=False):
        Entity.__init__(self, id=id,name=name, priority=priority, dueDate=dueDate, orderDate=orderDate, isCritical=isCritical)
        # instance specific attributes 
        self.id=id                                  # id
        # information on the routing and the stops of the entity
        self.route=route                            # the route that the job follows, 
                                                    # also contains the processing times in each station
        self.remainingRoute=list(route)                   # the remaining route. in the beginning 
                                                    # this should be the same as the full route
        # the scheduling of the entity as resolved by the simulation
#         self.schedule=[]                            # keeps the result of the simulation. 
#                                                     # A list with the stations and time of entrance
        self.extraPropertyDict = extraPropertyDict
        # variable used to differentiate entities with and entities without routes
        self.family='Job'
        # used by printRoute
        self.alias='J'+str(len(G.JobList))
    
    # =======================================================================
    # outputs results to JSON File 
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1):              #if we had just one replication output the results to excel
            json={}                                 # dictionary holding information related to the specific entity
            json['_class'] = 'Dream.Job'
            json['id'] = str(self.id)
            json['results'] = {}
            #json['extraPropertyDict'] = self.extraPropertyDict
            # if there is schedule
            if self.schedule:
                #if the Job has reached an exit, input completion time in the results
                if self.schedule[-1][0].type=='Exit':
                    json['results']['completionTime']=self.schedule[-1][1]  
                    completionTime=self.schedule[-1][1]  
                # TODO
                # if the entity is of type Mould and the last object holding it is orderDecomposition
                # XXX now Orders do not run through the system but OrderDesigns do
                elif self.type=='OrderDesign' and self.schedule[-1][0].type=='OrderDecomposition': #
                    json['results']['completionTime']=self.schedule[-1][1]  
                    completionTime=self.schedule[-1][1]  
                # TODO : check if there is a need for setting a different 'type' for the MouldAssembly than 'Machine'
                #    ask Georgios if the method __class__.__name__ of finding the class type of the last step is correct
                # if the entity is of type orderComponent and the last step in it's schedule is Assembly
                elif self.type=='OrderComponent' and self.schedule[-1][0].__class__.__name__=='MouldAssembly':
                    json['results']['completionTime']=self.schedule[-1][1]  
                    completionTime=self.schedule[-1][1]  
                #else input "still in progress"
                else:
                    json['results']['completionTime']="still in progress"  
                    completionTime=None
                
                if completionTime and self.dueDate:
                    delay=completionTime-self.dueDate
                    json['results']['delay']=delay
                    
                json['results']['schedule']=[]
                i=0
                for record in self.schedule:               
                    json['results']['schedule'].append({})                              # dictionary holding time and 
                    json['results']['schedule'][i]['stationId']=record[0].id            # id of the Object
                    json['results']['schedule'][i]['entranceTime']=record[1]            # time entering the Object
                    i+=1             
                G.outputJSON['elementList'].append(json)
    
    # =======================================================================
    # initializes all the Entity for a new simulation replication 
    # =======================================================================
    def initialize(self):
        # has to be re-initialized each time a new Job is added
        self.remainingRoute=list(self.route)
        # check the number of stations in the stationIdsList for the current step (0)
        # if it is greater than 1 then there is a problem definition
        objectIds = self.route[0].get('stationIdsList',[])
        try:
            if len(objectIds)==1:
                from Globals import findObjectById
                self.currentStation=findObjectById(objectIds[0])
            else:
                from Globals import SetWipTypeError
                raise SetWipTypeError('The starting station of the the entity is not defined uniquely')
        except SetWipTypeError as setWipError:
            print 'WIP definition error: {0}'.format(setWipError)
#         self.currentStation=self.route[0][0]
    
    #===========================================================================
    # check if the entity can proceed to an operated machine, for use by Router
    #===========================================================================
    def canProceed(self):
        activeObject=self.currentStation
        return activeObject.canDeliver(self)
     
    #===========================================================================
    # method that finds a receiver for a candidate entity
    #===========================================================================
    def findCandidateReceiver(self):
        from Globals import G
        router=G.Router
        # initiate the local list variable available receivers
        availableReceivers=[x for x in self.candidateReceivers\
                                        if not x in router.occupiedReceivers]
        # and pick the object that is waiting for the most time
        if availableReceivers:
            # find the receiver that waits the most
            availableReceiver=self.currentStation.selectReceiver(availableReceivers)
            router.occupiedReceivers.append(availableReceiver)
        # if there is no available receiver add the entity to the entitiesWithOccupiedReceivers list
        else:
            router.entitiesWithOccupiedReceivers.append(self)
            availableReceiver=None
        # if the sorting flag is not set then the sorting of each queue must prevail in case of operators conflict
        if not router.sorting and not availableReceiver and bool(availableReceivers):
            availableReceiver=self.currentStation.selectReceiver(self.candidateReceivers)
            if not self in router.conflictingEntities:
                router.conflictingEntities.append(self)
        return availableReceiver
    
    #===========================================================================
    # print the route (the different stations the entity moved through)
    #===========================================================================
    def printRoute(self):
        if self.schedule:
            for record in self.schedule:
                # find the station of this step
                station=record[0]               # XXX should also hold a list with all the machines G.MachineList?
                # find the column corresponding to the machine
                # XXX each machine should have at least 3 columns, 2 for the jobs and one for operators
                if station in G.MachineList:
                    machine_index=G.MachineList.index(station)
                    # find the entrance time of this step
                    entrance_time=record[1]         # the time entity entered station
                    # find the row corresponding to the event and start placing the name of the Job in the cells
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
                        col_to_write=station.station_col_inds[0]                                                                        # XXX
                        stepDone=False
                        # check if the cell is already written, if yes, then modify it adding the new jobs but not overwrite it
                        if not G.cells_to_write:
                            G.cells_to_write.append({'row':step+1,
                                          'col':col_to_write,
                                          'job':self.alias})
                            G.routeTraceSheet.write(step+1, col_to_write, self.alias)
                            continue
                        for cell in G.cells_to_write:
                            if cell['row']==step+1 and cell['col']==col_to_write:
                                next_col=station.station_col_inds[1]                                                                    # XXX
                                if not next_col in [x['col'] for x in G.cells_to_write if x['row']==step+1]:                            # XXX
                                    G.cells_to_write.append({'row':step+1,                                                              # XXX
                                                  'col':next_col,                                                                       # XXX
                                                  'job':self.alias})                                                                    # XXX
                                    G.routeTraceSheet.write(step+1, next_col, self.alias)                                               # XXX
                                    stepDone=True                                                                                       # XXX
                                    break                                                                                               # XXX
                                cell['job']=cell['job']+','+self.alias
                                G.routeTraceSheet.write(cell['row'], cell['col'], cell['job'])
                                stepDone=True
                                break
                        if not stepDone:
                            G.cells_to_write.append({'row':step+1,
                                          'col':col_to_write,
                                          'job':self.alias})
                            G.routeTraceSheet.write(step+1, col_to_write, self.alias)

