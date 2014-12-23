from dream.simulation.imports import Machine, Queue, Exit, Part, EventGenerator, ExcelHandler  
from dream.simulation.Globals import runSimulation, G


# method that is to be invoked by the generator. 
# it changes the predecessor of the Machine
def changeMachinePredecessor(machine, possiblePredecessors):
    # if the machine has no predecessors (at the start of the simulation)
    # pick the first of the list
    if not len(machine.previous):
        machine.previous.append(possiblePredecessors[0])
    # else loop through the possible predecessors and if one is not the current
    # set this as predecessor and break
    else:
        for buffer in possiblePredecessors:
            if not buffer==machine.previous[0]:
                machine.previous[0]=buffer  
                break  
    # if canDispose is not triggered in the predecessor send it
    if not machine.previous[0].canDispose.triggered:
        # a succeed function on an event must always take attributes the transmitter and the time of the event
        succeedTuple=(machine, G.env.now)
        machine.previous[0].canDispose.succeed(succeedTuple)
    print G.env.now, 'from now on the machine will take from', machine.previous[0].id
        
#define the objects of the model 
Q1=Queue('Q1','Queue1', capacity=float('inf'))
Q2=Queue('Q2','Queue2', capacity=float('inf'))
M=Machine('M1','Machine', processingTime={'Fixed':{'mean':3}})
E=Exit('E1','Exit')  
P1=Part('P1', 'Part1', currentStation=Q1)
entityList=[]
for i in range(5):      # create the WIP in a loop
    Q1PartId='Q1_P'+str(i)
    Q1PartName='Q1_Part'+str(i)
    PQ1=Part(Q1PartId, Q1PartName, currentStation=Q1)
    entityList.append(PQ1)
    Q2PartId='Q2_P'+str(i)
    Q2PartName='Q2_Part'+str(i)
    PQ2=Part(Q2PartId, Q2PartName, currentStation=Q2)
    entityList.append(PQ2)
    
#define predecessors and successors for the objects    
Q1.defineRouting(successorList=[M])
Q2.defineRouting(successorList=[M])
M.defineRouting(successorList=[E])
E.defineRouting(predecessorList=[M])

EV=EventGenerator('EV', 'PredecessorChanger', start=0, stop=50, interval=10,method=changeMachinePredecessor, 
                  argumentDict={'machine':M, 'possiblePredecessors':[Q1,Q2]})  

def main(test=0):
    # add all the objects in a list
    objectList=[Q1,Q2,M,E,EV]+entityList  
    # set the length of the experiment  
    maxSimTime=float('inf')
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime, trace='Yes')
    
    # calculate metrics
    working_ratio = (M.totalWorkingTime/E.timeLastEntityLeft)*100

    # return results for the test
    if test:
        return {"parts": E.numOfExits,
            "simulationTime":E.timeLastEntityLeft,
            "working_ratio": working_ratio}
    #print the results
    print '='*50
    print "the system produced", E.numOfExits, "parts in", E.timeLastEntityLeft, "minutes"
    print "the total working ratio of the Machine is", working_ratio, "%"
    ExcelHandler.outputTrace('ChangingPredecessors')

if __name__ == '__main__':
    main()