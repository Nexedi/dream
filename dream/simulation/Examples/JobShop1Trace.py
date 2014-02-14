from dream.simulation.imports import MachineJobShop, QueueJobShop, ExitJobShop, Globals, Job, G, ExcelHandler 
from dream.simulation.imports import simulate, activate, initialize, infinity

G.trace="Yes"

#define the objects of the model
Q1=QueueJobShop('Q1','Queue1', capacity=infinity)
Q2=QueueJobShop('Q2','Queue2', capacity=infinity)
Q3=QueueJobShop('Q3','Queue3', capacity=infinity)
M1=MachineJobShop('M1','Machine1')
M2=MachineJobShop('M2','Machine2')
M3=MachineJobShop('M3','Machine3')
E=ExitJobShop('E','Exit')  

G.ObjList=[M1,M2,M3,Q1,Q2,Q3,E]   #add all the objects in G.ObjList so that they can be easier accessed later

#define the route of the Job in the system
J1Route=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{"distributionType": "Fixed","mean": "1"}},
         {"stationIdsList": ["Q3"]},
         {"stationIdsList": ["M3"],"processingTime":{"distributionType": "Fixed","mean": "3"}},
         {"stationIdsList": ["Q2"]},
         {"stationIdsList": ["M2"],"processingTime":{"distributionType": "Fixed","mean": "2"}},
         {"stationIdsList": ["E"],}]
#define the Jobs
J=Job('J1','Job1',route=J1Route)
G.EntityList=[J]        #a list to hold all the jobs
   
initialize()                        #initialize the simulation (SimPy method)
        
#initialize all the objects    
for object in G.ObjList:
    object.initialize()
J.initialize()

#set the WIP
Globals.setWIP(G.EntityList)
    
#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

simulate(until=infinity)    #run the simulation until there are no more events

G.maxSimTime=E.timeLastEntityLeft   #calculate the maxSimTime as the time that the last Job left

#loop in the schedule to print the results
for record in J.schedule:
    #schedule holds ids of objects. The following loop will identify the name of the CoreObject with the given id
    name=None
    for obj in G.ObjList:
        if obj is record[0]:
            name=obj.objName
    print J.name, "got into", name, "at", record[1]
               
               
ExcelHandler.outputTrace('TRACE')

