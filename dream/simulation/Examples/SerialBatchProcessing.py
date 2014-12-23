from dream.simulation.imports import Machine, BatchSource, Exit, Batch, BatchDecomposition, BatchReassembly, Queue
from dream.simulation.Globals import runSimulation

# define the objects of the model
S=BatchSource('S','Source',interArrivalTime={'Fixed':{'mean':1.5}}, entity='Dream.Batch', batchNumberOfUnits=100)
Q=Queue('Q','StartQueue',capacity=100000)
BD=BatchDecomposition('BC', 'BatchDecomposition', numberOfSubBatches=4, processingTime={'Fixed':{'mean':1}})
M1=Machine('M1','Machine1',processingTime={'Fixed':{'mean':0.5}})
Q1=Queue('Q1','Queue1',capacity=2)
M2=Machine('M2','Machine2',processingTime={'Fixed':{'mean':1}})
BRA=BatchReassembly('BRA', 'BatchReassembly', numberOfSubBatches=4, processingTime={'Fixed':{'mean':0}})
M3=Machine('M3','Machine3',processingTime={'Fixed':{'mean':1}})
E=Exit('E','Exit')
 
# define the predecessors and successors for the objects
S.defineRouting([Q])
Q.defineRouting([S],[BD])
BD.defineRouting([Q],[M1])
M1.defineRouting([BD],[Q1])
Q1.defineRouting([M1],[M2])
M2.defineRouting([Q1],[BRA])
BRA.defineRouting([M2],[M3])
M3.defineRouting([BRA],[E])
E.defineRouting([M3])

def main(test=0):
    # add all the objects in a list
    objectList=[S,Q,BD,M1,Q1,M2,BRA,M3,E]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)

    # calculate metrics
    working_ratio_M1 = (M1.totalWorkingTime/maxSimTime)*100
    blockage_ratio_M1 = (M1.totalBlockageTime/maxSimTime)*100
    waiting_ratio_M1 = (M1.totalWaitingTime/maxSimTime)*100    
    working_ratio_M2 = (M2.totalWorkingTime/maxSimTime)*100
    blockage_ratio_M2 = (M2.totalBlockageTime/maxSimTime)*100
    waiting_ratio_M2 = (M2.totalWaitingTime/maxSimTime)*100    
    working_ratio_M3 = (M3.totalWorkingTime/maxSimTime)*100
    blockage_ratio_M3 = (M3.totalBlockageTime/maxSimTime)*100
    waiting_ratio_M3 = (M3.totalWaitingTime/maxSimTime)*100

    # return results for the test
    if test:
        return {"batches": E.numOfExits,
               "working_ratio_M1": working_ratio_M1,
              "blockage_ratio_M1": blockage_ratio_M1,
              "waiting_ratio_M1": waiting_ratio_M1,
               "working_ratio_M2": working_ratio_M2,
              "blockage_ratio_M2": blockage_ratio_M2,
              "waiting_ratio_M2": waiting_ratio_M2,   
               "working_ratio_M3": working_ratio_M3,
              "blockage_ratio_M3": blockage_ratio_M3,
              "waiting_ratio_M3": waiting_ratio_M3,       
              }

    # print the results 
    print "the system produced", E.numOfExits, "batches"
    print "the working ratio of", M1.objName, "is", working_ratio_M1
    print "the blockage ratio of", M1.objName, 'is', blockage_ratio_M1
    print "the waiting ratio of", M1.objName, 'is', waiting_ratio_M1
    print "the working ratio of", M2.objName, "is", working_ratio_M2
    print "the blockage ratio of", M2.objName, 'is', blockage_ratio_M2
    print "the waiting ratio of", M2.objName, 'is', waiting_ratio_M2
    print "the working ratio of", M3.objName, "is", working_ratio_M3
    print "the blockage ratio of", M3.objName, 'is', blockage_ratio_M3
    print "the waiting ratio of", M3.objName, 'is', waiting_ratio_M3

if __name__ == '__main__':
    main()