from dream.simulation.imports import MachineJobShop, QueueJobShop, ExitJobShop, Job, ExcelHandler
from dream.simulation.Globals import runSimulation

#define the objects of the model
Q1=QueueJobShop('Q1','Queue1', capacity=float("inf"))
Q2=QueueJobShop('Q2','Queue2', capacity=float("inf"))
Q3=QueueJobShop('Q3','Queue3', capacity=float("inf"))
M1=MachineJobShop('M1','Machine1')
M2=MachineJobShop('M2','Machine2')
M3=MachineJobShop('M3','Machine3')
E=ExitJobShop('E','Exit')  

#define the route of the Job in the system
route=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{'Fixed':{'mean':1}}},
         {"stationIdsList": ["Q3"]},
         {"stationIdsList": ["M3"],"processingTime":{'Fixed':{'mean':3}}},
         {"stationIdsList": ["Q2"]},
         {"stationIdsList": ["M2"],"processingTime":{'Fixed':{'mean':2}}},
         {"stationIdsList": ["E"],}]
#define the Jobs
J=Job('J1','Job1',route=route)
   
def main():
    # add all the objects in a list
    objectList=[M1,M2,M3,Q1,Q2,Q3,E,J]  
    # set the length of the experiment  
    maxSimTime=float('inf')
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime, trace='Yes')
      
    #loop in the schedule to print the results
    schedule=[]
    for record in J.schedule:
        schedule.append([record["station"].objName,record["entranceTime"]])
        print J.name, "got into", record["station"].objName, "at", record["entranceTime"] 
    ExcelHandler.outputTrace('TRACE')
    return schedule

if __name__ == '__main__':
    main()      
       
               


