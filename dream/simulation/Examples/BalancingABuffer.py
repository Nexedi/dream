from dream.simulation.imports import Machine, Queue, Exit, Part, EventGenerator  
from dream.simulation.Globals import runSimulation, setWIP, G

# method to check if the buffer is starving and refill it
def balanceQueue(buffer, refillLevel=1):
    # get the internal queue of the buffer
    objectQueue=buffer.getActiveObjectQueue()
    numInQueue=len(objectQueue)
    print '-'*50
    print 'at time=', G.env.now
    # check if the buffer is empty and if yes fill it with 5 parts
    if numInQueue==0:
        print 'buffer is starving, I will bring 5 parts'
        for i in range(refillLevel):
            # calculate the id and name of the new part
            partId='P'+str(G.numOfParts)
            partName='Part'+str(G.numOfParts)
            # create the Part
            P=Part(partId, partName, currentStation=buffer)       
            # set the part as WIP
            setWIP([P])
            G.numOfParts+=1
    # else do nothing        
    else:
        print 'buffer has', numInQueue, 'parts. No need to bring more'

#define the objects of the model 
Q=Queue('Q1','Queue', capacity=float('inf'))
M=Machine('M1','Machine', processingTime={'Fixed':{'mean':6}})
E=Exit('E1','Exit')
EV=EventGenerator('EV', 'EntityCreator', start=0, stop=float('inf'), interval=20,method=balanceQueue, 
                  argumentDict={'buffer':Q, 'refillLevel':5})  

# counter used in order to give parts meaningful ids (e.g P1, P2...) and names (e.g. Part1, Part2...)
G.numOfParts=0
   
#define predecessors and successors for the objects    
Q.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[Q],successorList=[E])
E.defineRouting(predecessorList=[M])

def main(test=0):
    # add all the objects in a list
    objectList=[Q,M,E,EV]  
    # set the length of the experiment  
    maxSimTime=100.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)

    # calculate metrics
    working_ratio = (M.totalWorkingTime/maxSimTime)*100

    # return results for the test
    if test:
        return {"parts": E.numOfExits,
              "working_ratio": working_ratio}

    #print the results
    print '='*50
    print "the system produced", E.numOfExits, "parts"
    print "the total working ratio of the Machine is", working_ratio, "%"


if __name__ == '__main__':
    main()