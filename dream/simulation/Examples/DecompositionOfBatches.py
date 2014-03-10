from dream.simulation.imports import Machine, BatchSource, Exit, Batch, BatchDecomposition, Queue, G 
from dream.simulation.imports import simulate, activate, initialize

# define the objects of the model
S=BatchSource('S','Source',interarrivalTime={'distributionType':'Fixed','mean':0.5}, entity='Dream.Batch', batchNumberOfUnits=4)
Q=Queue('Q','StartQueue',capacity=100000)
BD=BatchDecomposition('BC', 'BatchDecomposition', numberOfSubBatches=4, processingTime={'distributionType':'Fixed','mean':1})
M=Machine('M','Machine',processingTime={'distributionType':'Fixed','mean':0.5})
E=Exit('E','Exit')
# add all the objects in the G.ObjList so that they can be easier accessed later
G.ObjList=[S,Q,BD,M,E]
# define the predecessors and successors for the objects
S.defineRouting([Q])
Q.defineRouting([S],[BD])
BD.defineRouting([Q],[M])
M.defineRouting([BD],[E])
E.defineRouting([M])

def main():
    # initialize the simulation (SimPy method)
    initialize()
    # initialize all the objects
    for object in G.ObjList:
        object.initialize()
    # activate all the objects
    for object in G.ObjList:
        activate(object,object.run())
    # set G.maxSimTime 1440.0 minutes (1 day)
    G.maxSimTime=1440.0
    # run the simulation
    simulate(until=G.maxSimTime)
    # carry on the post processing operations for every object in the topology
    for object in G.ObjList:
        object.postProcessing()
    # print the results 
    print "the system produced", E.numOfExits, "parts"
    working_ratio = (M.totalWorkingTime/G.maxSimTime)*100
    blockage_ratio = (M.totalBlockageTime/G.maxSimTime)*100
    waiting_ratio = (M.totalWaitingTime/G.maxSimTime)*100
    print "the working ratio of", M.objName, "is", working_ratio
    print "the blockage ratio of", M.objName, 'is', blockage_ratio
    print "the waiting ratio of", M.objName, 'is', waiting_ratio
    return {"parts": E.numOfExits,
           "working_ratio": working_ratio,
          "blockage_ratio": blockage_ratio,
          "waiting_ratio": waiting_ratio}
    
if __name__ == '__main__':
    main()
