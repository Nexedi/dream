from SimPy.Simulation import simulate, activate, initialize, infinity, now
from simulation.MachineJobShop import MachineJobShop
from simulation.QueueJobShop import QueueJobShop
from simulation.ExitJobShop import ExitJobShop
from simulation.Job import Job
from simulation.Globals import G
import simulation.ExcelHandler

G.trace="Yes"

from SimPy.Simulation import simulate, activate, initialize, infinity, now
from simulation.MachineJobShop import MachineJobShop
from simulation.QueueJobShop import QueueJobShop
from simulation.ExitJobShop import ExitJobShop
from simulation.Job import Job
from simulation.Globals import G
import simulation.Globals as Globals


#define the objects of the model
Q1=QueueJobShop('Q1','Queue1', capacity=infinity)
Q2=QueueJobShop('Q2','Queue2', capacity=infinity)
Q3=QueueJobShop('Q3','Queue3', capacity=infinity)
M1=MachineJobShop('M1','Machine1')
M2=MachineJobShop('M2','Machine2')
M3=MachineJobShop('M3','Machine3')
E=ExitJobShop('E','Exit')  

G.ObjList=[M1,M2,M3,Q1,Q2,Q3,E]   #add all the objects in G.ObjList so that they can be easier accessed later

#define the Jobs
J=Job('J1','Job1',route=[['Q1',0],['M1',1],['Q3',0],['M3',3],['Q2',0],['M2',2],['E',0]])
G.EntityList=[J]        #a list to hold all the jobs
   
initialize()                        #initialize the simulation (SimPy method)
        
#initialize all the objects    
for object in G.ObjList:
    object.initialize()
J.initialize()

#set the WIP
Globals.setWIP(G.EntityList)
    
#activate all the objects 
for object in G.ObjList:
    activate(object, object.run())

simulate(until=infinity)    #run the simulation until there are no more events

G.maxSimTime=E.timeLastEntityLeft   #calculate the maxSimTime as the time that the last Job left

#loop in the schedule to print the results
for record in J.schedule:
    #schedule holds ids of objects. The following loop will identify the name of the CoreObject with the given id
    name=None
    for obj in G.ObjList:
        if obj is record[0]:
            name=obj.objName
    print J.name, "got into", name, "at", record[1]
               
               
simulation.ExcelHandler.outputTrace('TRACE')

