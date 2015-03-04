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
import simpy
from dream.simulation.Globals import G 
from dream.simulation.Order import Order
from dream.simulation.OrderDesign import OrderDesign
from dream.simulation.Mould import Mould
import dream.simulation.PrintRoute as PrintRoute
import dream.simulation.ExcelHandler as ExcelHandler
import time
import json
from random import Random
import sys
import os.path
import dream.simulation.Globals as Globals
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
#                       creates first the object interruptions 
#                            and then the core objects
# ===========================================================================
def createObjectResourcesAndCoreObjects():

    json_data = G.JSONData
    #Read the json data
    # nodes = json_data['nodes']                      # read from the dictionary the dicts with key 'nodes'
    nodes = json_data['graph']["node"]                      # read from the dictionary the dicts with key 'nodes'
    edges = json_data['graph']["edge"]                      # read from the dictionary the dicts with key 'edges'


    '''
    getSuccesorList method to get the successor 
    list of object with ID = id
    XXX slow implementation
    '''
    def getSuccessorList(node_id, predicate=lambda source, destination, edge_class, edge_data: True):
      successor_list = []                           # dummy variable that holds the list to be returned
      
      for edge in edges.values():
          source = edge["source"]
          destination = edge["destination"]
          edge_class = edge["_class"]
          edge_data = edge.get("data", {})
          if source == node_id:                               # for the node_id argument
              if predicate(source, destination, edge_class, edge_data):     # find its 'destinations' and 
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
    G.AllocationManagementList=[]
    G.CapacityStationList=[]
    G.CapacityStationExitList=[]
    G.CapacityStationControllerList=[]

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
        
        objectType=Globals.getClassFromName(resourceClass)    
        from dream.simulation.ObjectResource import ObjectResource     # operator pools to be created later since they use operators
                                                      # ToDo maybe it is semantically diferent object  
        if issubclass(objectType, ObjectResource) and not resourceClass=='Dream.OperatorPool':
            inputDict=dict(element)
            # create the CoreObject
            objectResource=objectType(**inputDict)
            objectResource.coreObjectIds=getSuccessorList(element['id'])    

    '''
    loop through all the model resources 
    search for operatorPools in order to create them
    read the data and create them
    '''
    from dream.simulation.OperatorPool import OperatorPool
    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
                                                                    # the key is the element_id and the second is the 
                                                                    # element itself 
        element = element.copy()
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
        for k in ('element_id', 'top', 'left'):
          element.pop(k, None)
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
  
        from dream.simulation.CoreObject import CoreObject
        if issubclass(objectType, CoreObject):
            # remove data that has to do with wip or object interruption. CoreObjects do not need it
            inputDict=dict(element)           
            # create the CoreObject
            coreObject=objectType(**inputDict)
            # update the nextIDs list of the object
            coreObject.nextIds=getSuccessorList(element['id'])           
            # (Below is only for Dismantle for now)
            # get the successorList for the 'Parts'
            coreObject.nextPartIds=getSuccessorList(element['id'], lambda source, destination, edge_class, edge_data: edge_data.get('entity',{}) == 'Part')
            # get the successorList for the 'Frames'
            coreObject.nextFrameIds=getSuccessorList(element['id'], lambda source, destination, edge_class, edge_data: edge_data.get('entity',{}) == 'Frame')
            
    #                    loop through all the core objects    
    #                         to read predecessors
    for element in G.ObjList:
        #loop through all the nextIds of the object
        for nextId in element.nextIds:
            #loop through all the core objects to find the on that has the id that was read in the successorList
            for possible_successor in G.ObjList:
                if possible_successor.id==nextId:
                    possible_successor.previousIds.append(element.id)            

# ===========================================================================
#                creates the object interruptions
# ===========================================================================
def createObjectInterruptions():
    G.ObjectInterruptionList=[]
    G.ScheduledMaintenanceList=[]
    G.FailureList=[]
    G.ShiftSchedulerList=[]
    G.EventGeneratorList=[]
    G.CapacityStationControllerList=[]
    G.PeriodicMaintenanceList=[]
    json_data = G.JSONData
    #Read the json data
    nodes = json_data['graph']["node"]                      # read from the dictionary the dicts with key 'nodes'
    
    #                loop through all the nodes to  
    #            search for Event Generator and create them
    #                   this is put last, since the EventGenerator 
    #                may take other objects as argument
    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
                                                                    # the key is the element_id and the second is the 
                                                                    # element itself 
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
                                                                    # with key 'id' and value the the element_id
        objClass = element.get('_class', 'not found')           # get the class type of the element
        from dream.simulation.ObjectInterruption import ObjectInterruption
        objClass = element.pop('_class')
        objectType=Globals.getClassFromName(objClass)    
        # from CoreObject import CoreObject
        # if issubclass(objectType, CoreObject):
    
        if issubclass(objectType,ObjectInterruption):   # check the object type
            inputDict=dict(element)        
            # create the ObjectInterruption
            objectInterruption=objectType(**inputDict)
            G.ObjectInterruptionList.append(objectInterruption)
    
    # search inside the nodes for encapsulated ObjectInterruptions (failures etc)
    # ToDo this will be cleaned a lot if we update the JSON notation:
    # define ObjectInterruption echelon inside node
    # define interruptions' distribution better
    from dream.simulation.ScheduledMaintenance import ScheduledMaintenance    
    from dream.simulation.Failure import Failure
    from dream.simulation.PeriodicMaintenance import PeriodicMaintenance    
    from dream.simulation.ShiftScheduler import ShiftScheduler
    for (element_id, element) in nodes.iteritems():
        element['id'] = element_id
        scheduledMaintenance=element.get('interruptions',{}).get('scheduledMaintenance', {})
        # if there is a scheduled maintenance initiate it and append it
        # to the interruptions- and scheduled maintenances- list
        if len(scheduledMaintenance):
            start=float(scheduledMaintenance.get('start', 0))
            duration=float(scheduledMaintenance.get('duration', 1))
            victim=Globals.findObjectById(element['id'])
            SM=ScheduledMaintenance(victim=victim, start=start, duration=duration)
            G.ObjectInterruptionList.append(SM)
            G.ScheduledMaintenanceList.append(SM)
        failure=element.get('interruptions',{}).get('failure', None)
        # if there are failures assigned 
        # initiate them   
        if failure:
            victim=Globals.findObjectById(element['id'])
            deteriorationType=failure.get('deteriorationType', 'constant')
            waitOnTie=failure.get('waitOnTie', False)
            F=Failure(victim=victim, distribution=failure, repairman=victim.repairman, deteriorationType=deteriorationType,
                      waitOnTie=waitOnTie)
            G.ObjectInterruptionList.append(F)
            G.FailureList.append(F)
        # if there are periodic maintenances assigned 
        # initiate them   
        periodicMaintenance=element.get('interruptions',{}).get('periodicMaintenance', None)
        if periodicMaintenance:
            distributionType=periodicMaintenance.get('distributionType', 'No')
            victim=Globals.findObjectById(element['id'])
            PM=PeriodicMaintenance(victim=victim, distribution=periodicMaintenance, repairman=victim.repairman)
            G.ObjectInterruptionList.append(PM)
            G.PeriodicMaintenanceList.append(PM)
        # if there is a shift pattern defined 
        # initiate them             
        shift=element.get('interruptions',{}).get('shift', {})
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
            thresholdTimeIsOnShift=bool(int(shift.get('thresholdTimeIsOnShift', 1)))
            SS=ShiftScheduler(victim=victim, shiftPattern=shiftPattern, endUnfinished=endUnfinished, 
                              receiveBeforeEndThreshold=receiveBeforeEndThreshold,
                              thresholdTimeIsOnShift=thresholdTimeIsOnShift)
            G.ObjectInterruptionList.append(SS)
            G.ShiftSchedulerList.append(SS)


# ===========================================================================
#                       creates the entities that are wip
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
    #Read the json data
    json_data = G.JSONData
    # read from the dictionary the dicts with key 'BOM' (if there are any)
    input=json_data.get('input',{})
    bom=input.get('BOM',None)
    if bom:
        orders=bom.get('productionOrders',[])
        # for every order in the productionOrders list
        for prodOrder in orders:
            orderClass=prodOrder.get('_class',None)
            orderType=Globals.getClassFromName(orderClass)
            # make sure that their type is Dream.Order
            if orderClass=='Dream.Order':
                id=prodOrder.get('id', 'not found')
                name=prodOrder.get('name', 'not found')
                priority=int(prodOrder.get('priority', '0'))
                dueDate=float(prodOrder.get('dueDate', '0'))
                orderDate=float(prodOrder.get('orderDate', '0'))
                isCritical=bool(int(prodOrder.get('isCritical', '0')))  
                componentsReadyForAssembly = bool((prodOrder.get('componentsReadyForAssembly', False)))
                componentsList=prodOrder.get('componentsList', {})
                # keep a reference of all extra properties passed to the job
                extraPropertyDict = {}
                for key, value in prodOrder.items():
                  if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value
                # initiate the Order
                O=Order('G'+id, 'general '+name, route=[], priority=priority, dueDate=dueDate,orderDate=orderDate,
                        isCritical=isCritical, componentsList=componentsList,
                        componentsReadyForAssembly=componentsReadyForAssembly, extraPropertyDict=extraPropertyDict)
                G.OrderList.append(O)
            else:
                productionOrderClass=prodOrder.get('_class', None)
                productionOrderType=Globals.getClassFromName(productionOrderClass)
                inputDict=dict(prodOrder)
                inputDict.pop('_class')
                from dream.simulation.Entity import Entity
                if issubclass(productionOrderType, Entity):
                    entity=productionOrderType(**inputDict)
                    G.EntityList.append(entity)                   
                
    # read from the dictionary the dicts with key 'nodes'
    nodes = json_data["graph"]['node']
    for (element_id, element) in nodes.iteritems():
        element['id'] = element_id
        wip=element.get('wip', [])
        from dream.simulation.OrderDesign import OrderDesign
        for entity in wip:
            # if there is BOM defined
            if bom:
                # and production orders in it
                if bom.get('productionOrders',[]):
                    # find which order has the entity in its componentsList
                    for order in G.OrderList:
                        if order.componentsList:
                            for componentDict in order.componentsList:
                                # if the entity has no parent order the following control will not be performed
                                if entity['id']==componentDict['id']:
                                    entityCurrentSeq=int(entity['sequence'])# the current seq number of the entity's  route
                                    entityRemainingProcessingTime=entity.get('remainingProcessingTime',{})
                                    entityRemainingSetupTime=entity.get('remainingSetupTime',{})
                                    ind=0               # holder of the route index corresponding to the entityCurrentSeq
                                    solution=False      # flag to signal that the route step is found
                                    # find the step that corresponds to the entityCurrentSeq
                                    for i, step in enumerate(componentDict.get('route',[])):
                                        stepSeq=step['sequence']        # the sequence of step i
                                        if stepSeq=='':
                                            stepSeq=0                   # if the seq is ''>OrderDecomposition then 0
                                        # if the entityCurrentSeq is found and the id of the holding Station is in the steps stationIdsList
                                        if int(stepSeq)==int(entityCurrentSeq) and element['id'] in step['stationIdsList']:
                                            ind=i                       # hold the index 
                                            solution=True               # the solution isfound
                                            break
                                    # assert that there is solution
                                    assert solution, 'something is wrong with the initial step of '+entity['id']
                                    # the remaining route of the entity assuming that the given route doesn't start from the entityCurrentSeq
                                    entityRoute=componentDict.get('route',[])[ind:]
                                    entity=dict(componentDict)          # copy the entity dict
                                    entity.pop('route')                 # remove the old route
                                    entity['route']=entityRoute         # and hold the new one without the previous steps
                                    entity['order']=order.id
                                    entity['remainingProcessingTime']=entityRemainingProcessingTime
                                    entity['remainingSetupTime']=entityRemainingSetupTime
                                    break
            
            entityClass=entity.get('_class', None)
            entityType=Globals.getClassFromName(entityClass)
            inputDict=dict(entity)
            inputDict.pop('_class')
            from dream.simulation.Entity import Entity
            if issubclass(entityType, Entity) and (not entityClass=='Dream.Order'):
                # if orders are provided separately (BOM) provide the parent order as argument  
                if entity.get('order',None):
                    entityOrder=Globals.findObjectById(entity['order'])
                    inputDict.pop('order')
                    entity=entityType(order=entityOrder,**inputDict)
                    entity.routeInBOM=True
                else:
                    entity=entityType(**inputDict)
                G.EntityList.append(entity)
                object=Globals.findObjectById(element['id'])
                entity.currentStation=object
                
            # ToDo order is to defined in a new way
            if entityClass=='Dream.Order':
                id=entity.get('id', 'not found')
                name=entity.get('name', 'not found')
                priority=int(entity.get('priority', '0'))
                dueDate=float(entity.get('dueDate', '0'))
                orderDate=float(entity.get('orderDate', '0'))
                isCritical=bool(int(entity.get('isCritical', '0')))  
                basicsEnded=bool(int(entity.get('basicsEnded', '0'))) 
                componentsReadyForAssembly = bool((entity.get('componentsReadyForAssembly', False)))
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
                # XXX dirty way to implement new approach were the order is abstract and does not run through the system 
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
    for element in G.ObjList + G.ObjectResourceList + G.EntityList + G.ObjectInterruptionList+G.RouterList:
        element.initialize()

# ===========================================================================
#                        activates all the objects
# ===========================================================================
def activateObjects():
    for element in G.ObjectInterruptionList:
        G.env.process(element.run())       
    for element in G.ObjList:
        G.env.process(element.run())                                             

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
    createObjectResourcesAndCoreObjects()
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
            G.numpyRnd.random.seed(G.seed)
        else:
            G.Rnd=Random()
            G.numpyRnd.random.seed()
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
        for element in G.ObjList+G.ObjectResourceList+G.RouterList:
            element.postProcessing()
                       
        # added for debugging, print the Route of the Jobs on the same G.traceFile
        PrintRoute.outputRoute()
            
        #output trace to excel      
        if(G.trace=="Yes"):
            ExcelHandler.outputTrace('trace'+str(i))  
            import StringIO
            traceStringIO = StringIO.StringIO()
            G.traceFile.save(traceStringIO)
            encodedTrace=traceStringIO.getvalue().encode('base64')
            ExcelHandler.resetTrace()
    
    G.outputJSON['_class'] = 'Dream.Simulation';
    G.outputJSON['general'] ={};
    G.outputJSON['general']['_class'] = 'Dream.Configuration';
    G.outputJSON['general']['totalExecutionTime'] = (time.time()-start);
    G.outputJSON['elementList'] =[];
    
        
    #output data to JSON for every object in the topology         
    for object in G.ObjectResourceList + G.EntityList + G.ObjList+G.RouterList:
        object.outputResultsJSON()
        
    # output the trace as encoded if it is set on
    if G.trace=="Yes":
        # XXX discuss names on this
        jsonTRACE = {'_class': 'Dream.Simulation',
                'id': 'TraceFile',
                'results': {'trace':encodedTrace}
            }
        G.outputJSON['elementList'].append(jsonTRACE)
        
        
    outputJSONString=json.dumps(G.outputJSON, indent=True)
    if 0:
      G.outputJSONFile=open('outputJSON.json', mode='w')
      G.outputJSONFile.write(outputJSONString)

    if not input_data:
      # Output on stdout
      print outputJSONString
      # XXX I am not sure we still need this case
      return

    # XXX result_list is not needed here, we could replace result by result_list
    G.JSONData['result'] = {'result_list': [G.outputJSON]}
    #logger.info("execution time="+str(time.time()-start))

    return json.dumps(G.JSONData, indent=True)


if __name__ == '__main__':
#     cProfile.run('main()')
    main()
