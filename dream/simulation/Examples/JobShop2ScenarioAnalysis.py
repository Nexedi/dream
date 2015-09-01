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
route1=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{"Fixed":{"mean": "1"}}},
         {"stationIdsList": ["Q3"]},
         {"stationIdsList": ["M3"],"processingTime":{"Fixed":{"mean": "3"}}},
         {"stationIdsList": ["Q2"]},
         {"stationIdsList": ["M2"],"processingTime":{"Fixed":{"mean": "2"}}},
         {"stationIdsList": ["E"],}]
route2=[{"stationIdsList": ["Q1"]},
         {"stationIdsList": ["M1"],"processingTime":{"Fixed":{"mean": "4"}}},
         {"stationIdsList": ["E"],}]
#define the Jobs
J1=Job('J1','J1',route=route1, dueDate=8)
J2=Job('J2','J1',route=route2, dueDate=7)

def main(test=0):
    # loop through the scheduling rules
    for schedulingRule in ['EDD','RPC']:
        totalDelay=0
        # set the scheduline rule of Q1
        Q1.schedulingRule=schedulingRule
        # call the runSimulation giving the objects and the length of the experiment
        runSimulation(objectList=[M1,M2,M3,Q1,Q2,Q3,E,J1,J2], maxSimTime=float('inf'))
        # loop through the moulds and if they are delayed add to the total delay
        for job in [J1,J2]:
            totalDelay+=max([job.schedule[-1]['entranceTime']-job.dueDate,0])        
        if test:
            return totalDelay    
        # print the total delay
        print "running with", schedulingRule, "total delay is",totalDelay 

if __name__ == '__main__':
    main()
