from SimPy.Simulation import simulate, activate, initialize

from dream.simulation.Globals import G
from dream.simulation.Machine import Machine
from dream.simulation.Exit import Exit
from dream.simulation.Queue import Queue

from dream.simulation.Batch import Batch
from dream.simulation.BatchDecomposition import BatchDecomposition
from dream.simulation.BatchReassembly import BatchReassembly
from dream.simulation.BatchSource import BatchSource
from dream.simulation.LineClearance import LineClearance
import dream.simulation.ExcelHandler

# choose to output trace or not
G.trace='Yes'
# define the objects of the model
S=BatchSource('S','Source',mean=1.5, item=Batch,batchNumberOfUnits=100)
Q=Queue('Q','StartQueue',capacity=-1)
BD=BatchDecomposition('BC', 'BatchDecomposition', numberOfSubBatches=4, mean=1)
M1=Machine('M1','Machine1',mean=0.5)
Q1=LineClearance('Q1','Queue1',capacity=2)
M2=Machine('M2','Machine2',mean=4)
BRA=BatchReassembly('BRA', 'BatchReassembly', numberOfSubBatches=4, mean=0)
M3=Machine('M3','Machine3',mean=1)
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
# print trace
dream.simulation.ExcelHandler.outputTrace('Trace')  
# print the results 
print "the system produced", E.numOfExits, "parts"
print "the working ratio of", M1.objName, "is", (M1.totalWorkingTime/G.maxSimTime)*100
print "the blockage ratio of", M1.objName, 'is', (M1.totalBlockageTime/G.maxSimTime)*100
print "the waiting ratio of", M1.objName, 'is', (M1.totalWaitingTime/G.maxSimTime)*100
print "the working ratio of", M2.objName, "is", (M2.totalWorkingTime/G.maxSimTime)*100
print "the blockage ratio of", M2.objName, 'is', (M2.totalBlockageTime/G.maxSimTime)*100
print "the waiting ratio of", M2.objName, 'is', (M2.totalWaitingTime/G.maxSimTime)*100
print "the working ratio of", M3.objName, "is", (M3.totalWorkingTime/G.maxSimTime)*100
print "the blockage ratio of", M3.objName, 'is', (M3.totalBlockageTime/G.maxSimTime)*100
print "the waiting ratio of", M3.objName, 'is', (M3.totalWaitingTime/G.maxSimTime)*100
