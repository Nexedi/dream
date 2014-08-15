from dream.simulation.imports import Machine, Source, Exit, Part, Frame, Assembly, Failure, G 
from dream.simulation.imports import simpy

G.env=simpy.Environment()   # define a simpy environment
                            # this is where all the simulation object 'live'

#define the objects of the model
Frame.capacity=4 
Sp=Source('SP','Parts', interarrivalTime={'distributionType':'Fixed','mean':0.5}, entity='Dream.Part')
Sf=Source('SF','Frames', interarrivalTime={'distributionType':'Fixed','mean':2}, entity='Dream.Frame')
M=Machine('M','Machine', processingTime={'distributionType':'Fixed','mean':0.25})
A=Assembly('A','Assembly', processingTime={'distributionType':'Fixed','mean':2})
E=Exit('E1','Exit')  

F=Failure(victim=M, distribution={'distributionType':'Fixed','MTTF':60,'MTTR':5})

#add objects in lists so that they can be easier accessed later
G.ObjList=[Sp,Sf,M,A,E]   
G.ObjectInterruptionList=[F]

#define predecessors and successors for the objects    
Sp.defineRouting([A])
Sf.defineRouting([A])
A.defineRouting([Sp,Sf],[M])
M.defineRouting([A],[E])
E.defineRouting([M])

def main():
    
    #initialize all the objects
    for object in G.ObjList + G.ObjectInterruptionList:
        object.initialize()
    
    #activate all the objects
    for object in G.ObjList + G.ObjectInterruptionList:
        G.env.process(object.run())
    
    G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
        
    G.env.run(until=G.maxSimTime)    #run the simulation
    
    #carry on the post processing operations for every object in the topology       
    for object in G.ObjList:
        object.postProcessing()
    
    #print the results
    print "the system produced", E.numOfExits, "frames"
    working_ratio=(A.totalWorkingTime/G.maxSimTime)*100
    print "the working ratio of", A.objName,  "is", working_ratio, "%"
    return {"frames": E.numOfExits,
          "working_ratio": working_ratio}

if __name__ == '__main__':
    main()

