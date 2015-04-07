import Globals
import xlwt
from Globals import ManPyEnvironment

import OrderComponent
import Mould
import Order
import OrderDesign

JOB_SHOP_TECHNOLOGY_SEQ=['CAD','CAM','MILL','EDM','ASSM','MA','INJM','IM' ]
ORDER_COMPONENT_TYPE_SET=set(['OrderComponent','Design','Mould'])

def sortMachines():
    '''sort the machines according to the set provided by JOB_SHOP_TECHNOLOGY_SEQ'''
    for tech in JOB_SHOP_TECHNOLOGY_SEQ:
        G.MachineList.sort(key=lambda x: x.id.startswith(tech))

def getEventsList(objectsList=[]):
    '''create an event list from the schedules of the objects provided'''
    events_list=[]  # list to hold the events of the system
    for object in objectsList:
        if object.schedule:
            for record in object.schedule:
                if not record["entranceTime"] in events_list:
                    events_list.append(record["entranceTime"])
                exit_time = record.get("exitTime", None)
                if exit_time != None:
                    if not exit_time in events_list:
                        events_list.append(exit_time)
    return events_list

def outputRoute(environment):
    '''            
        prints the routes of the Jobs through the model as a table 
        the horizontal axis represents the different stations of the model 
        the vertical axis represents the time axis (events as points in time)
        each job will move through the stations for a specific time
        e.g.
    
    time\machines            M1        M2        M3        M4        M5
                
    t1                       J1
    t2                       J1                            J2
    t3                       J1                 J3         J2
    t4                       J1                 J3         J2        J4
    t5                                J2        J3                   J4
    t6                                J2        J3         J1        J4
    t7                                J2                   J1
    
        TODO: create multiple columns for each machine as one machine can receive more than one jobs at the same time (assembly)
        or can get an entity when an entity is removed from it (the cell of this machine for the specific time is occupied by the last
        job accessing it) 
    '''
    
    # xx for each station allocate 2 rows and a 3rd one for operators
    
    if environment.trace=='Yes':
        if environment.JobList:
            environment.routeSheetIndex=environment.sheetIndex+1
            # add one more sheet to the trace file
            environment.routeTraceSheet=environment.traceFile.add_sheet('sheet '+str(environment.routeSheetIndex)+' route', cell_overwrite_ok=True)
            number_of_machines=len(environment.MachineList)
            sortMachines()  # sort the machines according to the priority specified in JOB_SHOP_TECHNOLOGY_SEQ
            # get the events list
            environment.events_list=getEventsList(environment.JobList+environment.OperatorsList)
            environment.events_list.sort(cmp=None, key=None, reverse=False)     # sort the events
            number_of_events=len(environment.events_list)                       # keep the total number of events 
            # create a table number_of_events X number_of_machines
            environment.routeTraceSheet.write(0,0, 'Time/Machines')
            # write the events in the first column and the machineIDs in the first row
            for j, event in enumerate(environment.events_list):
                environment.routeTraceSheet.write(j+1,0,float(event))
            # XXX create 3 times as many columns as the number of machines
            for j, machine in enumerate(environment.MachineList):
                machine.station_col_inds=range(j*3+1,j*3+3)
                machine.op_col_indx=j*3+3
                environment.routeTraceSheet.write_merge(0,0,j*3+1,j*3+3,str(machine.id))

            # sort the jobs according to their name
            environment.JobList.sort(key=lambda x:x.id)
            
            environment.cells_to_write=[]
            for job in environment.JobList:
                job.printRoute()
            
            # list of cells to be written
            environment.cells_to_write=[]
            # for every job in the JobList
            for worker in environment.OperatorsList:
                worker.printRoute()
            # reset list of cells to be written
            del environment.cells_to_write[:]
            del environment.events_list[:]
            
            # print aliases
            try:
                sample_job=next(x for x in environment.JobList)
                if sample_job.__class__.__name__ in ORDER_COMPONENT_TYPE_SET:
                    environment.JobList.sort(key=lambda x:x.order.id)
            except:
                pass
            for j,job in enumerate(environment.JobList):
                if job.schedule:
                    environment.routeTraceSheet.write(number_of_events+2+j, 0, job.id)
                    environment.routeTraceSheet.write(number_of_events+2+j, 1, job.alias)
            