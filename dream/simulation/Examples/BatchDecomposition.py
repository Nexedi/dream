from SimPy.Simulation import simulate, activate, initialize
from dream.simulation.Batch import Batch
from dream.simulation.BatchDecomposition import BatchDecomposition
from dream.simulation.BatchSource import BatchSource
from dream.simulation.Machine import Machine
from dream.simulation.Exit import Exit
from dream.simulation.Queue import Queue
from dream.simulation.Globals import G


# define the objects of the model
S=BatchSource('S','Source',mean=0.5, item=Batch,batchNumberOfUnits=4)
Q=Queue('Q','StartQueue',capacity=100000)
BD=BatchDecomposition('BC', 'BatchDecomposition', numberOfSubBatches=4, mean=1)
M=Machine('M','Machine',mean=0.5)
E=Exit('E','Exit')
# add all the objects in the G.ObjList so that they can be easier accessed later
G.ObjList=[S,Q,BD,M,E]
# define the predecessors and successors for the objects
S.defineRouting([Q])
Q.defineRouting([S],[BD])
BD.defineRouting([Q],[M])
M.defineRouting([BD],[E])
E.defineRouting([M])
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
print "the working ratio of", M.objName, "is", (M.totalWorkingTime/G.maxSimTime)*100
print "the blockage ratio of", M.objName, 'is', (M.totalBlockageTime/G.maxSimTime)*100
print "the waiting ratio of", M.objName, 'is', (M.totalWaitingTime/G.maxSimTime)*100