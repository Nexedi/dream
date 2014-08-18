from dream.simulation.imports import Machine, Source, Exit, Part, Repairman, Queue, Failure 
from dream.simulation.Globals import runSimulation

#define the objects of the model
R=Repairman('R1', 'Bob')
S=Source('S1','Source', interarrivalTime={'distributionType':'Fixed','mean':0.5}, entity='Dream.Part')
M1=Machine('M1','Machine1', processingTime={'distributionType':'Fixed','mean':0.25})
Q=Queue('Q1','Queue')
M2=Machine('M2','Machine2', processingTime={'distributionType':'Fixed','mean':1.5})
E=Exit('E1','Exit')  
#create failures
F1=Failure(victim=M1, distribution={'distributionType':'Fixed','MTTF':60,'MTTR':5}, repairman=R) 
F2=Failure(victim=M2, distribution={'distributionType':'Fixed','MTTF':40,'MTTR':10}, repairman=R)

#define predecessors and successors for the objects    
S.defineRouting([M1])
M1.defineRouting([S],[Q])
Q.defineRouting([M1],[M2])
M2.defineRouting([Q],[E])
E.defineRouting([M2])

def main():

    # add all the objects in a list
    objectList=[S,M1,M2,E,Q,R,F1,F2]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)

    #print the results
    print "the system produced", E.numOfExits, "parts"
    blockage_ratio = (M1.totalBlockageTime/maxSimTime)*100
    blockage_ratio = (M1.totalBlockageTime/maxSimTime)*100
    working_ratio = (R.totalWorkingTime/maxSimTime)*100
    waiting_ratio = (R.totalWaitingTime/maxSimTime)*100
    print "the blockage ratio of", M1.objName,  "is", blockage_ratio, "%"
    print "the working ratio of", R.objName,"is", working_ratio, "%"

    #create a graph object
    from dream.KnowledgeExtraction.Plots import Graphs
    graph=Graphs()
    #create the pie
    graph.Pie([working_ratio,waiting_ratio], "repairmanPie.jpg")

    return {"parts": E.numOfExits,
          "blockage_ratio": blockage_ratio,
          "working_ratio": working_ratio}
    

if __name__ == '__main__':
    main()




