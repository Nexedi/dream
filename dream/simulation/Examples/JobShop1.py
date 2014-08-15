from dream.simulation.imports import MachineJobShop, QueueJobShop, ExitJobShop, Globals, Job, G 
from dream.simulation.imports import simpy

G.env=simpy.Environment()   # define a simpy environment
                            # this is where all the simulation object 'live'

#define the objects of the model
Q1=QueueJobShop('Q1','Queue1', capacity=float("inf"))
Q2=QueueJobShop('Q2','Queue2', capacity=float("inf"))
Q3=QueueJobShop('Q3','Queue3', capacity=float("inf"))
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
G.EntityList=[J]        #a list to hold all the entities

def main():
    #initialize all the objects    
    for object in G.ObjList + G.EntityList:
        object.initialize()
    
    #activate all the objects 
    for object in G.ObjList:
        G.env.process(object.run())   
           
    #set the WIP
    Globals.setWIP(G.EntityList)
    
    G.env.run(until=float("inf"))    #run the simulation until there are no more events
    
    G.maxSimTime=E.timeLastEntityLeft   #calculate the maxSimTime as the time that the last Job left
    
    #carry on the post processing operations for every object in the topology       
    for object in G.ObjList:
        object.postProcessing()
    
    #loop in the schedule to print the results
    returnSchedule=[]     # dummy variable used just for returning values and testing
    for record in J.schedule:
        returnSchedule.append([record[0].objName,record[1]])
        print J.name, "got into", record[0].objName, "at", record[1]
    return returnSchedule 

if __name__ == '__main__':
    main()              