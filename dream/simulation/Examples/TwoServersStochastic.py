from dream.simulation.imports import Machine, Source, Exit, Part, G, Repairman, Queue, Failure 
from dream.simulation.imports import simpy

G.env=simpy.Environment()   # define a simpy environment
                            # this is where all the simulation object 'live'

#define the objects of the model
R=Repairman('R1', 'Bob') 
S=Source('S1','Source', interarrivalTime={'distributionType':'Exp','mean':0.5}, entity='Dream.Part')
M1=Machine('M1','Machine1', processingTime={'distributionType':'Normal','mean':0.25,'stdev':0.1,'min':0.1,'max':1})
M2=Machine('M2','Machine2', processingTime={'distributionType':'Normal','mean':1.5,'stdev':0.3,'min':0.5,'max':5})
Q=Queue('Q1','Queue')
E=Exit('E1','Exit')  

#create failures
F1=Failure(victim=M1, distribution={'distributionType':'Fixed','MTTF':60,'MTTR':5}, repairman=R) 
F2=Failure(victim=M2, distribution={'distributionType':'Fixed','MTTF':40,'MTTR':10}, repairman=R)

G.ObjList=[S,M1,M2,E,Q]   #add all the objects in G.ObjList so that they can be easier accessed later
G.ObjectResourceList=[R]
G.ObjectInterruptionList=[F1,F2]     #add all the objects in G.ObjList so that they can be easier accessed later

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
    
    #initialize all the objects
    for object in G.ObjList:
        object.initialize()

    for objectInterruption in G.ObjectInterruptionList:
        objectInterruption.initialize()
        
    for objectResource in G.ObjectResourceList:
        objectResource.initialize()

    #activate all the objects
    for object in G.ObjList:
        G.env.process(object.run())

    for objectInterruption in G.ObjectInterruptionList:
        G.env.process(objectInterruption.run())
    
    G.env.run(until=G.maxSimTime)    #run the simulation

    #carry on the post processing operations for every object in the topology
    for object in G.ObjList:
        object.postProcessing()
    
    for objectResource in G.ObjectResourceList:
        objectResource.postProcessing()
               
#output data to excel for every object        
for object in G.ObjList:
    object.outputResultsXL()      
R.outputResultsXL()        

G.outputFile.save("output.xls")      

