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
main script. Reads data from the CMSD xml files that Panos creates, 
generates and runs the simulation and prints the results to excel
'''
from warnings import warn
import logging
logger = logging.getLogger("dream.platform")


try:
  import scipy
except ImportError:
  class scipy:
    class stats:
      @staticmethod
      def bayes_mvs(*args, **kw):
        warn("Scipy is missing, using fake implementation")
        serie, confidence = args
        import numpy
        mean = numpy.mean(serie), (numpy.min(serie), numpy.max(serie))
        var = 0, (0, 0)
        std = 0, (0, 0) 
        return mean, var, std
  import sys
  sys.modules['scipy.stats'] = scipy.stats
  sys.modules['scipy'] = scipy
  logger.error("Scipy cannot be imported, using dummy implementation")

# from SimPy.Simulation import activate, initialize, simulate, now, infinity
import simpy

from Globals import G 
from Source import Source
from Machine import Machine
from Exit import Exit
from Queue import Queue
# from QueueLIFO import QueueLIFO
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
from Batch import Batch
from SubBatch import SubBatch
from BatchSource import BatchSource
from BatchDecomposition import BatchDecomposition
from RandomNumberGenerator import RandomNumberGenerator

import xlwt
import xlrd
import time
import json
from random import Random
import sys
import os.path
from xml.etree import ElementTree as et

from xml.dom.minidom import parseString
from xml.dom.minidom import parse


class SubProcess(object):
   
    def __init__(self, id):
        self.id=id
        self.isEndProcess=False
        self.parent=None
        self.hasChildren=False
        self.childrenList=[]
        self.next=None
        self.previous=None
        self.type=None
        self.isBasic=False
        self.isFirstInSequence=False
        self.isLastInSequence=False
        self.firstEndChildrenList=[]
        self.lastEndChildrenList=[]

#reads general simulation inputs
#CMSD does not have to do with such inputs (and it should not as they do not have to do with the system but with the simulation experiment)
#so these are hard coded for now
def readGeneralInput():
    G.numberOfReplications=1
    G.maxSimTime=2880.0
    G.trace="Yes"
    G.confidenceLevel=0.95

def createLists():
        G.MachineList=[]
        G.QueueList=[]
        G.QueueIds=[]
        G.RepairmanList=[]

#reads and creates the stations
def createStations():
    resource=(G.CMSDData.getElementsByTagName('Resource'))
    
    #loop through the resources
    for item in resource:
        try:
            ResourceType=item.getElementsByTagName('ResourceType')
            ResourceType=ResourceType[0].toxml().replace('<ResourceType>','').replace('</ResourceType>','')
            #if it is station or machine, read id and name and create it
            if ResourceType=='station' or ResourceType=='machine':
                id=item.getElementsByTagName('Identifier')
                id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
                name=item.getElementsByTagName('Name')
                name=name[0].toxml().replace('<Name>','').replace('</Name>','')
                M=Machine(id, name)
                G.MachineList.append(M)
                G.ObjList.append(M)
        except IndexError:
            continue   
        
        
#reads and defines the process Ids for the stations created
def defineEndProcessIds():
    process=G.CMSDData.getElementsByTagName('Process')
    G.EndProcessIdsList=[]
    #loop through the processes
    for proc in process:
        try:
            #read the id of the process
            id=proc.getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
                        
            #read the id of the station resource
            ResourcesRequired=proc.getElementsByTagName('ResourcesRequired')
            for res in ResourcesRequired:
                Resource=res.getElementsByTagName('Resource')
                ResourceIdentifier=Resource[0].getElementsByTagName('ResourceIdentifier')
                ResourceIdentifier=ResourceIdentifier[0].toxml().replace('<ResourceIdentifier>','').replace('</ResourceIdentifier>','')
                
                #loop through the stations and for the one with the id set the processing time
                for obj in G.ObjList:
                    if obj.id==ResourceIdentifier:
                        obj.resourceIdentifier=id  
                        G.EndProcessIdsList.append(id)                      
        except IndexError:
            continue    


#reads and defines the processing time for the stations created
def defineProcessingTimes():
    process=G.CMSDData.getElementsByTagName('Process')
    
    #loop through the processes
    for proc in process:
        try:
            #read the mean processing time a the unit
            OperationTime=proc.getElementsByTagName('OperationTime')
            distr=OperationTime[0].getElementsByTagName('Distribution') 
            distrName=distr[0].getElementsByTagName('Name')
            distrName=distrName[0].toxml().replace('<Name>','').replace('</Name>','')
            
            distrParA=distr[0].getElementsByTagName('DistributionParameterA')
            parAName=distrParA[0].getElementsByTagName('Name')
            parAName=parAName[0].toxml().replace('<Name>','').replace('</Name>','')
            parAValue=distrParA[0].getElementsByTagName('Value')
            parAValue=parAValue[0].toxml().replace('<Value>','').replace('</Value>','')
            
            distrParB=distr[0].getElementsByTagName('DistributionParameterB')
            parBName=distrParB[0].getElementsByTagName('Name')
            parBName=parBName[0].toxml().replace('<Name>','').replace('</Name>','')
            parBValue=distrParB[0].getElementsByTagName('Value')
            parBValue=parBValue[0].toxml().replace('<Value>','').replace('</Value>','')
            
            #read the id of the station resource
            ResourcesRequired=proc.getElementsByTagName('ResourcesRequired')
            for res in ResourcesRequired:
                Resource=res.getElementsByTagName('Resource')
                ResourceIdentifier=Resource[0].getElementsByTagName('ResourceIdentifier')
                ResourceIdentifier=ResourceIdentifier[0].toxml().replace('<ResourceIdentifier>','').replace('</ResourceIdentifier>','')
                
                #loop through the stations and for the one with the id set the processing time
                distributionDict={str(distrName):{
                                        str(parAName):parAValue,
                                        str(parBName):parBValue    
                                }
                            }              
                for obj in G.ObjList:
                    if obj.id==ResourceIdentifier:
                        obj.rng=RandomNumberGenerator(obj,distributionDict)                      
        except IndexError:
            continue    
        
#reads and defines the scrap quantites for the stations created
def defineScrapQuantities():
    process=G.CMSDData.getElementsByTagName('Process')
    
    #loop through the processes
    for proc in process:
        try:
            #read the scrap quantity
            Property=proc.getElementsByTagName('Property')
            for prop in Property:
                name=prop.getElementsByTagName('Name')
                name=name[0].toxml().replace('<Name>','').replace('</Name>','')  
                if name=='ScrapQuantity':  
                    scrap=Property[0].getElementsByTagName('Distribution')           
                    scrapName=scrap[0].getElementsByTagName('Name')
                    scrapName=scrapName[0].toxml().replace('<Name>','').replace('</Name>','')
                    
                    distrParA=scrap[0].getElementsByTagName('DistributionParameterA')
                    parAName=distrParA[0].getElementsByTagName('Name')
                    parAName=parAName[0].toxml().replace('<Name>','').replace('</Name>','')
                    parAValue=distrParA[0].getElementsByTagName('Value')
                    parAValue=parAValue[0].toxml().replace('<Value>','').replace('</Value>','')
                     
                else:
                    continue
            
                #read the id of the station resource                
                ResourcesRequired=proc.getElementsByTagName('ResourcesRequired')
                for res in ResourcesRequired:
                    Resource=res.getElementsByTagName('Resource')
                    ResourceIdentifier=Resource[0].getElementsByTagName('ResourceIdentifier')
                    ResourceIdentifier=ResourceIdentifier[0].toxml().replace('<ResourceIdentifier>','').replace('</ResourceIdentifier>','')
                        
                    #loop through the stations and for the one with the id set the scrap
                    distributionDict={str(scrapName):{
                                        str(parAName):parAValue   
                                }
                            }              
                for obj in G.ObjList:
                    if obj.id==ResourceIdentifier:
                        obj.rng=RandomNumberGenerator(obj,distributionDict)                                   
        except IndexError:
            continue     
        
#reads (and creates if needed) the input buffers for the stations created
def defineBuffers():
    process=G.CMSDData.getElementsByTagName('Process')
    
    #loop through the processes
    for proc in process:
        try:
            #read the scrap quantity
            Property=proc.getElementsByTagName('Property')
            for prop in Property:
                name=prop.getElementsByTagName('Name')
                name=name[0].toxml().replace('<Name>','').replace('</Name>','')                
                
                if name=='BufferIn':            
                    id=prop.getElementsByTagName('Identifier')
                    id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
                    capacity=prop.getElementsByTagName('Capacity')
                    capacity=capacity[0].toxml().replace('<Capacity>','').replace('</Capacity>','')
                    capacity=int(capacity)

                else:
                    continue
            
                #read the id of the station resource
                ResourcesRequired=proc.getElementsByTagName('ResourcesRequired')
                for res in ResourcesRequired:
                    Resource=res.getElementsByTagName('Resource')
                    ResourceIdentifier=Resource[0].getElementsByTagName('ResourceIdentifier')
                    ResourceIdentifier=ResourceIdentifier[0].toxml().replace('<ResourceIdentifier>','').replace('</ResourceIdentifier>','')
                    
                    #loop through to find the machine of the process and connect them
                    M=None
                    for obj in G.ObjList:
                        if obj.id==ResourceIdentifier:
                            M=obj
                    if M==None:
                        continue
            
                #if the Queue already exists find it
                if id in G.QueueIds:
                    for item in G.QueueIds:
                        for queue in G.QueueList:
                            if id==queue.id:
                                Q=queue
                            
                #else create the Queue
                else:
                    Q=Queue(id=id, name=id, capacity=capacity)
                    Q.resourceIdentifier=[]
                    G.ObjList.append(Q)
                    G.QueueList.append(Q)
                    G.QueueIds.append(id)
            
                #set the Queue as predecessor of the Machine and vice versa
                Q.next.append(M)
                M.previous.append(Q)  
                Q.resourceIdentifier.append(M.resourceIdentifier)          
        except IndexError:
            continue      

#converts a value to minutes        
def convertTimeUnits(value, unit):
    if unit=='hour':
        value=value*60
    elif unit=='second':
        value=value/60.0
    return value

def getFirstProcessId():
    processPlan=G.CMSDData.getElementsByTagName('ProcessPlan')
    firstProcess=processPlan[0].getElementsByTagName('FirstProcess')
    firstProcessId=firstProcess[0].getElementsByTagName('ProcessIdentifier')
    firstProcessId=firstProcessId[0].toxml().replace('<ProcessIdentifier>','').replace('</ProcessIdentifier>','')
    return firstProcessId
    
    
def getProcessIds(processId):
    idsList=[]
    processPlan=G.CMSDData.getElementsByTagName('ProcessPlan')
    process=processPlan[0].getElementsByTagName('Process')
    for proc in process:
        try:
            id=proc.getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            if id==processId:
                subProcess=proc.getElementsByTagName('Process')
                for sp in subProcess:
                    subProcessid=sp.getElementsByTagName('ProcessIdentifier')
                    subProcessid=subProcessid[0].toxml().replace('<ProcessIdentifier>','').replace('</ProcessIdentifier>','')
                    idsList.append(subProcessid)
        except IndexError:
            continue  
    return idsList

def defineTheGroupTopology(id, start=False, end=False):
    pass

def getProcessById(id):
    for process in G.SubProcessList:
        if id==process.id:
            return process
        
def getQueueByResourceIdentifier(id):
    for queue in G.QueueList:
        for resourceIdentifier in queue.resourceIdentifier:
            if id==resourceIdentifier:
                return queue
        
def getMachineByResourceIdentifier(id):
    for machine in G.MachineList:
        if id==machine.resourceIdentifier:
            return machine
        
        
def getProcessType(process):
    processPlan=G.CMSDData.getElementsByTagName('ProcessPlan')
    cmsdProcess=processPlan[0].getElementsByTagName('Process') 
    for proc in cmsdProcess:
        try:
            id=proc.getElementsByTagName('Identifier')
            id=id[0].toxml().replace('<Identifier>','').replace('</Identifier>','')
            if id==process.id:
                type=proc.getElementsByTagName('Type')
                type=type[0].toxml().replace('<Type>','').replace('</Type>','')
                process.type=type
        except IndexError:
            continue  

def getProcessEndChildren(process):
    endChildrenList=[]
    if process.isEndProcess:
        return None
    proc=process
    for child in proc.childrenList:
        if checkIfIsEndProcess(child):
            endChildrenList.append(child)
        else:
            for grandchild in child.childrenList:
                if checkIfIsEndProcess(grandchild):
                    endChildrenList.append(grandchild)
    
    return endChildrenList

def checkIfIsEndProcess(process):
    if process.isEndProcess:
        return True
    return False

#used to convert a string read from the input to object type
def str_to_class(str):
    return getattr(sys.modules[__name__], str)

#initializes all the objects that are in the topology
def initializeObjects():
    for j in range(len(G.ObjList)):       
        G.ObjList[j].initialize()
    for j in range(len(G.RepairmanList)):       
        G.RepairmanList[j].initialize()
    
# ===========================================================================
#                        activates all the objects
# ===========================================================================
def activateObjects():
#     for element in G.ObjectInterruptionList:
#         G.env.process(element.run())       
    for element in G.ObjList:
        G.env.process(element.run())      

#the main  script that is ran 

def main(argv=[], input_data=None):
    argv = argv or sys.argv[1:]

    #create an empty list to store all the objects in   
    G.ObjList=[]
    S=BatchSource('S1', 'Source', interArrivalTime={'Fixed':{'mean':0.5}}, item=Batch, batchNumberOfUnits = 100)
    E=Exit('E1', 'Exit')
    G.ObjList.append(S)
    G.ObjList.append(E)    
#     G.RouterList=[]
    if input_data is None:  
        # user passes the topology filename as first argument to the program
        filename = argv[0]
        try:                                          # try to open the file with the inputs
            G.CMSDFile=open(filename, "r")            # global variable holding the file to be opened
        except IOError, IndexError:                               
            print "%s could not be open" % filename
            return "ERROR"
        G.InputData=G.CMSDFile.read()                 # pass the contents of the input file to the global var InputData
    else:
        G.InputData = input_data
    
    start=time.time()                               # start counting execution time                                 
    G.InputData=input_data.read()
    G.CMSDData=parseString(G.InputData)
    G.SubProcessList=[]
    G.SequenceList=[]
    G.BasicProcessList=[]
    
    readGeneralInput()
    createLists()
    createStations()
    defineEndProcessIds()
    defineProcessingTimes()
    defineScrapQuantities()
    defineBuffers()
    firstProcessId=getFirstProcessId()
    processGroupIds=getProcessIds(firstProcessId)
    G.processPlan=processGroupIds
    
    for id in processGroupIds:
        p=SubProcess(id)
        p.isBasic=True
        G.SubProcessList.append(p)
        G.BasicProcessList.append(p) 
           
    for proc in G.SubProcessList:
        if proc.id in G.EndProcessIdsList:
            proc.isEndProcess=True            
        else:
            processId=getProcessIds(proc.id)
            for id in processId:
                p=SubProcess(id)
                p.parent=proc
                proc.childrenList.append(p)
                G.SubProcessList.append(p)
    
    for proc in G.SubProcessList:
        getProcessType(proc)
        
    i=0    
    for id in G.processPlan:
        try:
            thisProc=getProcessById(id)
            nextProc=getProcessById(G.processPlan[i+1])
            thisProc.next=nextProc
            nextProc.previous=thisProc
            i+=1
        except:
            continue
    
    for proc in G.SubProcessList:
        if proc.type=='sequence':
            i=0
            for subProc in proc.childrenList:
                try:
                    thisProc=subProc
                    nextProc=proc.childrenList[i+1]
                    thisProc.next=nextProc
                    nextProc.previous=thisProc   
                    i+=1
                except:
                    continue
                  
    for proc in G.SubProcessList:
        if proc.isEndProcess:
            if proc.next:
                M=getMachineByResourceIdentifier(proc.id)
                Q=getQueueByResourceIdentifier(proc.next.id)
                M.next.append(Q)
                Q.previous.append(M)
                
    for proc in G.BasicProcessList:
        for endChild in getProcessEndChildren(proc):
            if not endChild.next:
                proc.lastEndChildrenList.append(endChild)
            if not endChild.previous:
                proc.firstEndChildrenList.append(endChild)
    
    for proc in G.BasicProcessList:
        if proc.next:
            for lastEndChild in proc.lastEndChildrenList:
                for firstEndChild in proc.next.firstEndChildrenList:
                    M=getMachineByResourceIdentifier(lastEndChild.id)
                    Q=getQueueByResourceIdentifier(firstEndChild.id)
                    if Q not in M.next:
                        M.next.append(Q)
                        Q.previous.append(M)   
        else:                
            for lastEndChild in proc.lastEndChildrenList:
                M=getMachineByResourceIdentifier(lastEndChild.id)
                if E not in M.next:
                    M.next.append(E)
                    E.previous.append(M)
        if not proc.previous:
            for firstEndChild in proc.firstEndChildrenList:
                Q=getQueueByResourceIdentifier(firstEndChild.id)
                if Q not in S.next:
                    Q.previous.append(S)
                    S.next.append(Q)
    
    '''
    for obj in G.ObjList:
        if obj.type=="Source":
            pass
        elif obj.type=="Exit":
            pass
        else:
            print "name:", obj.objName
            print "Previous:", 
            for prev in obj.previous:
                print prev.objName
            print "Next:", 
            for next in obj.next:
                print next.objName  
            print "*"*100
    '''
    
    #run the experiment (replications)          
    for i in range(G.numberOfReplications):
        print "start run number "+str(i+1) 
        G.env=simpy.Environment()    
        G.seed+=1
        G.Rnd=Random(G.seed)         

        G.ObjList=list(set(G.ObjList)) 
          
        initializeObjects()
        activateObjects()            
        G.env.run(until=G.maxSimTime)                
        
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
        
#     #output data to excel for every object in the topology         
    for object in G.ObjList:
        if object is not 'BatchSource':
            continue
        object.outputResultsXL(G.maxSimTime)    

    G.outputFile.save("output.xls")      
    print "execution time="+str(time.time()-start) 
    
    G.outputJSONFile=open('outputJSONFromCMSD.json', mode='w')
    G.outputJSON['_class'] = 'Dream.Simulation';
    G.outputJSON['general'] ={};
    G.outputJSON['general']['_class'] = 'Dream.Configuration';
    G.outputJSON['general']['totalExecutionTime'] = (time.time()-start);
    G.outputJSON['elementList'] =[];

    #output data to JSON for every object in the topology         
    for element in G.ObjList:
        element.outputResultsJSON()
        
    #output data to JSON for every resource in the topology         
    for model_resource in G.ModelResourceList:
        model_resource.outputResultsJSON()
                
    outputJSONString=json.dumps(G.outputJSON, indent=True)
    G.outputJSONFile.write(outputJSONString)
    
if __name__ == '__main__': main()