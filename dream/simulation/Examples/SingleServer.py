from dream.simulation.imports import Machine, Source, Exit, Part, G 
from dream.simulation.imports import simulate, activate, initialize

#define the objects of the model 
S=Source('S1','Source',distribution='Fixed', mean=0.5, item=Part)
M=Machine('M1','Machine', mean=0.25)
E=Exit('E1','Exit')  

G.ObjList=[S,M,E]   #add all the objects in G.ObjList so that they can be easier accessed later

#define predecessors and successors for the objects    
S.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[S],successorList=[E])
E.defineRouting(predecessorList=[M])
              
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
print "the total working ratio of the Machine is", (M.totalWorkingTime/G.maxSimTime)*100, "%"
