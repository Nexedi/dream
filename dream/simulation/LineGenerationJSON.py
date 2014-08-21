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
Created on 7 May 2013

@author: George
'''
'''
main script. Reads data from JSON, generates and runs the simulation and prints the results to excel
'''

# ===========================================================================
#                                    IMPORTS
# ===========================================================================
from warnings import warn
import logging
logger = logging.getLogger("dream.platform")


# By default numpy just prints on stderr when there's an error. We do not want
# to hide errors.
import numpy
numpy.seterr(all='raise')


# from SimPy.Simulation import activate, initialize, simulate, now, infinity
import simpy
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
from Batch import Batch
from SubBatch import SubBatch
from BatchSource import BatchSource
from BatchDecomposition import BatchDecomposition
from BatchReassembly import BatchReassembly
from RoutingQueue import RoutingQueue
from BatchScrapMachine import BatchScrapMachine
from LineClearance import LineClearance
from EventGenerator import EventGenerator
from Operator import Operator
from OperatorManagedJob import OperatorManagedJob
from OperatorPool import OperatorPool
from OperatedPoolBroker import Broker
from OperatedMachine import OperatedMachine
from BatchDecompositionStartTime import BatchDecompositionStartTime
from M3 import M3
from OrderComponent import OrderComponent
from ScheduledMaintenance import ScheduledMaintenance
from Failure import Failure
from Order import Order
from OrderDesign import OrderDesign
from Mould import Mould
from OrderDecomposition import OrderDecomposition
from ConditionalBuffer import ConditionalBuffer
from MouldAssemblyBuffer import MouldAssemblyBuffer
from MachineManagedJob import MachineManagedJob
from QueueManagedJob import QueueManagedJob
from ShiftScheduler import ShiftScheduler

import PrintRoute
from CapacityStation import CapacityStation
from CapacityStationExit import CapacityStationExit
from CapacityStationBuffer import CapacityStationBuffer
from CapacityStationController import CapacityStationController
from CapacityEntity import CapacityEntity
from CapacityProject import CapacityProject
from CapacityStationController import CapacityStationController

import ExcelHandler
import time
import json
from random import Random
import sys
import os.path
import Globals
import ast
import cProfile

# ===========================================================================
#                       reads general simulation inputs
# ===========================================================================
def readGeneralInput():
    general=G.JSONData['general']                                           # read the dict with key 'general'
    G.numberOfReplications=int(general.get('numberOfReplications', '1'))    # read the number of replications / default 1
    G.maxSimTime=float(general.get('maxSimTime', '100'))                    # get the maxSimTime / default 100
    G.trace=general.get('trace', 'No')                                      # get trace in order to check if trace is requested
    G.console=general.get('console', 'No')                                  # get console flag in order to check if console print is requested
    G.confidenceLevel=float(general.get('confidenceLevel', '0.95'))         # get the confidence level
    G.seed = general.get('seed')                                            # the seed for random number generation
    G.extraPropertyDict=general.get('extraPropertyDict', {})                # a dict to put extra properties that are 
                                                                            # generic for the model

# ===========================================================================
#                       creates the simulation objects
# ===========================================================================
def createObjects():

    json_data = G.JSONData
    #Read the json data
    nodes = json_data['nodes']                      # read from the dictionary the dicts with key 'nodes'
    edges = json_data['edges']                      # read from the dictionary the dicts with key 'edges'


    '''
    getSuccesorList method to get the successor 
    list of object with ID = id
    XXX slow implementation
    '''
    def getSuccessorList(node_id, predicate=lambda source, destination, edge_data: True):
      successor_list = []                           # dummy variable that holds the list to be returned
      for source, destination, edge_data in edges.values(): # for all the values in the dictionary edges
        if source == node_id:                               # for the node_id argument
          if predicate(source, destination, edge_data):     # find its 'destinations' and 
            successor_list.append(destination)              # append it to the successor list
      # XXX We should probably not need to sort, but there is a bug that
      # prevents Topology10 to work if this sort is not used.
      successor_list.sort()
      return successor_list
    '''
    define the lists of each object type
    '''
    G.SourceList=[]
    G.MachineList=[]
    G.ExitList=[]
    G.QueueList=[]    
    G.RepairmanList=[]
    G.AssemblyList=[]
    G.DismantleList=[]
    G.ConveyerList=[]
    G.MachineJobShopList=[]
    G.QueueJobShopList=[]
    G.ExitJobShopList=[]
    G.BatchDecompositionList=[]
    G.BatchSourceList=[]
    G.BatchReassemblyList=[]
    G.RoutingQueueList=[]
    G.LineClearanceList=[]
    G.EventGeneratorList=[]
    G.OperatorsList = []
    G.OperatorManagedJobsList = []
    G.OperatorPoolsList = []
    G.BrokersList = []
    G.Router = None
    G.OperatedMachineList = []
    G.BatchScrapMachineList=[]
    G.OrderDecompositionList=[]
    G.ConditionalBufferList=[]
    G.MouldAssemblyBufferList=[]
    G.MouldAssemblyList=[]
    G.MachineManagedJobList=[]
    G.QueueManagedJobList=[]
    G.ObjectResourceList=[]
    G.CapacityStationBufferList=[]
    G.CapacityStationList=[]
    G.CapacityStationExitList=[]
    G.CapacityStationControllerList=[]
    G.ObjectInterruptionList=[]

    '''
    loop through all the model resources 
    search for repairmen and operators in order to create them
    read the data and create them
    '''

    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
        element = element.copy()
        for k in ('element_id', 'top', 'left'):
          element.pop(k, None)
                                                                    # with key 'id' and value the the element_id
        resourceClass = element.pop('_class')                       # get the class type of the element
        if resourceClass=='Dream.Repairman':                        # check the object type
            id = element.get('id', 'not found')                     # get the id of the element
            name = element.get('name', id)                          # get the name of the element / default 'not_found'
            capacity = int(element.get('capacity') or 1)
            R = Repairman(element_id, name, capacity)               # create a repairman object
            R.coreObjectIds=getSuccessorList(id)                    # update the list of objects that the repairman repairs
                                                                    # calling the getSuccessorList() method on the repairman
            G.RepairmanList.append(R)                               # add the repairman to the RepairmanList
            G.ObjectResourceList.append(R) 
        elif resourceClass=='Dream.Operator':
            id = element.get('id', 'not found')                     # get the id of the element   / default 'not_found'
            name = element.get('name', 'not found')                 # get the name of the element / default 'not_found'
            capacity = int(element.get('capacity') or 1)
            schedulingRule=element.get('schedulingRule', 'FIFO')    # get the scheduling rule of the el. (how to choose which 
                                                                    # station to serve first) / default 'FIFO' i.e. the one that 
                                                                    # called first
            skills=element.get('skills',[])                         # list of stations that the operator can attend to
            O = Operator(element_id, name, capacity,schedulingRule,skills)                # create an operator object
            O.coreObjectIds=getSuccessorList(id)                	# update the list of objects that the operator operates
																	# calling the getSuccesorList() method on the operator
            G.OperatorsList.append(O)                               # add the operator to the RepairmanList
            G.ObjectResourceList.append(O) 
        elif resourceClass=='Dream.OperatorManagedJob':
            id = element.get('id', 'not found')                     # get the id of the element   / default 'not_found'
            name = element.get('name', 'not found')                 # get the name of the element / default 'not_found'
            capacity = int(element.get('capacity') or 1)            # get the capacity of the el. / defautl '1'
            schedulingRule=element.get('schedulingRule', 'FIFO')    # get the scheduling rule of the el. (how to choose which 
                                                                    # station to serve first) / default 'FIFO' i.e. the one that 
                                                                    # called first
            O = OperatorManagedJob(element_id, name, capacity,schedulingRule)      # create an operator object
            O.coreObjectIds=getSuccessorList(id)                    # update the list of objects that the operator operates
                                                                    # calling the getSuccesorList() method on the operator
            G.OperatorsList.append(O)                               # add the operator to the RepairmanList
            G.OperatorManagedJobsList.append(O)
            G.ObjectResourceList.append(O) 
    '''
    loop through all the model resources 
    search for operatorPools in order to create them
    read the data and create them
    '''
    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
                                                                    # the key is the element_id and the second is the 
                                                                    # element itself 
        element = element.copy()
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
#         for k in ('element_id', 'top', 'left'):
#           element.pop(k, None)
                                                                    # with key 'id' and value the the element_id
        resourceClass = element.pop('_class')          # get the class type of the element
        if resourceClass=='Dream.OperatorPool':
            id = element.get('id', 'not found')                     # get the id of the element   / default 'not_found'
            name = element.get('name', 'not found')                 # get the name of the element / default 'not_found'
            capacity = int(element.get('capacity') or 1)
            operatorsList=[]
            for operator in G.OperatorsList:                        # find the operators assigned to the operatorPool
                if id in operator.coreObjectIds:
                    operatorsList.append(operator)
#             operatorsList = element.get('operatorsList', 'not found')
            if len(operatorsList)==0:                               # if the operatorsList is empty then assign no operators
                OP = OperatorPool(element_id, name, capacity)       # create a operatorPool object
            else:
                OP = OperatorPool(element_id, name, capacity,operatorsList)     # create a operatorPool object
            OP.coreObjectIds=getSuccessorList(id)                   # update the list of objects that the operators of the operatorPool operate            
            for operator in operatorsList:
                operator.coreObjectIds=OP.coreObjectIds        		# update the list of objects that the operators operate
            G.OperatorPoolsList.append(OP)                          # add the operatorPool to the RepairmanList
    '''
    loop through all the elements    
    read the data and create them
    '''
    for (element_id, element) in nodes.iteritems():
        element = element.copy()
        element['id'] = element_id
        element.setdefault('name', element_id)

        # XXX not sure about top & left.
        for k in ('element_id', 'top', 'left'):
          element.pop(k, None)
        objClass = element.pop('_class')
        objectType=Globals.getClassFromName(objClass)    
        from CoreObject import CoreObject
        if issubclass(objectType, CoreObject):
            # remove data that has to do with wip or object interruption. CoreObjects do not need it
            inputDict=dict(element)
            if 'wip' in inputDict:
                del inputDict['wip']
            if 'failures' in inputDict:
                del inputDict['failures']
            if 'shift' in inputDict:
                del inputDict['shift']
            if 'scheduledMaintenance' in inputDict:
                del inputDict['scheduledMaintenance']
            
            # create the CoreObject
            coreObject=objectType(**inputDict)
            # update the nextIDs list of the object
            coreObject.nextIds=getSuccessorList(element['id'])           
            # (Below is only for Dismantle for now)
            # get the successorList for the 'Parts'
            coreObject.nextPartIds=getSuccessorList(element['id'], lambda source, destination, edge_data: edge_data.get('entity') == 'Part')
            # get the successorList for the 'Frames'
            coreObject.nextFrameIds=getSuccessorList(element['id'], lambda source, destination, edge_data: edge_data.get('entity') == 'Frame')
             
    # -----------------------------------------------------------------------
    #                loop through all the nodes to  
    #            search for Event Generator and create them
    #                   this is put last, since the EventGenerator 
    #                may take other objects as argument
    # -----------------------------------------------------------------------
    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
                                                                    # the key is the element_id and the second is the 
                                                                    # element itself 
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
                                                                    # with key 'id' and value the the element_id
        elementClass = element.get('_class', 'not found')           # get the class type of the element
        if elementClass=='Dream.EventGenerator':                    # check the object type
            id = element.get('id', 'not found')                     # get the id of the element   / default 'not_found'
            name = element.get('name', 'not found')                 # get the name of the element / default 'not_found'
            start = float(element.get('start') or 0)
            stop = float(element.get('stop') or -1)
                                                                    # infinity (had to be done to make it as float)
            if stop<0:
                stop=float('inf')            
            interval = float(element.get('interval') or 1)
            duration = float(element.get('duration') or 0)
            method = (element.get('method', None))                    # get the method to be run / default None
            method = method.split('.')                                  #the method is given as 'Path.MethodName'
            method=getattr(str_to_class(method[0]),method[1])           #and then parsed with getattr
            argumentDict=(element.get('argumentDict', {}))      # get the arguments of the method as a dict / default {}
               
            EV = EventGenerator(id, name, start=start, stop=stop, interval=interval, 
                                duration=duration, method=method, argumentDict=argumentDict)       # create the EventGenerator object
                                                                   
            G.EventGeneratorList.append(EV)                              
            G.ObjectInterruptionList.append(EV)
            
        elif elementClass=='Dream.CapacityStationController':                    # check the object type
            id = element.get('id', 'not found')                     # get the id of the element   / default 'not_found'
            name = element.get('name', 'not found')                 # get the name of the element / default 'not_found'
            start = float(element.get('start') or 0)
            stop = float(element.get('stop') or -1)
                                                                    # infinity (had to be done to make it as float)
            if stop<0:
                stop=float('inf')            
            interval = float(element.get('interval') or 1)
            duration = float(element.get('duration') or 0)
            dueDateThreshold = float(element.get('dueDateThreshold') or float('inf'))
            prioritizeIfCanFinish = bool(element.get('prioritizeIfCanFinish', 0))
            argumentDict=(element.get('argumentDict', {}))      # get the arguments of the method as a dict / default {}
               
            # create the CapacityStationController object
            CSC = CapacityStationController(id, name, start=start, stop=stop, interval=interval, 
                                duration=duration, argumentDict=argumentDict, dueDateThreshold=dueDateThreshold,
                                prioritizeIfCanFinish=prioritizeIfCanFinish)                                                                         
            G.EventGeneratorList.append(CSC)                              
            G.CapacityStationControllerList.append(CSC)
            G.ObjectInterruptionList.append(CSC)
            
    # -----------------------------------------------------------------------
    #                    loop through all the core objects    
    #                         to read predecessors
    # -----------------------------------------------------------------------
    for element in G.ObjList:
        #loop through all the nextIds of the object
        for nextId in element.nextIds:
            #loop through all the core objects to find the on that has the id that was read in the successorList
            for possible_successor in G.ObjList:
                if possible_successor.id==nextId:
                    possible_successor.previousIds.append(element.id)            

# ===========================================================================
#    defines the topology (predecessors and successors for all the objects)
# ===========================================================================
def setTopology():
    #loop through all the objects  
    for element in G.ObjList:
        next=[]
        previous=[]
        for j in range(len(element.previousIds)):
            for q in range(len(G.ObjList)):
                if G.ObjList[q].id==element.previousIds[j]:
                    previous.append(G.ObjList[q])
                    
        for j in range(len(element.nextIds)):
            for q in range(len(G.ObjList)):
                if G.ObjList[q].id==element.nextIds[j]:
                    next.append(G.ObjList[q])      
                             
        if element.type=="Source":
            element.defineRouting(next)
        elif element.type=="Exit":
            element.defineRouting(previous)
        #Dismantle should be changed to identify what the the successor is.
        #nextPart and nextFrame will become problematic    
        elif element.type=="Dismantle":
            nextPart=[]
            nextFrame=[]
            for j in range(len(element.nextPartIds)):
                for q in range(len(G.ObjList)):
                    if G.ObjList[q].id==element.nextPartIds[j]:
                        nextPart.append(G.ObjList[q])
            for j in range(len(element.nextFrameIds)):
                for q in range(len(G.ObjList)):
                    if G.ObjList[q].id==element.nextFrameIds[j]:
                        nextFrame.append(G.ObjList[q])
            element.defineRouting(previous, next)            
            element.definePartFrameRouting(nextPart, nextFrame)
        else:
            element.defineRouting(previous, next)
            
# ===========================================================================
#            initializes all the objects that are in the topology
# ===========================================================================
def initializeObjects():
    for element in G.ObjList + G.ObjectResourceList + G.EntityList + G.ObjectInterruptionList:
        element.initialize()

# ===========================================================================
#                        activates all the objects
# ===========================================================================
def activateObjects():
    for element in G.ObjList + G.ObjectInterruptionList:
        G.env.process(element.run())

# ===========================================================================
#                reads the WIP of the stations
# ===========================================================================
def createWIP():
    G.JobList=[]
    G.WipList=[]
    G.EntityList=[]  
    G.PartList=[]
    G.OrderComponentList=[]
    G.DesignList=[]     # list of the OrderDesigns in the system
    G.OrderList=[]
    G.MouldList=[]
    G.BatchList=[]
    G.SubBatchList=[]
    G.CapacityEntityList=[]
    G.CapacityProjectList=[]
    # entities that just finished processing in a station 
    # and have to enter the next machine 
    G.pendingEntities=[]
    
    json_data = G.JSONData
    #Read the json data
    nodes = json_data['nodes']                      # read from the dictionary the dicts with key 'nodes'
    for (element_id, element) in nodes.iteritems():
        element['id'] = element_id
        wip=element.get('wip', [])
        for entity in wip:
            entityClass=entity.get('_class', None)
            
            if entityClass=='Dream.OrderComponent':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                priority=int(entity.get('priority', '0'))
                dueDate=float(entity.get('dueDate', '0'))
                orderDate=float(entity.get('orderDate', '0'))
                componentType=entity.get('componentType', 'not found')
                isCritical=bool(int(entity.get('isCritical', '0'))) 
                readyForAssembly=bool(int(entity.get('readyForAssembly', '0'))) 
                JSONRoute=entity.get('route', [])                  # dummy variable that holds the routes of the jobs
                                                                    #    the route from the JSON file 
                                                                    #    is a sequence of dictionaries
                route = [x for x in JSONRoute]       #    copy JSONRoute
                
                # keep a reference of all extra properties passed to the job
                extraPropertyDict = {}
                for key, value in entity.items():
                  if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value
                    
                # if there is an exit assigned to the component
                #    update the corresponding local flag
                # TODO: have to talk about it with NEX
                exitAssigned=False
                for element in route:
                    elementIds = element.get('stationIdsList',[])
                    for obj in G.ObjList:
                        for elementId in elementIds:
                            if obj.id==elementId and obj.type=='Exit':
                                exitAssigned=True
                # Below it is to assign assemblers if there are any in the corresponding Global list
                if not exitAssigned:                    
                    if len(G.MouldAssemblyList)!=0:
                        bufferIDlist = []
                        assemblerIDlist = []
                        for assemblyBuffer in G.MouldAssemblyBufferList:
                            bufferIDlist.append(str(assemblyBuffer.id))
                        for assembler in G.MouldAssemblyList:
                            assemblerIDlist.append(str(assembler.id))
                        route.append({'stationIdsList':bufferIDlist})       # assign MouldAssemblyBuffers
                        route.append({'stationIdsList':assemblerIDlist})    # assign MouldAssemblies
                        # if assemblers are assigned then an 'exit' is assigned
                        exitAssigned=True
                #Below it is to assign an exit if it was not assigned in JSON and no assemblers are already assigned
                if not exitAssigned:
                    exitId=None
                    for obj in G.ObjList:
                        if obj.type=='Exit':
                            exitId=obj.id
                            break
                    if exitId:
                        route.append({'stationIdsList':[exitId],\
                                      'processingTime':{}})
                # initiate the job
                OC=OrderComponent(id, name, route, priority=priority, dueDate=dueDate,orderDate=orderDate,
                                  componentType=componentType, readyForAssembly=readyForAssembly,
                                  isCritical=isCritical, extraPropertyDict=extraPropertyDict)
                G.OrderComponentList.append(OC)
                G.JobList.append(OC)   
                G.WipList.append(OC)  
                G.EntityList.append(OC)    
            
            elif entityClass=='Dream.Mould':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                priority=int(entity.get('priority', '0'))
                dueDate=float(entity.get('dueDate', '0'))
                orderDate=float(entity.get('orderDate', '0'))
                isCritical=bool(int(entity.get('isCritical', '0'))) 
                JSONRoute=entity.get('route', [])                  # dummy variable that holds the routes of the jobs
                                                                    #    the route from the JSON file 
                                                                    #    is a sequence of dictionaries
                route = [x for x in JSONRoute]       #    copy JSONRoute
                
                # keep a reference of all extra properties passed to the job
                extraPropertyDict = {}
                for key, value in entity.items():
                  if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value

                #Below it is to assign an exit if it was not assigned in JSON
                #have to talk about it with NEX
                exitAssigned=False
                for element in route:
#                     elementId=element[0]
                    elementIds = element.get('stationIdsList',[])
                    for obj in G.ObjList:
                        for elementId in elementIds:
                            if obj.id==elementId and obj.type=='Exit':
                                exitAssigned=True 
                if not exitAssigned:
                    exitId=None
                    for obj in G.ObjList:
                        if obj.type=='Exit':
                            exitId=obj.id
                            break
                    if exitId:
#                         route.append([exitId, 0])
                        route.append({'stationIdsList':[exitId],\
                                      'processingTime':{}})
                # initiate the job
                M=Mould(id, name, route, priority=priority, dueDate=dueDate,orderDate=orderDate,
                                  isCritical=isCritical, extraPropertyDict=extraPropertyDict)
                G.MouldList.append(M)
                G.JobList.append(M)   
                G.WipList.append(M)  
                G.EntityList.append(M)
            
            elif entityClass=='Dream.Job':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                priority=int(entity.get('priority', '0'))
                dueDate=float(entity.get('dueDate', '0'))
                orderDate=float(entity.get('orderDate', '0'))
                JSONRoute=entity.get('route', [])                  # dummy variable that holds the routes of the jobs
                                                                    #    the route from the JSON file 
                                                                    #    is a sequence of dictionaries
                route = [x for x in JSONRoute]       #    copy JSONRoute
                
                # keep a reference of all extra properties passed to the job
                extraPropertyDict = {}
                for key, value in entity.items():
                  if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value

                #Below it is to assign an exit if it was not assigned in JSON
                #have to talk about it with NEX
                exitAssigned=False
                for element in route:
#                     elementId=element[0]
                    elementIds = element.get('stationIdsList',[])
                    for obj in G.ObjList:
                        for elementId in elementIds:
                            if obj.id==elementId and obj.type=='Exit':
                                exitAssigned=True 
                if not exitAssigned:
                    exitId=None
                    for obj in G.ObjList:
                        if obj.type=='Exit':
                            exitId=obj.id
                            break
                    if exitId:
#                         route.append([exitId, 0])
                        route.append({'stationIdsList':[exitId],\
                                      'processingTime':{}})
                # initiate the job
                J=Job(id, name, route, priority=priority, dueDate=dueDate,
                    orderDate=orderDate, extraPropertyDict=extraPropertyDict)
                G.JobList.append(J)   
                G.WipList.append(J)  
                G.EntityList.append(J) 
            
            
            elif entityClass=='Dream.Part':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                P=Part(id,name)
                G.PartList.append(P)   
                G.WipList.append(P)  
                G.EntityList.append(P)  
                object=Globals.findObjectById(element['id'])
                P.remainingProcessingTime=entity.get('remainingProcessingTime', {})
                P.currentStation=object

            elif entityClass=='Dream.Batch':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                numberOfUnits=int(entity.get('numberOfUnits', '4'))
                B=Batch(id,name, numberOfUnits)
                G.BatchList.append(B)   
                G.WipList.append(B)  
                G.EntityList.append(B)  
                object=Globals.findObjectById(element['id'])
                B.unitsToProcess=int(entity.get('unitsToProcess', numberOfUnits))
                B.remainingProcessingTime=entity.get('remainingProcessingTime', {})
                B.currentStation=object
                
            elif entityClass=='Dream.SubBatch':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                numberOfUnits=int(entity.get('numberOfUnits', '4'))
                parentBatchId=entity.get('parentBatchId', 'not found')
                parentBatchName=entity.get('parentBatchName', 'not found')
            
                # check if the parent batch is already created. If not, then create it
                batch=None
                for b in G.BatchList:
                    if b.id==parentBatchId:
                        batch=b
                if batch:               #if the parent batch was found add the number of units of current sub-batch
                    batch.numberOfUnits+=numberOfUnits
                else:     #if the parent batch was not found create it
                    batch=Batch(parentBatchId,parentBatchName, numberOfUnits)
                    G.BatchList.append(batch)   
                    G.WipList.append(batch)  
                    G.EntityList.append(batch)               
                           
                SB=SubBatch(id,name, numberOfUnits=numberOfUnits, parentBatch=batch)
                G.SubBatchList.append(SB)   
                G.WipList.append(SB)  
                G.EntityList.append(SB)  
                object=Globals.findObjectById(element['id'])
                SB.unitsToProcess=int(entity.get('unitsToProcess', numberOfUnits))
                SB.remainingProcessingTime=entity.get('remainingProcessingTime', {})
                SB.currentStation=object

            if entityClass=='Dream.Order':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                priority=int(entity.get('priority', '0'))
                dueDate=float(entity.get('dueDate', '0'))
                orderDate=float(entity.get('orderDate', '0'))
                isCritical=bool(int(entity.get('isCritical', '0')))  
                basicsEnded=bool(int(entity.get('basicsEnded', '0'))) 
                componentsReadyForAssembly = bool((entity.get('componentsReadyForAssembly', '0')))
                # read the manager ID
                manager=entity.get('manager', None)
                # if a manager ID is assigned then search for the operator with the corresponding ID
                # and assign it as the manager of the order 
                if manager:
                    for operator in G.OperatorsList:
                        if manager==operator.id:
                            manager=operator
                            break
                componentsList=entity.get('componentsList', {})
                JSONRoute=entity.get('route', [])                  # dummy variable that holds the routes of the jobs
                                                                    #    the route from the JSON file 
                                                                    #    is a sequence of dictionaries
                route = [x for x in JSONRoute]       #    copy JSONRoute
                
                # keep a reference of all extra properties passed to the job
                extraPropertyDict = {}
                for key, value in entity.items():
                  if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value

                #Below it is to assign an order decomposition if it was not assigned in JSON
                #have to talk about it with NEX
                odAssigned=False
                for element in route:
#                     elementId=element[0]
                    elementIds = element.get('stationIdsList',[])
                    for obj in G.ObjList:
                        for elementId in elementIds:
                            if obj.id==elementId and obj.type=='OrderDecomposition':
                                odAssigned=True 
                if not odAssigned:
                    odId=None
                    for obj in G.ObjList:
                        if obj.type=='OrderDecomposition':
                            odId=obj.id
                            break
                    if odId:
#                         route.append([odId, 0])
                        route.append({'stationIdsList':[odId],\
                                      'processingTime':\
                                            {'distributionType':'Fixed',\
                                             'mean':'0'}})
                # XXX durty way to implement new approach were the order is abstract and does not run through the system 
                # but the OrderDesign does
                # XXX initiate the Order and the OrderDesign
                O=Order('G'+id, 'general '+name, route=[], priority=priority, dueDate=dueDate,orderDate=orderDate,
                        isCritical=isCritical, basicsEnded=basicsEnded, manager=manager, componentsList=componentsList,
                        componentsReadyForAssembly=componentsReadyForAssembly, extraPropertyDict=extraPropertyDict)
                # create the OrderDesign
                OD=OrderDesign(id, name, route, priority=priority, dueDate=dueDate,orderDate=orderDate,
                        isCritical=isCritical, order=O, extraPropertyDict=extraPropertyDict)
                # add the order to the OrderList
                G.OrderList.append(O)
                # add the OrderDesign to the DesignList and the OrderComponentList
                G.OrderComponentList.append(OD)
                G.DesignList.append(OD)
                G.WipList.append(OD)  
                G.EntityList.append(OD)
                G.JobList.append(OD)
            
            if entityClass=='Dream.CapacityProject':
                id=entity.get('id', 'not found')  
                name=entity.get('name', 'not found') 
                capacityRequirementDict=entity.get('capacityRequirementDict', {})
                earliestStartDict=entity.get('earliestStartDict', {})
                dueDate=float(entity.get('dueDate', 0))
                assemblySpaceRequirement=float(entity.get('assemblySpaceRequirement', 0))
                
                CP=CapacityProject(id=id, name=name, capacityRequirementDict=capacityRequirementDict, 
                                        earliestStartDict=earliestStartDict, dueDate=dueDate,
                                        assemblySpaceRequirement=assemblySpaceRequirement) 
                G.EntityList.append(CP)     
                G.CapacityProjectList.append(CP)
                         
            if entityClass=='Dream.CapacityEntity':
                id=entity.get('id', 'not found')  
                name=entity.get('name', 'not found') 
                requiredCapacity=entity.get('requiredCapacity', 10)
                capacityProjectId=entity.get('capacityProjectId', None)
                CE=CapacityEntity(id=id, name=name, requiredCapacity=requiredCapacity, capacityProjectId=capacityProjectId) 
                G.CapacityEntityList.append(CE)     
                G.EntityList.append(CE)    
                object=Globals.findObjectById(element['id'])
                CE.currentStation=object
                
# ===========================================================================
#                reads the interruptions of the stations
# ===========================================================================
def createObjectInterruptions():
    G.ScheduledMaintenanceList=[]
    G.FailureList=[]
    G.ShiftSchedulerList=[]
    
    json_data = G.JSONData
    #Read the json data
    nodes = json_data['nodes']                      # read from the dictionary the dicts with key 'nodes'
    # for the elements in the nodes dict
    for (element_id, element) in nodes.iteritems():
        element['id'] = element_id
        scheduledMaintenance=element.get('scheduledMaintenance', {})
        # if there is a scheduled maintenance initiate it and append it
        # to the interruptions- and scheduled maintenances- list
        if len(scheduledMaintenance):
            start=float(scheduledMaintenance.get('start', 0))
            duration=float(scheduledMaintenance.get('duration', 1))
            victim=Globals.findObjectById(element['id'])
            SM=ScheduledMaintenance(victim=victim, start=start, duration=duration)
            victim.objectInterruptions.append(SM)
            G.ObjectInterruptionList.append(SM)
            G.ScheduledMaintenanceList.append(SM)
        failure=element.get('failures', None)
        # if there are failures assigned 
        # initiate them   
        if failure:
            distributionType=failure.get('distributionType', 'No')
            if distributionType=='No':
                pass
            else:
                victim=Globals.findObjectById(element['id'])
                deteriorationType=failure.get('deteriorationType', 'constant')
                F=Failure(victim, distribution=failure, repairman=victim.repairman, deteriorationType=deteriorationType)
                victim.objectInterruptions.append(F)
                G.ObjectInterruptionList.append(F)
                G.FailureList.append(F)
        # if there is a shift pattern defined 
        # initiate them             
        shift=element.get('shift', {})
        if len(shift):
            victim=Globals.findObjectById(element['id'])
            shiftPattern=list(shift.get('shiftPattern', []))
            # patch to correct if input has end of shift at the same time of start of next shift
            # TODO check if the backend should be able to handle this
            for index, element in enumerate(shiftPattern):
                if element is shiftPattern[-1]:
                    break
                next = shiftPattern[index + 1]
                if element[1]==next[0]:
                    element[1]=next[1]
                    shiftPattern.remove(next)
            endUnfinished=bool(int(shift.get('endUnfinished', 0)))
            receiveBeforeEndThreshold=float(shift.get('receiveBeforeEndThreshold', 0))
            SS=ShiftScheduler(victim, shiftPattern=shiftPattern, endUnfinished=endUnfinished, 
                              receiveBeforeEndThreshold=receiveBeforeEndThreshold)
            victim.objectInterruptions.append(SS)
            G.ObjectInterruptionList.append(SS)
            G.ShiftSchedulerList.append(SS)
                
# ===========================================================================
#        used to convert a string read from the input to object type
# ===========================================================================
def str_to_class(str):
    str = str.replace("Dream.", "") # XXX temporary.
    # actuall this method can be dropped in favor of getClassFromName
    return getattr(sys.modules[__name__], str)

# ===========================================================================
#                        the main script that is ran
# ===========================================================================
def main(argv=[], input_data=None):
    argv = argv or sys.argv[1:]
    
    #create an empty list to store all the objects in   
    G.ObjList=[]

    if input_data is None:
      # user passes the topology filename as first argument to the program
      filename = argv[0]
      try:                                          # try to open the file with the inputs
          G.JSONFile=open(filename, "r")            # global variable holding the file to be opened
      except IOError:                               
          print "%s could not be open" % filename
          return "ERROR"
      G.InputData=G.JSONFile.read()                 # pass the contents of the input file to the global var InputData
    else:
      G.InputData = input_data
    start=time.time()                               # start counting execution time 

    #read the input from the JSON file and create the line
    G.JSONData=json.loads(G.InputData)              # create the dictionary JSONData
    readGeneralInput()
    createObjects()
    createObjectInterruptions()
    setTopology()

    #run the experiment (replications)          
    for i in xrange(G.numberOfReplications):
        G.env=simpy.Environment()                       # initialize the environment
        G.maxSimTime=float(G.JSONData['general'].get('maxSimTime', '100'))     # read the maxSimTime in each replication 
                                                                               # since it may be changed for infinite ones
        if G.Router:
            G.Router.isActivated=False
            G.Router.isInitialized=False
        
        if G.seed:
          G.Rnd=Random('%s%s' % (G.seed, i))
        else:
          G.Rnd=Random()
        createWIP()
        initializeObjects()
        Globals.setWIP(G.EntityList)        
        activateObjects()
        
        # if the simulation is ran until no more events are scheduled, 
        # then we have to find the end time as the time the last entity ended.
        if G.maxSimTime==-1:
            # If someone does it for a model that has always events, then it will run forever!
            G.env.run(until=float('inf'))
                                         
            # identify from the exits what is the time that the last entity has ended. 
            endList=[]
            for exit in G.ExitList:
                endList.append(exit.timeLastEntityLeft)
  
            # identify the time of the last event
            if float(max(endList))!=0 and G.env.now==float('inf'):    #do not let G.maxSimTime=0 so that there will be no crash
                G.maxSimTime=float(max(endList))
            else:
                print "simulation ran for 0 time, something may have gone wrong"
                logger.info("simulation ran for 0 time, something may have gone wrong")
        #else we simulate until the given maxSimTime
        else:
            G.env.run(until=G.maxSimTime)
        
        #carry on the post processing operations for every object in the topology       
        for element in G.ObjList:
            element.postProcessing()
            
        #carry on the post processing operations for every model resource in the topology       
        for model_resource in G.ObjectResourceList:
            model_resource.postProcessing()
            
        # added for debugging, print the Route of the Jobs on the same G.traceFile
        PrintRoute.outputRoute()
            
        #output trace to excel      
        if(G.trace=="Yes"):
            ExcelHandler.outputTrace('trace'+str(i))  
            ExcelHandler.resetTrace()
    
    G.outputJSONFile=open('outputJSON.json', mode='w')
    G.outputJSON['_class'] = 'Dream.Simulation';
    G.outputJSON['general'] ={};
    G.outputJSON['general']['_class'] = 'Dream.Configuration';
    G.outputJSON['general']['totalExecutionTime'] = (time.time()-start);
    G.outputJSON['elementList'] =[];
    
    #output data to JSON for every object in the topology         
    for element in G.ObjList:
        element.outputResultsJSON()
        
    #output data to JSON for every resource in the topology         
    for model_resource in G.ObjectResourceList:
        model_resource.outputResultsJSON()
        
    for job in G.JobList:
        job.outputResultsJSON()
        
    for capacityProject in G.CapacityProjectList:
        capacityProject.outputResultsJSON()
         
    outputJSONString=json.dumps(G.outputJSON, indent=True)
    G.outputJSONFile.write(outputJSONString)

    #logger.info("execution time="+str(time.time()-start))
    if input_data:
      return outputJSONString

    # Output on stdout
    print outputJSONString
    
if __name__ == '__main__':
#     cProfile.run('main()')
    main()

