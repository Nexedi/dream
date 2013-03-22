'''
Created on 21 Feb 2013

@author: George
'''

'''
The main script that is ran. 
It reads the inputs, runs the experiments and calls the post-processing method
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
import xlwt
import xlrd
import time
import numpy as np
from random import Random
import sys

#read general simulation inputs
def readGeneralInput():
    GeneralXL=xlrd.open_workbook('inputs/General.xls')
    GeneralSheet = GeneralXL.sheet_by_index(0) 
    G.numberOfReplications=int(GeneralSheet.cell(1,1).value)
    G.maxSimTime=GeneralSheet.cell(2,1).value
    G.trace=GeneralSheet.cell(3,1).value
    G.confidenceLevel=GeneralSheet.cell(4,1).value  

#create the simulation objects
def createObjects():
    #Read Source Data and create sources
    SourceXL=xlrd.open_workbook('inputs/Source.xls')
    SourceSheet = SourceXL.sheet_by_index(0)    
    i=1

    G.SourceList=[]     #a list that will hold all the sources
    while(SourceSheet.cell(0,i).value!="END"):
        if SourceSheet.cell(3,i).value=="Part":
            S=Source(i, "S"+str(i), SourceSheet.cell(1,i).value, SourceSheet.cell(2,i).value, Part)
        elif SourceSheet.cell(3,i).value=="Frame":  
            S=Source(i, "S"+str(i), SourceSheet.cell(1,i).value, SourceSheet.cell(2,i).value, Frame)  
        G.SourceList.append(S)
        i+=1  
    G.ObjList=G.ObjList+G.SourceList  #add sources also to object list
    
    #Read Queue Data and create queues
    QueueXL=xlrd.open_workbook('inputs/Queue.xls')
    QueueSheet = QueueXL.sheet_by_index(0)    
    i=1

    G.QueueList=[]     #a list that will hold all the queues
    while(QueueSheet.cell(0,i).value!="END"):
        if QueueSheet.cell(2,i).value=="Yes":
            Q=Queue(i, "Q"+str(i), int(QueueSheet.cell(1,i).value), True)
        else:   
            Q=Queue(i, "Q"+str(i), int(QueueSheet.cell(1,i).value), False)   
        i+=1  
        G.QueueList.append(Q)
    G.ObjList=G.ObjList+G.QueueList    #add queues also to object list
 
    #Read Queue Data and create QueueLifo
    QueueLIFOXL=xlrd.open_workbook('inputs/QueueLIFO.xls')
    QueueLIFOSheet = QueueLIFOXL.sheet_by_index(0)    
    i=1

    G.QueueLIFOList=[]     #a list that will hold all the queues
    while(QueueLIFOSheet.cell(0,i).value!="END"):
        if QueueLIFOSheet.cell(2,i).value=="Yes":
            Q=QueueLIFO(i, "QLIFO"+str(i), int(QueueLIFOSheet.cell(1,i).value), True)
        else:   
            Q=QueueLIFO(i, "QLIFO"+str(i), int(QueueLIFOSheet.cell(1,i).value), False)   
        i+=1  
        G.QueueLIFOList.append(Q)
    G.ObjList=G.ObjList+G.QueueLIFOList    #add queues also to object list
 
    #Read Repairman Data and create repairmen
    RepairmanXL=xlrd.open_workbook('inputs/Repairman.xls')
    RepairmanSheet = RepairmanXL.sheet_by_index(0)    
    i=1

    G.RepairmanList=[]     #a list that will hold all the repairmen
    while(RepairmanSheet.cell(0,i).value!="END"):
        W=Repairman(i, "W"+str(i), RepairmanSheet.cell(1,i).value)
        G.RepairmanList.append(W)
        i+=1  
    G.ObjList=G.ObjList+G.RepairmanList  #add repairmen also to object list
  
    #Read Machine Data and create machines
    MachineXL=xlrd.open_workbook('inputs/Machine.xls')
    MachineSheet = MachineXL.sheet_by_index(0)    
    i=1
    

    G.MachineList=[]     #a list that will hold all the machines
    while(MachineSheet.cell(0,i).value!="END"):
        if MachineSheet.cell(11,i).value=="Yes" and len(G.RepairmanList)>0:
            MR=G.RepairmanList[0]
        else:
            MR="None"         
        
        M=Machine(i, "M"+str(i), int(MachineSheet.cell(1,i).value), MachineSheet.cell(2,i).value, [MachineSheet.cell(3,i).value, MachineSheet.cell(4,i).value,
                                                    MachineSheet.cell(5,i).value, MachineSheet.cell(6,i).value], MachineSheet.cell(7,i).value,
                                                    MachineSheet.cell(8,i).value, MachineSheet.cell(9,i).value, MachineSheet.cell(10,i).value,
                                                    MR)
        G.MachineList.append(M)
        i+=1  
    G.ObjList=G.ObjList+G.MachineList    #add machines also to object list #add sources also to object list  
    
    #Read Exit Data and create exits
    ExitXL=xlrd.open_workbook('inputs/Exit.xls')
    ExitSheet = ExitXL.sheet_by_index(0)    
    i=1 
    
    G.ExitList=[]   #a list that will hold all the exits
    while(ExitSheet.cell(0,i).value!="END"):          
        E=Exit(i, "E"+str(i))
        G.ExitList.append(E)
        i+=1  
    G.ObjList=G.ObjList+G.ExitList    #add exits also to object list 
   
   
    #Read Assembly Data and create assemblies
    AssemblyXL=xlrd.open_workbook('inputs/Assembly.xls')
    AssemblySheet = AssemblyXL.sheet_by_index(0)    
    i=1   
    
    G.AssemblyList=[]     #a list that will hold all the machines
    while(AssemblySheet.cell(0,i).value!="END"):              
        A=Assembly(i, "A"+str(i), AssemblySheet.cell(1,i).value, [AssemblySheet.cell(2,i).value, AssemblySheet.cell(3,i).value,
                                                    AssemblySheet.cell(4,i).value, AssemblySheet.cell(5,i).value])
        G.AssemblyList.append(A)
        i+=1  
    G.ObjList=G.ObjList+G.AssemblyList    #add machines also to object list #add sources also to object list 

#reads the topology and defines it for the objects
def setTopology(topologyFilename):  
    G.TopologyList=[]
    
    try:
        TopologyXL=xlrd.open_workbook('inputs/'+topologyFilename+'.xls')
    except IOError:
        print "no such topology file. The programm is terminated"
        sys.exit()
    
    TopologySheet = TopologyXL.sheet_by_index(0) 
    i=1
    while(TopologySheet.cell(i,0).value!="END"):
        curList=list(str(TopologySheet.cell(i,0).value))
        if curList[0]=="S":
            next=str(TopologySheet.cell(i,2).value)
            for j in range(len(G.ObjList)):
                if G.ObjList[j].objName==next:
                    nextObjInd=j
            G.SourceList[int(curList[1])-1].defineRouting([G.ObjList[nextObjInd]])
            G.TopologyList.append(G.SourceList[int(curList[1])-1])
            
        elif curList[0]=="Q":
            previous=str(TopologySheet.cell(i,1).value)
            next=str(TopologySheet.cell(i,2).value)
            for j in range(len(G.ObjList)):
                if G.ObjList[j].objName==previous:
                    previousObjInd=j   
                if  G.ObjList[j].objName==next:
                    nextObjInd=j                       
            G.QueueList[int(curList[1])-1].defineRouting([G.ObjList[previousObjInd]], [G.ObjList[nextObjInd]])    
            G.TopologyList.append(G.QueueList[int(curList[1])-1])
            
        elif curList[0]=="M":
            previous=str(TopologySheet.cell(i,1).value)
            next=str(TopologySheet.cell(i,2).value)
            for j in range(len(G.ObjList)):
                if G.ObjList[j].objName==previous:
                    previousObjInd=j   
                if  G.ObjList[j].objName==next:
                    nextObjInd=j                       
            G.MachineList[int(curList[1])-1].defineRouting([G.ObjList[previousObjInd]], [G.ObjList[nextObjInd]]) 
            G.TopologyList.append(G.MachineList[int(curList[1])-1])
            
        elif curList[0]=="A":
            previousPart=str(TopologySheet.cell(i,3).value)
            previousFrame=str(TopologySheet.cell(i,4).value)
            next=str(TopologySheet.cell(i,2).value)
            for j in range(len(G.ObjList)):
                if G.ObjList[j].objName==previousPart:
                    previousPartObjInd=j   
                if G.ObjList[j].objName==previousFrame:
                    previousFrameObjInd=j   
                if  G.ObjList[j].objName==next:
                    nextObjInd=j                       
            G.AssemblyList[int(curList[1])-1].defineRouting([G.ObjList[previousPartObjInd]], [G.ObjList[previousFrameObjInd]], [G.ObjList[nextObjInd]]) 
            G.TopologyList.append(G.AssemblyList[int(curList[1])-1])

        elif curList[0]=="E":
            previous=str(TopologySheet.cell(i,1).value)
            for j in range(len(G.ObjList)):
                if G.ObjList[j].objName==previous:
                    previousObjInd=j                 
            G.ExitList[int(curList[1])-1].defineRouting([G.ObjList[previousObjInd]]) 
            G.TopologyList.append(G.ExitList[int(curList[1])-1])           
        i+=1 
    G.TopologyList.append(G.RepairmanList[0]) 

#initializes all the objects that are in the topology
def initializeObjects():
    for j in range(len(G.TopologyList)):       
        G.TopologyList[j].initialize()
    
#activates all the objects    
def activateObjects():   
    for j in range(len(G.TopologyList)):
        try:
            activate(G.TopologyList[j],G.TopologyList[j].Run())   
        except AttributeError:
            pass

#the main  script that is ran                                 
def main():
    
    topologyId=raw_input("give the topology id\n")
    G.ObjList=[]
    start=time.time()   #start counting execution time
    readGeneralInput()
    createObjects()
    
    setTopology("Topology"+topologyId)
    for j in range(len(G.TopologyList)):
        print G.TopologyList[j].objName
    
    for i in range(G.numberOfReplications):
        print "start run number "+str(i+1) 
        G.seed+=1
        G.Rnd=Random(G.seed) 
              
        initialize()                        #initialize the simulation 
        initializeObjects()
        activateObjects()       
    
        for j in range(len(G.TopologyList)):
            pass
        #print G.TopologyList[j]
          
        simulate(until=G.maxSimTime)      #start the simulation
        
        #carry on the post processing operations for every object in the topology       
        for j in range(len(G.TopologyList)):
            G.TopologyList[j].postProcessing(G.maxSimTime) 
            
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
    for j in range(len(G.TopologyList)):
        G.TopologyList[j].outputResultsXL(G.maxSimTime)            

    G.outputFile.save("output.xls")      
    print "execution time="+str(time.time()-start) 

if __name__ == '__main__': main()