from dream.simulation.imports import Machine, Source, Exit, Batch, BatchDecomposition,\
                            BatchSource, BatchReassembly, Queue, LineClearance, ExcelHandler, G, ExcelHandler 
from dream.simulation.imports import simpy

G.env=simpy.Environment()   # define a simpy environment
                            # this is where all the simulation object 'live'

# choose to output trace or not
G.trace='Yes'
# define the objects of the model
S=BatchSource('S','Source',interarrivalTime={'distributionType':'Fixed','mean':1.5}, entity='Dream.Batch', batchNumberOfUnits=100)
Q=Queue('Q','StartQueue',capacity=100000)
BD=BatchDecomposition('BC', 'BatchDecomposition', numberOfSubBatches=4, processingTime={'distributionType':'Fixed','mean':1})
M1=Machine('M1','Machine1',processingTime={'distributionType':'Fixed','mean':0.5})
Q1=LineClearance('Q1','Queue1',capacity=2)
M2=Machine('M2','Machine2',processingTime={'distributionType':'Fixed','mean':4})
BRA=BatchReassembly('BRA', 'BatchReassembly', numberOfSubBatches=4, processingTime={'distributionType':'Fixed','mean':0})
M3=Machine('M3','Machine3',processingTime={'distributionType':'Fixed','mean':1})
E=Exit('E','Exit')
# add all the objects in the G.ObjList so that they can be easier accessed later
G.ObjList=[S,Q,BD,M1,Q1,M2,BRA,M3,E]
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

def main():

    # initialize all the objects
    for object in G.ObjList:
        object.initialize()
    
    #activate all the objects 
    for object in G.ObjList:
        G.env.process(object.run()) 
    
    # set G.maxSimTime 1440.0 minutes (1 day)
    G.maxSimTime=1440.0
    # run the simulation
    G.env.run(until=G.maxSimTime)
    # carry on the post processing operations for every object in the topology
    for object in G.ObjList:
        object.postProcessing()
    # print the results 
    print "the system produced", E.numOfExits, "batches"
    working_ratio_M1 = (M1.totalWorkingTime/G.maxSimTime)*100
    blockage_ratio_M1 = (M1.totalBlockageTime/G.maxSimTime)*100
    waiting_ratio_M1 = (M1.totalWaitingTime/G.maxSimTime)*100
    print "the working ratio of", M1.objName, "is", working_ratio_M1
    print "the blockage ratio of", M1.objName, 'is', blockage_ratio_M1
    print "the waiting ratio of", M1.objName, 'is', waiting_ratio_M1
    working_ratio_M2 = (M2.totalWorkingTime/G.maxSimTime)*100
    blockage_ratio_M2 = (M2.totalBlockageTime/G.maxSimTime)*100
    waiting_ratio_M2 = (M2.totalWaitingTime/G.maxSimTime)*100
    print "the working ratio of", M2.objName, "is", working_ratio_M2
    print "the blockage ratio of", M2.objName, 'is', blockage_ratio_M2
    print "the waiting ratio of", M2.objName, 'is', waiting_ratio_M2
    working_ratio_M3 = (M3.totalWorkingTime/G.maxSimTime)*100
    blockage_ratio_M3 = (M3.totalBlockageTime/G.maxSimTime)*100
    waiting_ratio_M3 = (M3.totalWaitingTime/G.maxSimTime)*100
    print "the working ratio of", M3.objName, "is", working_ratio_M3
    print "the blockage ratio of", M3.objName, 'is', blockage_ratio_M3
    print "the waiting ratio of", M3.objName, 'is', waiting_ratio_M3

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
    
if __name__ == '__main__':
    main()
