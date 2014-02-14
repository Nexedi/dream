from SimPy.Simulation import simulate, activate, initialize, infinity, now
from dream.simulation.MachineJobShop import MachineJobShop
from dream.simulation.QueueJobShop import QueueJobShop
from dream.simulation.ExitJobShop import ExitJobShop
from dream.simulation.Job import Job
from dream.simulation.Globals import G
import dream.simulation.Globals as Globals

#define the objects of the model
Q1=QueueJobShop('Q1','Queue1', capacity=infinity, schedulingRule="LPT")
Q2=QueueJobShop('Q2','Queue2', capacity=infinity)
Q3=QueueJobShop('Q3','Queue3', capacity=infinity)
M1=MachineJobShop('M1','Machine1')
M2=MachineJobShop('M2','Machine2')
M3=MachineJobShop('M3','Machine3')
E=ExitJobShop('E','Exit')  

G.ObjList=[M1,M2,M3,Q1,Q2,Q3,E]   #add all the objects in G.ObjList so that they can be easier accessed later

#define predecessors and successors for the objects    
Q1.defineRouting(successorList=[M1])
Q2.defineRouting(successorList=[M2])
Q3.defineRouting(successorList=[M3])
M1.defineRouting(predecessorList=[Q1])
M2.defineRouting(predecessorList=[Q2])
M3.defineRouting(predecessorList=[Q3])

#define the routes of the Jobs in the system
J1Route=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{"distributionType": "Fixed","mean": "1"}},
         {"stationIdsList": ["Q3"]},
         {"stationIdsList": ["M3"],"processingTime":{"distributionType": "Fixed","mean": "3"}},
         {"stationIdsList": ["Q2"]},
         {"stationIdsList": ["M2"],"processingTime":{"distributionType": "Fixed","mean": "2"}},
         {"stationIdsList": ["E"],}]
J2Route=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{"distributionType": "Fixed","mean": "2"}},
         {"stationIdsList": ["Q2"]},
         {"stationIdsList": ["M2"],"processingTime":{"distributionType": "Fixed","mean": "4"}},
         {"stationIdsList": ["Q3"]},
         {"stationIdsList": ["M3"],"processingTime":{"distributionType": "Fixed","mean": "6"}},
         {"stationIdsList": ["E"],}]
J3Route=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{"distributionType": "Fixed","mean": "10"}},
         {"stationIdsList": ["Q3"]},
         {"stationIdsList": ["M3"],"processingTime":{"distributionType": "Fixed","mean": "3"}},
         {"stationIdsList": ["E"],}]

#define the Jobs
J1=Job('J1','Job1',route=J1Route, priority=1, dueDate=100)
J2=Job('J2','Job2',route=J2Route, priority=1, dueDate=90)
J3=Job('J3','Job3',route=J3Route, priority=0, dueDate=110)
G.JobList=[J1,J2,J3]        #a list to hold all the jobs

G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
    
initialize()            #initialize the simulation (SimPy method)
        
#initialize all the objects    
for object in G.ObjList:
    object.initialize()

#initialize all the jobs
for job in G.JobList: 
    job.initialize()

#set the WIP for all the jobs
Globals.setWIP(G.JobList)
    
#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

simulate(until=G.maxSimTime)    #run the simulation

#output the schedule of every job
for job in G.JobList: 
    #loop in the schedule to print the results
    for record in job.schedule:
        #schedule holds ids of objects. The following loop will identify the name of the CoreObject with the given id
        name=None
        for obj in G.ObjList:
            if obj is record[0]:
                name=obj.objName
        print job.name, "got into", name, "at", record[1]
    print "-"*30
