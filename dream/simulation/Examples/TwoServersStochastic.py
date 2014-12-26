from dream.simulation.imports import Machine, Source, Exit, Part, Repairman, Queue, Failure 
from dream.simulation.Globals import runSimulation

#define the objects of the model
R=Repairman('R1', 'Bob') 
S=Source('S1','Source', interarrivalTime={'Exp':{'mean':0.5}}, entity='Dream.Part')
M1=Machine('M1','Machine1', processingTime={'Normal':{'mean':0.25,'stdev':0.1,'min':0.1,'max':1}})
M2=Machine('M2','Machine2', processingTime={'Normal':{'mean':1.5,'stdev':0.3,'min':0.5,'max':5}})
Q=Queue('Q1','Queue')
E=Exit('E1','Exit')  
#create failures
F1=Failure(victim=M1, distribution={'TTF':{'Fixed':{'mean':60.0}},'TTR':{'Fixed':{'mean':5.0}}}, repairman=R) 
F2=Failure(victim=M2, distribution={'TTF':{'Fixed':{'mean':40.0}},'TTR':{'Fixed':{'mean':10.0}}}, repairman=R)

#define predecessors and successors for the objects    
S.defineRouting([M1])
M1.defineRouting([S],[Q])
Q.defineRouting([M1],[M2])
M2.defineRouting([Q],[E])
E.defineRouting([M2])

def main():
    
    # add all the objects in a list
    objectList=[S,M1,M2,E,Q,R,F1,F2]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime, numberOfReplications=10, seed=1)
        
    print 'The exit of each replication is:'
    print E.Exits
    
    # calculate confidence interval using the Knowledge Extraction tool
    from dream.KnowledgeExtraction.ConfidenceIntervals import Intervals
    from dream.KnowledgeExtraction.StatisticalMeasures import BasicStatisticalMeasures
    BSM=BasicStatisticalMeasures()
    lb, ub = Intervals().ConfidIntervals(E.Exits, 0.95)
    print 'the 95% confidence interval for the throughput is:'
    print 'lower bound:', lb 
    print 'mean:', BSM.mean(E.Exits)
    print 'upper bound:', ub       

if __name__ == '__main__':
    main()