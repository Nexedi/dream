from dream.simulation.imports import Machine, Queue, Exit, Part, ExcelHandler  
from dream.simulation.Globals import runSimulation, G

#define the objects of the model 
Q=Queue('Q1','Queue', capacity=1)
M=Machine('M1','Machine', processingTime={'Fixed':{'mean':0.25}})
E=Exit('E1','Exit')  
P1=Part('P1', 'Part1', currentStation=Q)
P2=Part('P2', 'Part2', currentStation=M)

#define predecessors and successors for the objects    
Q.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[Q],successorList=[E])
E.defineRouting(predecessorList=[M])

def main(test=0):
    # add all the objects in a list
    objectList=[Q,M,E,P1,P2]  
    # set the length of the experiment  
    maxSimTime=float('inf')
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime, trace='Yes')

    # calculate metrics
    working_ratio = (M.totalWorkingTime/G.maxSimTime)*100

    # return results for the test
    if test:
        return {"parts": E.numOfExits,
        "simulationTime":E.timeLastEntityLeft,
      "working_ratio": working_ratio}

    #print the results
    print "the system produced", E.numOfExits, "parts in", E.timeLastEntityLeft, "minutes"
    print "the total working ratio of the Machine is", working_ratio, "%"
    ExcelHandler.outputTrace('Wip2')
    
if __name__ == '__main__':
    main()