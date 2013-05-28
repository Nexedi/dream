'''
Created on 7 May 2013

@author: George
'''
'''
main script. Reads data from JSON, generates and runs the simulation and prints the results to excel
'''

from SimPy.Simulation import *
from Source import Source
from Globals import G
from Machine import Machine
from Exit import Exit
from Queue import Queue
from QueueLIFO import QueueLIFO
from Repairman import Repairman
from Part import Part
from Frame import Frame
from Assembly import Assembly
from Dismantle import Dismantle
from Conveyer import Conveyer
import xlwt
import xlrd
import time
import numpy as np
import json
from random import Random
import sys

#reads general simulation inputs
def readGeneralInput():
    general=G.JSONData['general']
    G.numberOfReplications=int(general.get('numberOfReplications', 'not found'))
    G.maxSimTime=float(general.get('maxSimTime', 'not found'))
    G.trace=general.get('trace', 'not found')
    G.confidenceLevel=float(general.get('confidenceLevel', 'not found'))

#creates the simulation objects
def createObjects():
    #Read the json data
    coreObject=G.JSONData['coreObject']
    modelResource=G.JSONData['modelResource']
   
    #define the lists
    G.SourceList=[]
    G.MachineList=[]
    G.ExitList=[]
    G.QueueList=[]    
    G.RepairmanList=[]
    G.AssemblyList=[]
    G.DismantleList=[]
    G.ConveyerList=[]
    
    #loop through all the model resources 
    #read the data and create them
    for i in range(len(modelResource)):
        resourceClass=modelResource[i].get('_class', 'not found')
        if resourceClass=='Dream.Repairman':
            id=modelResource[i].get('id', 'not found')
            name=modelResource[i].get('name', 'not found')
            capacity=int(modelResource[i].get('capacity', '1'))
            R=Repairman(id, name, capacity)
            G.RepairmanList.append(R)    
    
    #loop through all the core objects    
    #read the data and create them
    for i in range(len(coreObject)):
        objClass=coreObject[i].get('_class', 'not found')   
        if objClass=='Dream.Source':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            interarrivalTime=coreObject[i].get('interarrivalTime', 'not found')
            distributionType=interarrivalTime.get('distributionType', 'not found')
            mean=float(interarrivalTime.get('mean', '0'))        
            entity=str_to_class(coreObject[i].get('entity', 'not found'))
            successorList=coreObject[i].get('successorList', 'not found')
            S=Source(id, name, distributionType, mean, entity)
            S.nextIds=successorList
            G.SourceList.append(S)
            G.ObjList.append(S)
            
        elif objClass=='Dream.Machine':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            processingTime=coreObject[i].get('processingTime', 'not found')
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean', '0'))  
            stdev=float(processingTime.get('stdev', '0'))  
            min=float(processingTime.get('min', '0')) 
            max=float(processingTime.get('stdev', '0'))
            failures=coreObject[i].get('failures', 'not found')  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF', '0'))   
            MTTR=float(failures.get('MTTR', '0')) 
            availability=float(failures.get('availability', '0'))  
            needRepairman=failures.get('repairman', 'None')
            if(needRepairman=='None'):
                repairman=needRepairman
            else: 
                for j in range(len(G.RepairmanList)):
                    if(G.RepairmanList[j].id==needRepairman):
                        repairman=G.RepairmanList[j]
            predecessorList=coreObject[i].get('predecessorList', 'not found')
            successorList=coreObject[i].get('successorList', 'not found')
            M=Machine(id, name, 1, distributionType, [mean,stdev,min,max], failureDistribution,
                                                    MTTF, MTTR, availability, repairman)
            M.previousIds=predecessorList
            M.nextIds=successorList
            G.MachineList.append(M)
            G.ObjList.append(M)
            
        elif objClass=='Dream.Exit':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            predecessorList=coreObject[i].get('predecessorList', 'not found')
            E=Exit(id, name)
            E.previousIds=predecessorList
            G.ExitList.append(E)
            G.ObjList.append(E)
            
        elif objClass=='Dream.Queue':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            successorList=coreObject[i].get('successorList', 'not found')
            predecessorList=coreObject[i].get('predecessorList', 'not found')
            capacity=int(coreObject[i].get('capacity', '1'))
            isDummy=bool(int(coreObject[i].get('isDummy', '0')))
            Q=Queue(id, name, capacity, isDummy)
            Q.previousIds=predecessorList
            Q.nextIds=successorList
            G.QueueList.append(Q)
            G.ObjList.append(Q)
            
        elif objClass=='Dream.Assembly':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            processingTime=coreObject[i].get('processingTime', 'not found')
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean', '0'))  
            stdev=float(processingTime.get('stdev', '0'))  
            min=float(processingTime.get('min', '0')) 
            max=float(processingTime.get('stdev', '0'))
            predecessorPartList=coreObject[i].get('predecessorPartList', 'not found')
            predecessorFrameList=coreObject[i].get('predecessorFrameList', 'not found')
            successorList=coreObject[i].get('successorList', 'not found')
            A=Assembly(id, name, distributionType, [mean,stdev,min,max])
            A.previousPartIds=predecessorPartList
            A.previousFrameIds=predecessorFrameList
            A.nextIds=successorList
            G.AssemblyList.append(A)
            G.ObjList.append(A)
            
        elif objClass=='Dream.Dismantle':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            processingTime=coreObject[i].get('processingTime', 'not found')
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean', '0'))  
            stdev=float(processingTime.get('stdev', '0'))  
            min=float(processingTime.get('min', '0')) 
            max=float(processingTime.get('stdev', '0'))
            successorPartList=coreObject[i].get('successorPartList', 'not found')
            successorFrameList=coreObject[i].get('successorFrameList', 'not found')
            predecessorList=coreObject[i].get('predecessorList', 'not found')
            D=Dismantle(id, name, distributionType, [mean,stdev,min,max])
            D.nextPartIds=successorPartList
            D.nextFrameIds=successorFrameList
            D.previousIds=predecessorList
            G.DismantleList.append(D)
            G.ObjList.append(D)
            
        elif objClass=='Dream.Conveyer':
            id=coreObject[i].get('id', 'not found')
            name=coreObject[i].get('name', 'not found')
            length=float(coreObject[i].get('length', '10'))
            speed=float(coreObject[i].get('speed', '1'))
            successorList=coreObject[i].get('successorList', 'not found')
            predecessorList=coreObject[i].get('predecessorList', 'not found')
            C=Conveyer(id, name, length, speed)
            C.previousIds=predecessorList
            C.nextIds=successorList
            G.ObjList.append(C)
            G.ConveyerList.append(C)

#defines the topology (predecessors and successors for all the objects)
def setTopology():
    
    #loop through all the objects  
    for i in range(len(G.ObjList)):
        next=[]
        previous=[]
        for j in range(len(G.ObjList[i].previousIds)):
            for q in range(len(G.ObjList)):
                if G.ObjList[q].id==G.ObjList[i].previousIds[j]:
                    previous.append(G.ObjList[q])
                    
        for j in range(len(G.ObjList[i].nextIds)):
            for q in range(len(G.ObjList)):
                if G.ObjList[q].id==G.ObjList[i].nextIds[j]:
                    next.append(G.ObjList[q])      
                    
                    
        if G.ObjList[i].type=="Source":
            G.ObjList[i].defineRouting(next)
        elif G.ObjList[i].type=="Exit":
            G.ObjList[i].defineRouting(previous)
            
        #Assembly should be changed to identify what the entity that it receives is.
        #previousPart and previousFrame will become problematic    
        elif G.ObjList[i].type=="Assembly":
            previousPart=[]
            previousFrame=[]
            for j in range(len(G.ObjList[i].previousPartIds)):
                for q in range(len(G.ObjList)):
                    if G.ObjList[q].id==G.ObjList[i].previousPartIds[j]:
                        previousPart.append(G.ObjList[q])
            for j in range(len(G.ObjList[i].previousFrameIds)):
                for q in range(len(G.ObjList)):
                    if G.ObjList[q].id==G.ObjList[i].previousFrameIds[j]:
                        previousFrame.append(G.ObjList[q])
            G.ObjList[i].defineRouting(previousPart, previousFrame, next)
        #Dispatch should be changed to identify what the the successor is.
        #nextPart and nextFrame will become problematic    
        elif G.ObjList[i].type=="Dismantle":
            nextPart=[]
            nextFrame=[]
            for j in range(len(G.ObjList[i].nextPartIds)):
                for q in range(len(G.ObjList)):
                    if G.ObjList[q].id==G.ObjList[i].nextPartIds[j]:
                        nextPart.append(G.ObjList[q])
            for j in range(len(G.ObjList[i].nextFrameIds)):
                for q in range(len(G.ObjList)):
                    if G.ObjList[q].id==G.ObjList[i].nextFrameIds[j]:
                        nextFrame.append(G.ObjList[q])
            G.ObjList[i].defineRouting(previous, nextPart, nextFrame)
        else:
            G.ObjList[i].defineRouting(previous, next)

#used to convert a string read from the input to object type
def str_to_class(str):
    return getattr(sys.modules[__name__], str)

#initializes all the objects that are in the topology
def initializeObjects():
    for j in range(len(G.ObjList)):       
        G.ObjList[j].initialize()
    for j in range(len(G.RepairmanList)):       
        G.RepairmanList[j].initialize()
    
#activates all the objects    
def activateObjects():   
    for j in range(len(G.ObjList)):
        try:
            activate(G.ObjList[j],G.ObjList[j].run())   
        except AttributeError:
            pass

#the main  script that is ran                                 
def main():
 
    #create an empty list to store all the objects in   
    G.ObjList=[]
    
    #user inputs the id of the JSON file
    topologyId=raw_input("give the topology id\n")
    try:
        G.JSONFile=open('JSONInputs/Topology'+str(topologyId)+'.JSON', "r")
    except IOError:
        print "no such topology file. The programm is terminated"
        sys.exit()

    start=time.time()   #start counting execution time 
    
    #read the input from the JSON file and create the line
    G.InputData=G.JSONFile.read()
    G.JSONData=json.loads(G.InputData)
    readGeneralInput()
    createObjects()
    setTopology() 
              
    #run the experiment (replications)          
    for i in range(G.numberOfReplications):
        print "start run number "+str(i+1) 
        G.seed+=1
        G.Rnd=Random(G.seed) 
              
        initialize()                        #initialize the simulation 
        initializeObjects()
        activateObjects()
                            
        simulate(until=G.maxSimTime)      #start the simulation
        
        #carry on the post processing operations for every object in the topology       
        for j in range(len(G.ObjList)):
            G.ObjList[j].postProcessing(G.maxSimTime) 
            
        #output trace to excel
        if(G.trace=="Yes"):
            G.traceFile.save('trace'+str(i+1)+'.xls')
            G.traceIndex=0    #index that shows in what row we are
            G.sheetIndex=1    #index that shows in what sheet we are
            G.traceFile = xlwt.Workbook()     #create excel file
            G.traceSheet = G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)  #create excel sheet
    
    G.outputSheet.write(G.outputIndex,0, "Execution Time")
    G.outputSheet.write(G.outputIndex,1, str(time.time()-start)+" seconds")
    G.outputIndex+=2 
        
    #output data to excel for every object in the topology         
    for j in range(len(G.ObjList)):
        G.ObjList[j].outputResultsXL(G.maxSimTime)            

    G.outputFile.save("output.xls")      
    print "execution time="+str(time.time()-start)  
    
    #print len(G.ConveyerList[0].Res.activeQ)   
    '''
    for i in range(len(G.ConveyerList[0].Res.activeQ)):
        print G.ConveyerList[0].Res.activeQ[i].name
    print (G.ConveyerList[0].position)   
    '''
if __name__ == '__main__': main()