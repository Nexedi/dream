from SimPy.Simulation import simulate, activate, initialize, infinity
from dream.simulation.Machine import Machine
from dream.simulation.Queue import Queue
from dream.simulation.Source import Source
from dream.simulation.Exit import Exit
from dream.simulation.Part import Part
from dream.simulation.Globals import G

#define the objects of the model
S=Source('S','Source', mean=0.5, item=Part)
Q=Queue('Q','Queue', capacity=infinity)
M1=Machine('M1','Milling1', mean=0.25, failureDistribution='Fixed', MTTF=60, MTTR=5)
M2=Machine('M2','Milling2', mean=0.25)
E=Exit('E1','Exit')  

G.ObjList=[S,Q,M1,M2,E]   #add all the objects in G.ObjList so that they can be easier accessed later

#define predecessors and successors for the objects    
S.defineRouting([Q])
Q.defineRouting([S],[M1,M2])
M1.defineRouting([Q],[E])
M2.defineRouting([Q],[E])
E.defineRouting([M1,M2])

initialize()                        #initialize the simulation (SimPy method)
    
#initialize all the objects    
for object in G.ObjList:
    object.initialize()

#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
    
simulate(until=G.maxSimTime)    #run the simulation

#carry on the post processing operations for every object in the topology       
for object in G.ObjList:
    object.postProcessing()

#print the results
print "the system produced", E.numOfExits, "parts"
print "the working ratio of", M1.objName,  "is", (M1.totalWorkingTime/G.maxSimTime)*100, "%"
print "the working ratio of", M2.objName,  "is", (M2.totalWorkingTime/G.maxSimTime)*100, "%"


