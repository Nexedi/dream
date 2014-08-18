from dream.simulation.imports import MachineJobShop, QueueJobShop, ExitJobShop, Job
from dream.simulation.Globals import runSimulation

#define the objects of the model
Q1=QueueJobShop('Q1','Queue1', capacity=float("inf"), schedulingRule="EDD")
Q2=QueueJobShop('Q2','Queue2', capacity=float("inf"))
Q3=QueueJobShop('Q3','Queue3', capacity=float("inf"))
M1=MachineJobShop('M1','Machine1')
M2=MachineJobShop('M2','Machine2')
M3=MachineJobShop('M3','Machine3')
E=ExitJobShop('E','Exit')  

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

def main():
    # add all the objects in a list
    objectList=[M1,M2,M3,Q1,Q2,Q3,E,J1,J2,J3]  
    # set the length of the experiment  
    maxSimTime=float('inf')
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)
    
    #output the schedule of every job
    returnSchedule=[]     # dummy variable used just for returning values and testing
    for job in [J1,J2,J3]: 
        #loop in the schedule to print the results
        for record in job.schedule:
            #schedule holds ids of objects. The following loop will identify the name of the CoreObject with the given id
            name=None
            returnSchedule.append([record[0].objName,record[1]])
            print job.name, "got into", record[0].objName, "at", record[1]
        print "-"*30
    return returnSchedule
    
if __name__ == '__main__':
    main()