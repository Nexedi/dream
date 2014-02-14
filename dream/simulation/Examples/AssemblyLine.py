from dream.simulation.imports import Machine, Source, Exit, Part, Frame, Assembly, Failure, G 
from dream.simulation.imports import simulate, activate, initialize

#define the objects of the model
Frame.capacity=4 
Sp=Source('SP','Parts', mean=0.5, item=Part)
Sf=Source('SF','Frames', mean=2, item=Frame)
M=Machine('M','Machine', mean=0.25)
A=Assembly('A','Assembly', mean=2)
E=Exit('E1','Exit')  

F=Failure(victim=M, distributionType='Fixed', MTTF=60, MTTR=5)

G.ObjList=[Sp,Sf,M,A,E]   #add all the objects in G.ObjList so that they can be easier accessed later

G.ObjectInterruptionList=[F]     #add all the objects in G.ObjList so that they can be easier accessed later

#define predecessors and successors for the objects    
Sp.defineRouting([A])
Sf.defineRouting([A])
A.defineRouting([Sp,Sf],[M])
M.defineRouting([A],[E])
E.defineRouting([M])

initialize()                        #initialize the simulation (SimPy method)
    
for object in G.ObjList:
    object.initialize()
    
for objectInterruption in G.ObjectInterruptionList:
    objectInterruption.initialize()

#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

for objectInterruption in G.ObjectInterruptionList:
    activate(objectInterruption, objectInterruption.run())

G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
    
simulate(until=G.maxSimTime)    #run the simulation

#carry on the post processing operations for every object in the topology       
for object in G.ObjList:
    object.postProcessing()

#print the results
print "the system produced", E.numOfExits, "frames"
print "the working ratio of", A.objName,  "is", (A.totalWorkingTime/G.maxSimTime)*100, "%"


