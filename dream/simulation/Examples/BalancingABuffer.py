from dream.simulation.imports import Machine, Queue, Exit, Part, EventGenerator  
from dream.simulation.Globals import runSimulation, G

# method to check if the buffer is starving and refill it
def balanceQueue(buffer, refillLevel=1):
    objectQueue=buffer.getActiveObjectQueue()
    numInQueue=len(objectQueue)
    print '-'*50
    print 'at time=', G.env.now
    if numInQueue==0:
        print 'buffer is starving, I will bring 5 parts'
        for i in range(refillLevel):
            partId='P'+str(G.numOfParts)
            partName='Part'+str(G.numOfParts)
            P=Part(partId, partName, currentStation=buffer)       
            objectQueue.append(P)
            G.numOfParts+=1
        # send a signal to the buffer that it can dispose an Entity
        buffer.canDispose.succeed(G.env.now)
    else:
        print 'buffer has', numInQueue, 'parts. No need to bring more'

#define the objects of the model 
Q=Queue('Q1','Queue', capacity=float('inf'))
M=Machine('M1','Machine', processingTime={'distributionType':'Fixed','mean':6})
E=Exit('E1','Exit')
EV=EventGenerator('EV', 'EntityCreator', start=0, stop=float('inf'), interval=20,method=balanceQueue, 
                  argumentDict={'buffer':Q, 'refillLevel':5})  

G.numOfParts=0
   
#define predecessors and successors for the objects    
Q.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[Q],successorList=[E])
E.defineRouting(predecessorList=[M])

def main():
    # add all the objects in a list
    objectList=[Q,M,E,EV]  
    # set the length of the experiment  
    maxSimTime=100.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)

    #print the results
    print '='*50
    print "the system produced", E.numOfExits, "parts"
    working_ratio = (M.totalWorkingTime/maxSimTime)*100
    print "the total working ratio of the Machine is", working_ratio, "%"
    return {"parts": E.numOfExits,
          "working_ratio": working_ratio}

if __name__ == '__main__':
    main()