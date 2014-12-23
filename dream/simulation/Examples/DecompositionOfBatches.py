from dream.simulation.imports import Machine, BatchSource, Exit, Batch, BatchDecomposition, Queue
from dream.simulation.Globals import runSimulation

# define the objects of the model
S=BatchSource('S','Source',interArrivalTime={'Fixed':{'mean':0.5}}, entity='Dream.Batch', batchNumberOfUnits=4)
Q=Queue('Q','StartQueue',capacity=100000)
BD=BatchDecomposition('BC', 'BatchDecomposition', numberOfSubBatches=4, processingTime={'Fixed':{'mean':1}})
M=Machine('M','Machine',processingTime={'Fixed':{'mean':0.5}})
E=Exit('E','Exit')

# define the predecessors and successors for the objects
S.defineRouting([Q])
Q.defineRouting([S],[BD])
BD.defineRouting([Q],[M])
M.defineRouting([BD],[E])
E.defineRouting([M])

def main(test=0):

    # add all the objects in a list
    objectList=[S,Q,BD,M,E]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)
        
    # calculate metrics
    working_ratio = (M.totalWorkingTime/maxSimTime)*100
    blockage_ratio = (M.totalBlockageTime/maxSimTime)*100
    waiting_ratio = (M.totalWaitingTime/maxSimTime)*100
    
    # return results for the test
    if test:
        return {"subbatches": E.numOfExits,
               "working_ratio": working_ratio,
              "blockage_ratio": blockage_ratio,
              "waiting_ratio": waiting_ratio}
        
    # print the results 
    print "the system produced", E.numOfExits, "subbatches"        
    print "the working ratio of", M.objName, "is", working_ratio
    print "the blockage ratio of", M.objName, "is", blockage_ratio
    print "the waiting ratio of", M.objName, "is", waiting_ratio

    
if __name__ == '__main__':
    main()
