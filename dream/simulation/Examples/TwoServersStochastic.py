from SimPy.Simulation import simulate, activate, initialize
from simulation.Machine import Machine
from simulation.Source import Source
from simulation.Exit import Exit
from simulation.Part import Part
from simulation.Repairman import Repairman
from simulation.Queue import Queue
from simulation.Globals import G

#define the objects of the model
R=Repairman('R1', 'Bob') 
S=Source('S1','Source', mean=0.5, item=Part)
M1=Machine('M1','Machine1', distribution='Normal', mean=0.25, stdev=0.1, min=0.1, max=1, failureDistribution='Fixed', MTTF=60, MTTR=5, repairman=R)
Q=Queue('Q1','Queue')
M2=Machine('M2','Machine2', distribution='Normal', mean=1.5, stdev=0.3, min=0.5, max=5, failureDistribution='Fixed', MTTF=40, MTTR=10,repairman=R)
E=Exit('E1','Exit')  

G.ObjList=[S,M1,M2,E,Q]   #add all the objects in G.ObjList so that they can be easier accessed later

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
    
    #activate all the objects 
    for object in G.ObjList:
        activate(object, object.run())
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

