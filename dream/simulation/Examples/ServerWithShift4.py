from dream.simulation.imports import Machine, Source, Exit, Part, ShiftScheduler 
from dream.simulation.Globals import runSimulation

#define the objects of the model 
S=Source('S1','Source',interarrivalTime={'distributionType':'Fixed','mean':0.5}, entity='Dream.Part')
M=Machine('M1','Machine', processingTime={'distributionType':'Fixed','mean':3})
E=Exit('E1','Exit')  

SS=ShiftScheduler(victim=M, shiftPattern=[[0,5],[10,15]],receiveBeforeEndThreshold=3) 

#define predecessors and successors for the objects    
S.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[S],successorList=[E])
E.defineRouting(predecessorList=[M])

def main():
    
    # add all the objects in a list
    objectList=[S,M,E,SS]  
    # set the length of the experiment  
    maxSimTime=20.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)
    
    #print the results
    print "the system produced", E.numOfExits, "parts"
    working_ratio = (M.totalWorkingTime/maxSimTime)*100
    off_shift_ratio=(M.totalOffShiftTime/maxSimTime)*100
    print "the total working ratio of the Machine is", working_ratio, "%"
    print "the total off-shift ratio of the Machine is", off_shift_ratio, "%"
    return {"parts": E.numOfExits,
          "working_ratio": working_ratio}

if __name__ == '__main__':
    main()