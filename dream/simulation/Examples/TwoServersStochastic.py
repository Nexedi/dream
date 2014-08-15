from dream.simulation.imports import Machine, Source, Exit, Part, G, Repairman, Queue, Failure 
from dream.simulation.imports import simpy

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

#add objects in lists so that they can be easier accessed later
G.ObjList=[S,M1,M2,E,Q]   
G.ObjectResourceList=[R]
G.ObjectInterruptionList=[F1,F2]     

#define predecessors and successors for the objects    
S.defineRouting([M1])
M1.defineRouting([S],[Q])
Q.defineRouting([M1],[M2])
M2.defineRouting([Q],[E])
E.defineRouting([M2])

G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
G.numberOfReplications=10   #set 10 replications
G.confidenceLevel=0.99      #set the confidence level. 0.99=99%

def main():
    throughputList=[]   # a list to hold the throughput of each replication

    #run the replications
    for i in range(G.numberOfReplications):
        G.seed+=1       #increment the seed so that we get different random numbers in each run.
        
        G.env=simpy.Environment()   # define a simpy environment
                                    # this is where all the simulation object 'live'
        
        #initialize all the objects
        for object in G.ObjList + G.ObjectInterruptionList + G.ObjectResourceList:
            object.initialize()
    
        #activate all the objects
        for object in G.ObjList + G.ObjectInterruptionList:
            G.env.process(object.run())
        
        G.env.run(until=G.maxSimTime)    #run the simulation
    
        #carry on the post processing operations for every object in the topology
        for object in G.ObjList + G.ObjectResourceList:
            object.postProcessing()

        # append the number of exits in the throughputList
        throughputList.append(E.numOfExits)
        
    print 'The exit of each replication is:'
    print throughputList
    
    # calculate confidence interval using the Knowledge Extraction tool
    from dream.KnowledgeExtraction.ConfidenceIntervals import Intervals
    from dream.KnowledgeExtraction.StatisticalMeasures import BasicStatisticalMeasures
    BSM=BasicStatisticalMeasures()
    lb, ub = Intervals().ConfidIntervals(throughputList, 0.95)
    print 'the 95% confidence interval for the throughput is:'
    print 'lower bound:', lb 
    print 'mean:', BSM.mean(throughputList)
    print 'upper bound:', ub       

if __name__ == '__main__':
    main()