from dream.simulation.imports import Machine, Source, Exit, Part, Queue, NonStarvingEntry
from dream.simulation.Globals import runSimulation

#define the objects of the model
NS=NonStarvingEntry('NS1','Entry',entityData={'_class':'Dream.Part'})
M1=Machine('M1','Machine1', processingTime={'Exp':{'mean':1}})
Q2=Queue('Q2','Queue2')
M2=Machine('M2','Machine2', processingTime={'Exp':{'mean':3}})
Q3=Queue('Q3','Queue3')
M3=Machine('M3','Machine3', processingTime={'Exp':{'mean':5}})
E=Exit('E1','Exit')  


#define predecessors and successors for the objects    
NS.defineRouting(successorList=[M1])
M1.defineRouting(predecessorList=[NS],successorList=[Q2])
Q2.defineRouting(predecessorList=[M1],successorList=[M2])
M2.defineRouting(predecessorList=[Q2],successorList=[Q3])
Q3.defineRouting(predecessorList=[M2],successorList=[M3])
M3.defineRouting(predecessorList=[Q3],successorList=[E])
E.defineRouting(predecessorList=[M3])

def main(test=0):
    # add all the objects in a list
    objectList=[NS,M1,M2,M3,Q2,Q3,E]  
    # set the length of the experiment  
    maxSimTime=480
    
    solutionList=[]
    
    for i in range(1,10):
        Q2.capacity=i
        Q3.capacity=10-i
        # call the runSimulation giving the objects and the length of the experiment
        runSimulation(objectList, maxSimTime,numberOfReplications=10)
    
        # return results for the test
        if test:
            return {"parts": E.numOfExits}
       
        solutionList.append({
                             "Q2":Q2.capacity,
                             "Q3":Q3.capacity,
                             "throughput":sum(E.Exits)/float(len(E.Exits))
                             }
                            )
        E.Exits=[]
    solutionList.sort(key=lambda x: x.get("throughput",0), reverse=True)
    print "the best allocation is for Q2",solutionList[0]['Q2'],"units and Q3",solutionList[0]['Q2'],\
            "units, with a predicted throughput of",solutionList[0]['throughput']

if __name__ == '__main__':
    main()
