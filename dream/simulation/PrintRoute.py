import Globals
import xlwt
from Globals import G

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

def outputRoute():
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
    
    if G.trace=='Yes':
        if G.JobList:
            G.routeSheetIndex=G.sheetIndex+1
            # add one more sheet to the trace file
            G.routeTraceSheet=G.traceFile.add_sheet('sheet '+str(G.routeSheetIndex)+' route', cell_overwrite_ok=True)
            number_of_machines=len(G.MachineList)
            sortMachines()  # sort the machines according to the priority specified in JOB_SHOP_TECHNOLOGY_SEQ
            # get the events list
            G.events_list=getEventsList(G.JobList+G.OperatorsList)
            G.events_list.sort(cmp=None, key=None, reverse=False)     # sort the events
            number_of_events=len(G.events_list)                       # keep the total number of events 
            # create a table number_of_events X number_of_machines
            G.routeTraceSheet.write(0,0, 'Time/Machines')
            # write the events in the first column and the machineIDs in the first row
            for j, event in enumerate(G.events_list):
                G.routeTraceSheet.write(j+1,0,float(event))
            # XXX create 3 times as many columns as the number of machines
            for j, machine in enumerate(G.MachineList):
                machine.station_col_inds=range(j*3+1,j*3+3)
                machine.op_col_indx=j*3+3
                G.routeTraceSheet.write_merge(0,0,j*3+1,j*3+3,str(machine.id))

            # sort the jobs according to their name
            G.JobList.sort(key=lambda x:x.id)
            
            G.cells_to_write=[]
            for job in G.JobList:
                job.printRoute()
            
            # list of cells to be written
            G.cells_to_write=[]
            # for every job in the JobList
            for worker in G.OperatorsList:
                worker.printRoute()
            # reset list of cells to be written
            del G.cells_to_write[:]
            del G.events_list[:]
            
            # print aliases
            try:
                sample_job=next(x for x in G.JobList)
                if sample_job.__class__.__name__ in ORDER_COMPONENT_TYPE_SET:
                    G.JobList.sort(key=lambda x:x.order.id)
            except:
                pass
            for j,job in enumerate(G.JobList):
                if job.schedule:
                    G.routeTraceSheet.write(number_of_events+2+j, 0, job.id)
                    G.routeTraceSheet.write(number_of_events+2+j, 1, job.alias)
            