from dream.simulation.Source import Source
from dream.simulation.Queue import Queue
from dream.simulation.Machine import Machine
from dream.simulation.Exit import Exit
from dream.simulation.Part import Part
from dream.simulation.Globals import runSimulation
from dream.simulation.Globals import G
import random

#the custom machine
class Inspection(Machine):
    def selectReceiver(self, possibleReceivers=[]):
        # 80% continue, 20% go back to Q1
        # XXX Custom implementation hard-coding objects
        if random.uniform(0, 1) < 0.8:
            return Q2
        else:
            return Q1

#define the objects of the model
S=Source('S','Source', interArrivalTime={'Fixed':{'mean':0.5}}, entity='Dream.Part')
Q1=Queue('Q','Queue', capacity=float("inf"))
M1=Machine('M1','Milling1', processingTime={'Fixed':{'mean':1}})
QI=Queue('Q','Queue', capacity=float("inf"))
I=Inspection('I','Inspection', processingTime={'Fixed':{'mean':0.2}})
Q2=Queue('Q','Queue', capacity=float("inf"))
M2=Machine('M2','Milling2', processingTime={'Fixed':{'mean':1}})
E=Exit('E1','Exit')  

#create the global counter variables
G.NumM1=0
G.NumM2=0

#define predecessors and successors for the objects    
S.defineRouting([Q1])
Q1.defineRouting([S, I],[M1])
M1.defineRouting([Q1],[QI])
QI.defineRouting([M1],[I])
I.defineRouting([QI],[Q1, Q2])
Q2.defineRouting([I],[M2])
M2.defineRouting([Q2],[E])
E.defineRouting([M2])

def main(test=0):

    # add all the objects in a list
    objectList=[S,Q1,M1,QI,I,Q2,M2,E]  
    # set the length of the experiment  
    maxSimTime=1440.0
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList, maxSimTime)
    
    # calculate metrics
    working_ratio_M1=(M1.totalWorkingTime/maxSimTime)*100
    working_ratio_M2=(M2.totalWorkingTime/maxSimTime)*100    

    # return results for the test
    if test:
        return {"parts": E.numOfExits,
              "working_ratio_M1": working_ratio_M1,
              "working_ratio_M2": working_ratio_M2,
              "NumM1":G.NumM1,
              "NumM2":G.NumM2}

    #print the results
    print "the system produced", E.numOfExits, "parts"
    print "the working ratio of", M1.objName,  "is", working_ratio_M1, "%"
    print "the working ratio of", M2.objName,  "is", working_ratio_M2, "%"

if __name__ == '__main__':
    main()
