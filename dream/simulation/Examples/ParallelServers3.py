from dream.simulation.imports import Machine, Source, Exit, Part, Queue, G, Globals, Failure 
from dream.simulation.imports import simulate, activate, initialize, infinity

#the custom queue
class SelectiveQueue(Queue):
    def haveToDispose(self,callerObject=None):
        caller=callerObject
        # if the caller is M1 then return true if there is an Entity to give
        if caller.id=='M1':
            return len(self.getActiveObjectQueue())>0
        # else return true only if M1 cannot accept the Entity
        if caller.id=='M2':
            # find M1
            M1=Globals.findObjectById('M1') # global method to obtain an object from the id
            return len(self.getActiveObjectQueue())>0 and (not (M1.canAccept()))

#the custom machine
class Milling(Machine):
    def getEntity(self):
        activeEntity=Machine.getEntity(self)        #call the parent method to get the entity
        part=self.getActiveObjectQueue()[0]         #retrieve the obtained part
        part.machineId=self.id                      #create an attribute to the obtained part and give it the value of the object's id
        return activeEntity                         #return the entity obtained

#the custom exit
class CountingExit(Exit):
    def getEntity(self):
        activeEntity=Exit.getEntity(self)                        #call the parent method to get the entity
        #check the attribute and update the counters accordingly
        if activeEntity.machineId=='M1':         
            G.NumM1+=1
        elif activeEntity.machineId=='M2':
            G.NumM2+=1
        return activeEntity             #return the entity obtained
        
#define the objects of the model
S=Source('S','Source', mean=0.5, item=Part)
Q=SelectiveQueue('Q','Queue', capacity=infinity)
M1=Milling('M1','Milling1', mean=0.25)
M2=Milling('M2','Milling2', mean=0.25)
E=CountingExit('E1','Exit')  

F=Failure(victim=M1, distributionType='Fixed', MTTF=60, MTTR=5)

G.ObjList=[S,Q,M1,M2,E]   #add all the objects in G.ObjList so that they can be easier accessed later

G.ObjectInterruptionList=[F]     #add all the objects in G.ObjList so that they can be easier accessed later

#create the global counter variables
G.NumM1=0
G.NumM2=0

#define predecessors and successors for the objects    
S.defineRouting([Q])
Q.defineRouting([S],[M1,M2])
M1.defineRouting([Q],[E])
M2.defineRouting([Q],[E])
E.defineRouting([M1,M2])

initialize()                        #initialize the simulation (SimPy method)
    
for object in G.ObjList:
    object.initialize()
    
for objectInterruption in G.ObjectInterruptionList:
    objectInterruption.initialize()

#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

for objectInterruption in G.ObjectInterruptionList:
    activate(objectInterruption, objectInterruption.run())

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


