# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================
'''
Created on 27 May 2013

@author: George
'''
'''
main script. Reads data from the CMSD xml files that Panos creates, 
generates and runs the simulation and prints the results to excel
'''
from warnings import warn
import logging
logger = logging.getLogger("dream.platform")


from SimPy.Simulation import activate, initialize, simulate, now, infinity
from Globals import G 
from Source import Source
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
from Job import Job
from MachineJobShop import MachineJobShop
from QueueJobShop import QueueJobShop
from ExitJobShop import ExitJobShop
import xlwt
import xlrd
import time
from random import Random
import sys
import os.path

from xml.dom.minidom import parseString
from xml.dom.minidom import parse


#reads general simulation inputs
#CMSD does not have to do with such inputs (and it should not as they do not have to do with the system but with the simulation experiment)
#so these are hard coded for now
def readGeneralInput():
    G.numberOfReplications=1
    G.maxSimTime=1440
    G.trace="Yes"
    G.confidenceLevel=0.95

#Reads the resources of the CMSD file and creates the objects
def readResources():
    G.SourceList=[]
    G.MachineList=[]
    G.ExitList=[]
    G.QueueList=[]    
    G.RepairmanList=[]
    G.AssemblyList=[]
    G.DismantleList=[]
    G.ConveyerList=[]
    
    resource=(G.CMSDData.getElementsByTagName('Resource'))
    
    #this loop will search in all the objects for repairmen and create them.
    #repairmen have to be created first since they may be used in the creation of the other objects
    for i in range(len(resource)):
        #get the class
        try:
            resourceClass=resource[i].getElementsByTagName('ResourceClassIdentifier')
            resourceClass=resourceClass[0].toxml().replace('<ResourceClassIdentifier>','').replace('</ResourceClassIdentifier>','')
        except IndexError:
            continue
    
        if resourceClass=='Repairman':
            id=resource[i].getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            name=resource[i].getElementsByTagName('Name')
            name=name[0].toxml().replace('<Name>','').replace('</Name>','')      
            property=resource[i].getElementsByTagName('Property')      
            for j in range(len(property)):
                propertyName=property[j].getElementsByTagName('Name') 
                propertyName=propertyName[0].toxml().replace('<Name>','').replace('</Name>','')
                if propertyName=='capacity':
                    capacity=property[j].getElementsByTagName('Value') 
                    capacity=int(capacity[0].toxml().replace('<Value>','').replace('</Value>',''))
            
            R=Repairman(id, name, capacity)
            G.RepairmanList.append(R)           
                           
    for i in range(len(resource)):
        #get the class
        try:
            resourceClass=resource[i].getElementsByTagName('ResourceClassIdentifier')
            resourceClass=resourceClass[0].toxml().replace('<ResourceClassIdentifier>','').replace('</ResourceClassIdentifier>','')
        except IndexError:
            continue       
        
        if resourceClass=='Source':
            id=resource[i].getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            name=resource[i].getElementsByTagName('Name')
            name=name[0].toxml().replace('<Name>','').replace('</Name>','') 
            property=resource[i].getElementsByTagName('Property')      
            for j in range(len(property)):
                propertyName=property[j].getElementsByTagName('Name') 
                propertyName=propertyName[0].toxml().replace('<Name>','').replace('</Name>','')
                if propertyName=='partType':
                    partType=property[j].getElementsByTagName('Value') 
                    partType=(partType[0].toxml().replace('<Value>','').replace('</Value>',''))
                    entity=str_to_class(partType)
                elif propertyName=='interarrivalTime':
                    unit=property[j].getElementsByTagName('Unit')
                    unit=unit[0].toxml().replace('<Unit>','').replace('</Unit>','')
                    distribution=property[j].getElementsByTagName('Distribution')
                    distributionType=distribution[0].getElementsByTagName('Name')
                    distributionType=distributionType[0].toxml().replace('<Name>','').replace('</Name>','')
                    distributionParameter=distribution[0].getElementsByTagName('DistributionParameter')
                    distributionParameterName=distributionParameter[0].getElementsByTagName('Name')                        
                    distributionParameterName=distributionParameterName[0].toxml().replace('<Name>','').replace('</Name>','')
                    mean=distributionParameter[0].getElementsByTagName('Value')
                    mean=float(mean[0].toxml().replace('<Value>','').replace('</Value>',''))

            S=Source(id, name, distributionType, mean, entity)
            G.SourceList.append(S)
            G.ObjList.append(S)
            
        elif resourceClass=='Machine':
            id=resource[i].getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            name=resource[i].getElementsByTagName('Name')
            name=name[0].toxml().replace('<Name>','').replace('</Name>','') 
            property=resource[i].getElementsByTagName('Property')   
            for j in range(len(property)):
                propertyName=property[j].getElementsByTagName('Name') 
                propertyName=propertyName[0].toxml().replace('<Name>','').replace('</Name>','')
                if propertyName=='ProcessTime':
                    unit=property[j].getElementsByTagName('Unit')
                    unit=unit[0].toxml().replace('<Unit>','').replace('</Unit>','')
                    distribution=property[j].getElementsByTagName('Distribution')
                    distributionType=distribution[0].getElementsByTagName('Name')
                    distributionType=distributionType[0].toxml().replace('<Name>','').replace('</Name>','')        
                    distributionParameter=distribution[0].getElementsByTagName('DistributionParameter')
                    mean=0
                    stdev=0
                    min=0
                    max=0
                    availability=0
                    failureDistribution=None
                    for k in range(len(distributionParameter)):
                        distributionParameterName=distributionParameter[0].getElementsByTagName('Name')                        
                        distributionParameterName=distributionParameterName[0].toxml().replace('<Name>','').replace('</Name>','')
                        if distributionParameterName=='mean':
                            mean=distributionParameter[0].getElementsByTagName('Value')
                            mean=float(mean[0].toxml().replace('<Value>','').replace('</Value>',''))
                        elif distributionParameterName=='stdev':
                            stdev=distributionParameter[0].getElementsByTagName('Value')
                            stdev=float(stdev[0].toxml().replace('<Value>','').replace('</Value>',''))
                        elif distributionParameterName=='min':
                            min=distributionParameter[0].getElementsByTagName('Value')
                            min=float(mean[0].toxml().replace('<Value>','').replace('</Value>',''))
                        elif distributionParameterName=='max':
                            max=distributionParameter[0].getElementsByTagName('Value')
                            max=float(mean[0].toxml().replace('<Value>','').replace('</Value>',''))
                elif propertyName=='MeanTimeToFailure':
                    unit=property[j].getElementsByTagName('Unit')
                    unit=unit[0].toxml().replace('<Unit>','').replace('</Unit>','')
                    distribution=property[j].getElementsByTagName('Distribution')
                    failureDistribution=distribution[0].getElementsByTagName('Name')
                    failureDistribution=failureDistribution[0].toxml().replace('<Name>','').replace('</Name>','')    
                    distributionParameter=distribution[0].getElementsByTagName('DistributionParameter')
                    for k in range(len(distributionParameter)):
                        distributionParameterName=distributionParameter[0].getElementsByTagName('Name')                        
                        distributionParameterName=distributionParameterName[0].toxml().replace('<Name>','').replace('</Name>','')
                        if distributionParameterName=='mean':
                            MTTF=distributionParameter[0].getElementsByTagName('Value')
                            MTTF=float(MTTF[0].toxml().replace('<Value>','').replace('</Value>',''))
                        elif distributionParameterName=='availability':
                            availability=distributionParameter[0].getElementsByTagName('Value')
                            availability=(availability[0].toxml().replace('<Value>','').replace('</Value>',''))
                elif propertyName=='MeanTimeToRepair':
                    unit=property[j].getElementsByTagName('Unit')
                    unit=unit[0].toxml().replace('<Unit>','').replace('</Unit>','')
                    distribution=property[j].getElementsByTagName('Distribution')
                    failureDistribution=distribution[0].getElementsByTagName('Name')
                    failureDistribution=failureDistribution[0].toxml().replace('<Name>','').replace('</Name>','')     
                    distributionParameter=distribution[0].getElementsByTagName('DistributionParameter')
                    for k in range(len(distributionParameter)):
                        distributionParameterName=distributionParameter[0].getElementsByTagName('Name')                        
                        distributionParameterName=distributionParameterName[0].toxml().replace('<Name>','').replace('</Name>','')
                        if distributionParameterName=='mean':
                            MTTR=distributionParameter[0].getElementsByTagName('Value')
                            MTTR=float(MTTR[0].toxml().replace('<Value>','').replace('</Value>',''))
                        elif distributionParameterName=='availability':
                            availability=distributionParameter[0].getElementsByTagName('Value')
                            availability=(availability[0].toxml().replace('<Value>','').replace('</Value>',''))
                elif propertyName=='RepairmanRequired':
                    repairmanID=property[j].getElementsByTagName('ResourceIdentifier')
                    repairmanID=(repairmanID[0].toxml().replace('<ResourceIdentifier>','').replace('</ResourceIdentifier>',''))
                    if repairmanID=='None':
                        repairman=repairmanID
                    else: 
                        for j in range(len(G.RepairmanList)):
                            if(G.RepairmanList[j].id==repairmanID):
                                repairman=G.RepairmanList[j]
            
            M=Machine(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, repairman=repairman,
                                                    mean=mean,stdev=stdev,min=min,max=max)
            G.MachineList.append(M)
            G.ObjList.append(M)
            
        elif resourceClass=='Queue':
            id=resource[i].getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            name=resource[i].getElementsByTagName('Name')
            name=name[0].toxml().replace('<Name>','').replace('</Name>','') 
            property=resource[i].getElementsByTagName('Property')    
            isDummy=0
            capacity=2  
            for j in range(len(property)):
                propertyName=property[j].getElementsByTagName('Name') 
                propertyName=propertyName[0].toxml().replace('<Name>','').replace('</Name>','')
                if propertyName=='capacity':
                    capacity=property[j].getElementsByTagName('Value') 
                    capacity=int(capacity[0].toxml().replace('<Value>','').replace('</Value>',''))
                if propertyName=='isDummy':
                    capacity=property[j].getElementsByTagName('Value') 
                    capacity=int(capacity[0].toxml().replace('<Value>','').replace('</Value>',''))
            Q=Queue(id, name, capacity, isDummy)
            G.QueueList.append(Q)
            G.ObjList.append(Q)

        elif resourceClass=='Exit':
            id=resource[i].getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            name=resource[i].getElementsByTagName('Name')
            name=name[0].toxml().replace('<Name>','').replace('</Name>','') 
            E=Exit(id, name)
            G.ExitList.append(E)
            G.ObjList.append(E)

#reads the sequences process identifiers from the CMSD file            
def readProcessIdentifiersSequence():
    processPlan=G.CMSDData.getElementsByTagName('ProcessPlan')
    process=processPlan[0].getElementsByTagName('Process')
    G.processIdentifiers=[]
    for i in range(len(process)):
        try:
            processIdentifier=process[i].getElementsByTagName('Identifier')
            processIdentifierValue=processIdentifier[0].toxml().replace('<Identifier>','').replace('</Identifier>','')             
        except IndexError:
            continue
        if processIdentifierValue=='MainProcessSequence':
            processNode=process[i].getElementsByTagName('Process')
            for j in range(len(processNode)):
                processNodeIdentifier=processNode[j].getElementsByTagName('ProcessIdentifier')
                processNodeIdentifier=processNodeIdentifier[0].toxml().replace('<ProcessIdentifier>','').replace('</ProcessIdentifier>','')   
                G.processIdentifiers.append(processNodeIdentifier)
    
def readProcesses():
    process=G.CMSDData.getElementsByTagName('Process')
    G.TopologyList=[]
    for i in range(len(G.processIdentifiers)):
        G.TopologyList.append(None)
   
    for i in range(len(process)):
        index=0
        try:
            processIdentifier=process[i].getElementsByTagName('Identifier')
            processIdentifierValue=processIdentifier[0].toxml().replace('<Identifier>','').replace('</Identifier>','')     
            Description=process[i].getElementsByTagName('Description')
            Description=Description[0].toxml().replace('<Description>','').replace('</Description>','')   
        except IndexError:
            continue
        if processIdentifierValue in G.processIdentifiers:
            resourceIdentifier=process[i].getElementsByTagName('ResourceIdentifier')
            resourceIdentifier=resourceIdentifier[0].toxml().replace('<ResourceIdentifier>','').replace('</ResourceIdentifier>','')  
            G.TopologyList[G.processIdentifiers.index(processIdentifierValue)]=resourceIdentifier           
            
def setPredecessorIDs():
    for i in range(1,len(G.TopologyList)):
        for j in range(len(G.ObjList)):
            if G.ObjList[j].id==G.TopologyList[i]:
                G.ObjList[j].previousIds.append(G.TopologyList[i-1])
    
def setSuccessorIDs():
    for i in range(0,len(G.TopologyList)-1):
        for j in range(len(G.ObjList)):
            if G.ObjList[j].id==G.TopologyList[i]:
                G.ObjList[j].nextIds.append(G.TopologyList[i+1])
                  
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
    topologyId=raw_input("give the path to the CMSD file\n")
    try:
        G.CMSDFile=open(str(topologyId), "r")
    except IOError:
        print "no such file. The programm is terminated"
        sys.exit()

    start=time.time()   #start counting execution time 
    
    #read the input from the CMSD file and create the line
    G.InputData=G.CMSDFile.read()
    G.CMSDData=parseString(G.InputData)
    readGeneralInput()
    readResources()
    readProcessIdentifiersSequence()
    readProcesses()
    setPredecessorIDs()
    setSuccessorIDs()
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
   
    
if __name__ == '__main__': main()