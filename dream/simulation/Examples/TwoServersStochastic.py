from SimPy.Simulation import simulate, activate, initialize
from dream.simulation.Machine import Machine
from dream.simulation.Source import Source
from dream.simulation.Exit import Exit
from dream.simulation.Part import Part
from dream.simulation.Repairman import Repairman
from dream.simulation.Queue import Queue
from dream.simulation.Globals import G
from dream.simulation.Failure import Failure

#define the objects of the model
R=Repairman('R1', 'Bob') 
S=Source('S1','Source', mean=0.5, item=Part)
M1=Machine('M1','Machine1', distribution='Normal', mean=0.25, stdev=0.1, min=0.1, max=1)
Q=Queue('Q1','Queue')
M2=Machine('M2','Machine2', distribution='Normal', mean=1.5, stdev=0.3, min=0.5, max=5)
E=Exit('E1','Exit')  

#create failures
F1=Failure(victim=M1, distributionType='Fixed', MTTF=60, MTTR=5, repairman=R) 
F2=Failure(victim=M2, distributionType='Fixed', MTTF=40, MTTR=10, repairman=R)

G.ObjList=[S,M1,M2,E,Q]   #add all the objects in G.ObjList so that they can be easier accessed later

G.FailureList=[F1,F2]     #add all the objects in G.ObjList so that they can be easier accessed later

#define predecessors and successors for the objects    
S.defineRouting([M1])
M1.defineRouting([S],[Q])
Q.defineRouting([M1],[M2])
M2.defineRouting([Q],[E])
E.defineRouting([M2])

G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
G.numberOfReplications=10   #set 10 replications
G.confidenceLevel=0.99      #set the confidence level. 0.99=99%

#run the replications
for i in range(G.numberOfReplications):
    G.seed+=1       #increment the seed so that we get different random numbers in each run.
    
    initialize()                        #initialize the simulation (SimPy method)
        
    #initialize all the objects    
    R.initialize()
    for object in G.ObjList:
        object.initialize()

    for failure in G.FailureList:
        failure.initialize()
    
    #activate all the objects 
    for object in G.ObjList:
        activate(object, object.run())
        
    for failure in G.FailureList:
        activate(failure, failure.run())
    
    simulate(until=G.maxSimTime)    #run the simulation

    #carry on the post processing operations for every object in the topology       
    for object in G.ObjList:
        object.postProcessing()
    R.postProcessing()
               
#output data to excel for every object        
for object in G.ObjList:
    object.outputResultsXL()      
R.outputResultsXL()        

G.outputFile.save("output.xls")      

