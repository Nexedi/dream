from SimPy.Simulation import simulate, activate, initialize, infinity, now
from simulation.Machine import Machine
from simulation.Queue import Queue
from simulation.Source import Source
from simulation.Exit import Exit
from simulation.Part import Part
from simulation.Globals import G

#the custom queue
class SelectiveQueue(Queue):
    def haveToDispose(self,callerObject=None):
        caller=callerObject
        if caller.id=='M1':
            return len(self.getActiveObjectQueue())>0
        self.M1=None
        if caller.id=='M2':
            for object in G.ObjList:
                if object.id=='M1':
                    self.M1=object
            return len(self.getActiveObjectQueue())>0 and (not (self.M1.canAccept()))

#the custom machine
class Milling(Machine):
    def getEntity(self):
        Machine.getEntity(self)         #call the parent method to get the entity
        part=self.getActiveObjectQueue()[0] #retrieve the obtained part
        part.machineId=self.id              #create an attribute to the obtained part and give it the value of the object's id

#the custom exit
class CountingExit(Exit):
    def getEntity(self):
        part=self.getGiverObjectQueue()[0]   #find the part to be obtained
        Exit.getEntity(self)                        #call the parent method to get the entity
        #check the attribute and update the counters accordingly
        if part.machineId=='M1':         
            G.NumM1+=1
        elif part.machineId=='M2':
            G.NumM2+=1
        
#define the objects of the model
S=Source('S','Source', mean=0.5, item=Part)
Q=SelectiveQueue('Q','Queue', capacity=infinity)
M1=Milling('M1','Milling1', mean=0.25, failureDistribution='Fixed', MTTF=60, MTTR=5)
M2=Milling('M2','Milling2', mean=0.25)
E=CountingExit('E1','Exit')  

G.ObjList=[S,Q,M1,M2,E]   #add all the objects in G.ObjList so that they can be easier accessed later

#create the global variables
G.NumM1=0
G.NumM2=0

#define predecessors and successors for the objects    
S.defineRouting([Q])
Q.defineRouting([S],[M1,M2])
M1.defineRouting([Q],[E])
M2.defineRouting([Q],[E])
E.defineRouting([M1,M2])

initialize()                        #initialize the simulation (SimPy method)
    
#initialize all the objects    
for object in G.ObjList:
    object.initialize()

#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

G.maxSimTime=1440.0     #set G.maxSimTime 1440.0 minutes (1 day)
    
simulate(until=G.maxSimTime)    #run the simulation

#carry on the post processing operations for every object in the topology       
for object in G.ObjList:
    object.postProcessing()

#print the results
print "the system produced", E.numOfExits, "parts"
print "the working ratio of", M1.objName,  "is", (M1.totalWorkingTime/G.maxSimTime)*100, "%"
print "the working ratio of", M2.objName,  "is", (M2.totalWorkingTime/G.maxSimTime)*100, "%"
print M1.objName, "produced", G.NumM1, "parts"
print M2.objName, "produced", G.NumM2, "parts"


