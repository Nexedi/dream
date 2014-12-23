from dream.simulation.imports import Machine, Source, Exit, Part, Frame, Assembly, Failure
from dream.simulation.Globals import runSimulation

#define the objects of the model
Frame.capacity=4 
Sp=Source('SP','Parts', interArrivalTime={'Fixed':{'mean':0.5}}, entity='Dream.Part')
Sf=Source('SF','Frames', interArrivalTime={'Fixed':{'mean':2}}, entity='Dream.Frame')
M=Machine('M','Machine', processingTime={'Fixed':{'mean':0.25}})
A=Assembly('A','Assembly', processingTime={'Fixed':{'mean':2}})
E=Exit('E1','Exit')  

F=Failure(victim=M, distribution={'TTF':{'Fixed':{'mean':60.0}},'TTR':{'Fixed':{'mean':5.0}}})

#define predecessors and successors for the objects    
Sp.defineRouting([A])
Sf.defineRouting([A])
A.defineRouting([Sp,Sf],[M])
M.defineRouting([A],[E])
E.defineRouting([M])

def main(test=0):
    # add all the objects in a list
    objectList=[Sp,Sf,M,A,E,F]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)

    # calculate metrics
    working_ratio=(A.totalWorkingTime/maxSimTime)*100
    
    # return results for the test
    if test:
        return {"frames": E.numOfExits,
              "working_ratio": working_ratio}    
   
    # print the results
    print "the system produced", E.numOfExits, "frames"
    print "the working ratio of", A.objName,  "is", working_ratio, "%"


if __name__ == '__main__':
    main()

