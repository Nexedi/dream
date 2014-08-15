from dream.simulation.imports import Machine, Source, Exit, Part, G, ShiftScheduler 
from dream.simulation.imports import simpy

G.env=simpy.Environment()   # define a simpy environment
                            # this is where all the simulation object 'live'

#define the objects of the model 
S=Source('S1','Source',interarrivalTime={'distributionType':'Fixed','mean':0.5}, entity='Dream.Part')
M=Machine('M1','Machine', processingTime={'distributionType':'Fixed','mean':1})
E=Exit('E1','Exit')  

G.ObjList=[S,M,E]   #add all the objects in a list so that they can be easier accessed later

#create the shift
SS=ShiftScheduler(victim=M, shiftPattern=[[0,5],[10,15]]) 
G.ObjectInterruptionList=[SS]     #add all the interruptions in a list so that they can be easier accessed later

#define predecessors and successors for the objects    
S.defineRouting(successorList=[M])
M.defineRouting(predecessorList=[S],successorList=[E])
E.defineRouting(predecessorList=[M])

def main():
    
    #initialize all the objects    
    for object in G.ObjList:
        object.initialize()
        
    for objectInterruption in G.ObjectInterruptionList:
        objectInterruption.initialize()
    
    #activate all the objects 
    for object in G.ObjList:
        G.env.process(object.run())   
        
    for objectInterruption in G.ObjectInterruptionList:
        G.env.process(objectInterruption.run())
  
    G.maxSimTime=20     #set G.maxSimTime 1440.0 minutes (1 day)
        
    G.env.run(G.maxSimTime)    #run the simulation
    
    #carry on the post processing operations for every object in the topology       
    for object in G.ObjList:
        object.postProcessing()
    
    #print the results
    print "the system produced", E.numOfExits, "parts"
    working_ratio = (M.totalWorkingTime/G.maxSimTime)*100
    off_shift_ratio=(M.totalOffShiftTime/G.maxSimTime)*100
    print "the total working ratio of the Machine is", working_ratio, "%"
    print "the total off-shift ratio of the Machine is", off_shift_ratio, "%"
    return {"parts": E.numOfExits,
          "working_ratio": working_ratio}

if __name__ == '__main__':
    main()