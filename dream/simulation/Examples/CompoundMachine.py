from dream.simulation.imports import Machine, Exit, Queue, Globals, Part, ExcelHandler
from dream.simulation.imports import G 
from dream.simulation.Globals import runSimulation

# models the behaviour of the buffers in the compound machine
class InternalQueue(Queue):
    def canAccept(self, callerObject=None):
        # if the next machine holds a part return false
        if len(self.next[0].getActiveObjectQueue()):
            return False
        # else use the default Queue logic
        return Queue.canAccept(self, callerObject)

# models the behaviour of the processes in the compound machine
class InternalProcess(Machine):
    def canAccept(self, callerObject=None):
        # do not start processing unless there are enough parts 
        # (i.e. equal to the number of processes) in the compound machine
        if not self.countInternalParts()==len(G.InternalProcessList):
            return False
        return Machine.canAccept(self, callerObject)  

    # send signal to internalQueues for synchronization
    def getEntity(self):
        activeEntity=Machine.getEntity(self)
        for queue in G.InternalQueueList:
            station=queue.next[0]
            # do not send the signal if it is already triggered
            if not queue.canDispose.triggered:
                self.sendSignal(receiver=queue, signal=queue.canDispose, sender=station)
        return activeEntity

    # do not allow parts to proceed until all the processes are over
    def haveToDispose(self, callerObject=None):
        for object in G.InternalProcessList:
            # if there is one other machine processing return False
            if object.isProcessing:
                return False
        return Machine.haveToDispose(self, callerObject)  
    
    # check if all the machines got empty and send signal to QB
    def removeEntity(self,entity=None):
        # run the default method  
        activeEntity=Machine.removeEntity(self, entity)             
        # count the number of parts in the server. 
        # If it is empty have one internal queue to signal the queue before the compound object
        if not self.countInternalParts():
            self.sendSignal(receiver=QB, signal=QB.canDispose, sender=Q1)
        return activeEntity

    # returns the number of internal parts in the server
    def countInternalParts(self):
        totalParts=0
        for object in G.InternalProcessList+G.InternalQueueList:
            totalParts+=len(object.getActiveObjectQueue())
        return totalParts

QB=Queue('QB','QueueBefore', capacity=float("inf"))
Q1=InternalQueue('Q1','Q1', capacity=1)
M1=InternalProcess('M1','M1',processingTime={'Exp':{'mean':1}})
Q2=InternalQueue('Q2','Q2', capacity=1)
M2=InternalProcess('M2','M2',processingTime={'Exp':{'mean':1}})
Q3=InternalQueue('Q3','Q3', capacity=1)
M3=InternalProcess('M3','M3',processingTime={'Exp':{'mean':1}})
QA=Queue('QA','QueueAfter', capacity=float("inf"))
MA=Machine('MA','MachineAfter',processingTime={'Exp':{'mean':1}})
E=Exit('E','Exit')

QB.defineRouting(successorList=[Q1,Q2,Q3])
Q1.defineRouting(predecessorList=[QB],successorList=[M1])
Q2.defineRouting(predecessorList=[QB],successorList=[M2])
Q3.defineRouting(predecessorList=[QB],successorList=[M3])
M1.defineRouting(predecessorList=[Q1],successorList=[QA])
M2.defineRouting(predecessorList=[Q2],successorList=[QA])
M3.defineRouting(predecessorList=[Q3],successorList=[QA])
QA.defineRouting(predecessorList=[M1,M2,M3],successorList=[MA])
MA.defineRouting(predecessorList=[QA],successorList=[E])
E.defineRouting(predecessorList=[MA])

P1=Part('P1','P1',currentStation=QB)
P2=Part('P2','P2',currentStation=QB)
P3=Part('P3','P3',currentStation=QB)
P4=Part('P4','P4',currentStation=QB)
P5=Part('P5','P5',currentStation=QB)
P6=Part('P6','P6',currentStation=QB)

G.InternalQueueList=[Q1,Q2,Q3]
G.InternalProcessList=[M1,M2,M3]

def main(test=0):
    # call the runSimulation giving the objects and the length of the experiment
    runSimulation(objectList=[QB,Q1,M1,Q2,M2,Q3,M3,QA,E,P1,P2,P3,P4,P5,P6,MA], maxSimTime=float('inf'), trace='Yes')
    
    #output the trace of the simulation
    ExcelHandler.outputTrace('CompoundMachine')
    if test:
        return G.maxSimTime

if __name__ == '__main__':
    main()    

