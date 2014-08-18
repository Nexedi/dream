from dream.simulation.imports import Machine, Source, Exit, Part, Queue, Failure 
from dream.simulation.Globals import runSimulation

#the custom queue
class SelectiveQueue(Queue):
    # override so that it first chooses M1 and then M2
    def selectReceiver(self,possibleReceivers=[]):
        if M1.canAccept():
            return M1
        elif M2.canAccept():
            return M2
        return None
        
#define the objects of the model
S=Source('S','Source', interarrivalTime={'distributionType':'Fixed','mean':0.5}, entity='Dream.Part')
Q=SelectiveQueue('Q','Queue', capacity=float("inf"))
M1=Machine('M1','Milling1', processingTime={'distributionType':'Fixed','mean':0.25})
M2=Machine('M2','Milling2', processingTime={'distributionType':'Fixed','mean':0.25})
E=Exit('E1','Exit')  
F=Failure(victim=M1, distribution={'distributionType':'Fixed','MTTF':60,'MTTR':5})

#define predecessors and successors for the objects    
S.defineRouting([Q])
Q.defineRouting([S],[M1,M2])
M1.defineRouting([Q],[E])
M2.defineRouting([Q],[E])
E.defineRouting([M1,M2])

def main():
    
    # add all the objects in a list
    objectList=[S,Q,M1,M2,E,F]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)
    
    #print the results
    print "the system produced", E.numOfExits, "parts"
    working_ratio_M1=(M1.totalWorkingTime/maxSimTime)*100
    working_ratio_M2=(M2.totalWorkingTime/maxSimTime)*100
    print "the working ratio of", M1.objName,  "is", working_ratio_M1, "%"
    print "the working ratio of", M2.objName,  "is", working_ratio_M2, "%"
    return {"parts": E.numOfExits,
          "working_ratio_M1": working_ratio_M1,
          "working_ratio_M2": working_ratio_M2}

if __name__ == '__main__':
    main()