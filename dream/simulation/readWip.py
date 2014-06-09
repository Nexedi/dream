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
from BatchScrapMachine import BatchScrapMachine
from LineClearance import LineClearance
from EventGenerator import EventGenerator
from Operator import Operator
from OperatorPreemptive import OperatorPreemptive
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
from Mould import Mould
from OrderDecomposition import OrderDecomposition
from ConditionalBuffer import ConditionalBuffer
from MouldAssemblyBuffer import MouldAssemblyBuffer
from MachineManagedJob import MachineManagedJob
from QueueManagedJob import QueueManagedJob
from ShiftScheduler import ShiftScheduler

import ExcelHandler
import time
import json
from random import Random
import sys
import os.path
import Globals
import ast


def checkWIP():
    '''checks if there is WIP given, if there is no WIP given returns False'''
    json_data = G.JSONData
    totalWip=[]
    #Read the json data
    nodes = json_data['nodes']                      # read from the dictionary the dicts with key 'nodes'
    for (element_id, element) in nodes.iteritems():
        wip=element.get('wip', [])
        totalWip.append(wip)
    return len(totalWip)>0


class WIPreadError(Exception):
    """Exception raised for errors in the WIP.
    """
    def __init__(self, msg):
        Exception.__init__(self, msg) 

def getOrders():
    ''' run the method from KEtool to read the orders'''
    ''' dict={
            'orders':[{ 'orderName':'name1',
                        'orderID':'ID1',
                        'manager':'manager1',
                        'orderDate':'orderDate1',
                        'dueDate':'dueDate1',
                        'componentsList':[  {'componentName':'componenet1order1',
                                             'componentID':'C1O1',
                                             'route':[{'technology':'CAD',
                                                       'sequence':'1',
                                                       'processingTime':{'distribution':'Fixed',
                                                                         'mean':'1'}
                                                       },
                                                      {'technology':'MOULDINJECTION',
                                                       'sequence':'?',
                                                       'numberOfParts':'200',
                                                       'processingTime':{'distribution':'Fixed',
                                                                         'mean':'2'}
                                                       }
                                                     ]
                                            },
                                            {'componentName':'component2order1',
                                             'componentID':'C2O1',
                                             'route':[{'technology':'CAM',
                                                       'sequence':'1',
                                                       'processingTime':{'distribution':'Fixed',
                                                                         'mean':'1'}
                                                       },
                                                      {'technology':'MILL',
                                                       'sequence':'2',
                                                       'processingTime':{'distribution':'Fixed',
                                                                         'mean':'1'}
                                                       }
                                                     ]
                                            }
                                         ]
                       },
                      { 'orderName':'name2',
                        'ordeerID':'ID1',
                        'manager':'manager1',
                        'orderDate':'orderDate2':
                        'dueDate':'dueDate2',
                        'componentsList':[  {'componentName':'component1order2',
                                             'componentID':'C1O2',
                                             'route':[]},
                                            {'componentName':'component1order2',
                                             'componentID':'C1O2',
                                             'route':[]}
                                         ]
                       }
                    ],
            'WIP':{'CAM1':[C102],
                   'CAM2':[],
                   'EDM':[C103],
                   'MILL1':[C203],
                   'MILL2':[],
                   'ASS1':[],
                   'ASS2':[],
                   'ASS3':[],
                   'IM':[]
                   }
            }
    WHAT HAPPENS WITH STATIONS THAT ARE IN WIP BUT NOT IN STATIONS BUT QUEUED,
    PANOS I WILL INFORMATION ON THEIR CURRENT STATE
    '''   
    # request the WIP json file
    input_data=requestJSON()
    
    if input_data is None:
        raise WIPreadError('There are no Orders to be read')# pass the contents of the input file to the global var InputData
    else:
      G.inputWIP = input_data

    #read the input from the JSON file and create the line
    G.wip_Data=json.loads(G.inputWIP)              # create the dictionary wip_Data
    
    G.OrderList=[]
    
    json_data = G.wip_Data
    # find the IDs of the entities that are in the wip list and should be created
    getWipID()
    
    #Read the json data
    orders = json_data['orders']                                    # read from the dictionary the list with key 'orders'
    # each order is a dictionary
    for orderDict in orders:
        id=orderDict.get('id', 'not found')
        name=orderDict.get('name', 'not found')
        priority=int(orderDict.get('priority', '0'))
        dueDate=float(orderDict.get('dueDate', '0'))
        orderDate=float(orderDict.get('orderDate', '0'))
        isCritical=bool(int(orderDict.get('isCritical', '0')))
        basicsEnded=bool(int(orderDict.get('basicsEnded', '0')))
        componentsReadyForAssembly=bool((orderDict.get('componentsReadyForAssembly', '0')))
        manager=orderDict.get('manager', None)                          # read the manager ID
        # if a manager ID is assigned then search for the operator with the corresponding ID
        # and assign it as the manager of the order 
        if manager:
            for operator in G.OperatorsList:
                if manager==operator.id:
                    manager=operator
                    break
        # keep a reference of all extra properties passed to the job
        extraPropertyDict = {}
        for key, value in orderDict.items():
            if key not in ('_class', 'id'):
                extraPropertyDict[key] = value
        # initiate the Order (the order has no route any more)
        O=Order(id, name, priority=priority, dueDate=dueDate,orderDate=orderDate,
                isCritical=isCritical, basicsEnded=basicsEnded, manager=manager, componentsList=[],
                componentsReadyForAssembly=componentsReadyForAssembly, extraPropertyDict=extraPropertyDict)
        G.OrderList.append(O)
        # call the method that finds the components of each order and initiates them 
        getComponets(orderDict,O)

        
def getMachineNameSet(technology):
    """
    Give list of machines given a particular step name. For example
    if step_name is "CAM", it will return ["CAM1", "CAM2"]
    """
    from Globals import G
    machine_name_set = set()
    for machine_name in G.MachineList:
        if machine_name.startswith(technology):
            machine_name_set.add(machine_name)
    return machine_name_set

MACHINE_TYPE_SET = set(["Dream.MachineManagedJob", "Dream.MouldAssembly"])
def getNotMachineNodePredecessorList(technology):
    """
    Give the list of all predecessors that are not of type machine
    For example, for technology "CAM", it may return "QCAM"
    """
    predecessor_list = []
    machine_name_set = getMachineNameSet(technology)
    from Globals import G
    for edge in G.JSONdata["edges"].values():
        if edge[1] in machine_name_set:
            predecessor_step = edge[0]
            if predecessor_step in predecessor_list:
                continue
            if not G.JSONdata["nodes"][predecessor_step]["_class"] in MACHINE_TYPE_SET:
                predecessor_list = [predecessor_step] + predecessor_list
                predecessor_list = [x for x in getNotMachineNodePredecessorList(predecessor_step) \
                                    if x not in predecessor_list] + predecessor_list
    return predecessor_list

def getNotMachineNodeSuccessorList(technology):
    """
    Give the list of all successors that are not of type machine
    For example, for technology "CAM", it may return "Decomposition"
                 for technology "INJM-MAN" or "INJM" it may return "Exit"
    """
    successor_list = []
    machine_name_set = getMachineNameSet(technology)
    from Globals import G
    for edge in G.JSONdata["edges"].values():
        if edge[0] in machine_name_set:
            successor_step = edge[1]
            if successor_step in successor_list:
                continue
            if not G.JSONdata["nodes"][successor_step]["_class"] in MACHINE_TYPE_SET:
                successor_list = [successor_step] + successor_list
                successor_list = [x for x in getNotMachineNodePredecessorList(successor_step) \
                                    if x not in successor_list] + successor_list
    return successor_list
        
def getRouteList(steps_list):
    # step_list is a list of tuples (technology, sequence, processing_time, parts_needed)
    # use to record which predecessor has been already done, used to avoid doing
    # two times Decomposition
    technology_list=[]
    step_sequence_list=[]
    processing_time_list=[]
    prerequisite_list=[]
    for step in steps_list:
        technology_list.append(steps_list[step][0])
        step_sequence_list.append(steps_list[step][1])
        processing_time_list.append(steps_list[step][2])
        prerequisite_list.append(steps_list[step][3])
    predecessor_set = set()
    successor_set = set()
    route_list = []
    setup_step=None             # a step that is of type SETUP
    next_step=None        # the next step of the last SETUP step
    for j, sequence_step in enumerate(technology_list):
        #=======================================================================
        #             check whether the current step is SETUP-step
        #=======================================================================
        # if so, keep the step and append the processing time to the following step of the sequence
        if sequence_step.endswith('SET'):
            setup_step=(sequence_step,step_sequence_list[j],processing_time_list[j],prerequisite_list[j])
            next_step=step_sequence_list[j+1]
            continue
        #=======================================================================
        #                         append the predecessors
        #=======================================================================
        for predecessor_step in getNotMachineNodePredecessorList(sequence_step):
            # before the QCAM must an order decomposition come
            if predecessor_step=='QCAM': #XXX hard coded logic to add DECOMPOSITION in the route of components
                for pre_predecessor_step in getNotMachineNodePredecessorList(predecessor_step):
                    predecessor_set.add(pre_predecessor_step)
                    route={"stationIdsList": [pre_predecessor_step],}
                    route_list.append(route)
            predecessor_set.add(predecessor_step)
            route = {"stationIdsList": [predecessor_step],}
            route_list.append(route)
        #=======================================================================
        #                        append the current step
        #=======================================================================
        # if there is a pending step (SETUP-setup_step) for this step (next_step), 
        # add the processing time as setup_time to the current step
        setup_time=0
        if step_sequence_list[j]==next_step:
            setup_time=float(setup_step[2])
            #reset the dummy variables
            setup_step=None
            next_step=None
        route = {"stationIdsList": list(getMachineNameSet(sequence_step)),
                 "processingTime": {"distributionType": "Fixed",
                                    "mean": float(processing_time_list[j])},
                 "setupTime": {"distributionType": "Fixed",
                               "mean": setup_time}, # XXX hard-coded value
                 "stepNumber": str(step_sequence_list[j]),
                 }
        if prerequisite_list:
            route["prerequisites"] = prerequisite_list
        route_list.append(route)
        #=======================================================================
        #                     append successors if needed
        #=======================================================================
        # treat the case of design (add order DECOMPOSITION)
        if "CAD" in sequence_step and j==len(technology_list):
            for successor_step in getNotMachineNodeSuccessorList(sequence_step):
                successor_set.add(successor_step)
                route = {"stationIdsList": [successor_step],}
                route_list.append(route)
        # treat the case of mould (add EXIT)
        elif sequence_step=="INJM" or sequence_step=='INJM-MAN' and j==len(technology_list):
            for successor_step in getNotMachineNodeSuccessorList(sequence_step):
                successor_set.add(successor_step)
                route = {"stationIdsList": [successor_step],}
                route_list.append(route)
        # treat the case of normal components (add ASSM buffer and ASSM after MAN operations 
        elif j==len(technology_list):
            for successor_step in getNotMachineNodeSuccessorList(sequence_step):
                # first add the ASSEMBLY BUFFER
                successor_set.add(successor_step)
                route = {"stationIdsList": [successor_step],}
                route_list.append(route)
                # the add the ASSEMBLY
                for second_successor_step in getNotMachineNodeSuccessorList(successor_step):
                    successor_set.add(second_successor_step)
                    route = {"stationIdsList": [second_successor_step],}
                    route_list.append(route)
        # XXX INJM-MAN/INJM+INJM-SET must be set as one step of the route, the same stands for the other ***-SET steps
    return route_list
        
def getListFromString(self, my_string):
    my_list = []
    if not my_string in (None, ''):
      my_list = my_string.split('-')
    return my_list

ROUTE_STEPS_SET=set(["ENG", "CAD","CAM","MILL", "MILL-SET","TURN", "DRILL", "QUAL","EDM", "EDM-SET","ASSM", "MAN","INJM", "INJM-MAN", "INJM-SET"])
DESIGN_ROUTE_STEPS_SET=set(["ENG", "CAD"])
MOULD_ROUTE_STEPS_SET=set(["ASSM","INJM","INJM-MAN","INJM-SET"])
def getComponets(orderDict,Order):
    """ get the components of each order, and construct them.
    """
    G.MouldList=[]
    G.OrderComponentList=[]
    G.DesignList=[]
    G.WipList=[]
    G.EntityList=[]
    G.JobList=[]
    isCritical=Order.isCritical                        # XXX have to figure out the isCritical flag
    
    # get the componentsList
    components=orderDict.get('componentsList',[])
    
    for component in components:
        id=component.get('componentID','')
        name=component.get('componentName','')
        dictRoute=component.get('route',[])
        route = [x for x in dictRoute]       #    copy dictRoute
        # keep a reference of all extra properties passed to the job
        extraPropertyDict = {}
        for key, value in entity.items():
            if key not in ('_class', 'id'):
                extraPropertyDict[key] = value
        
        # if there is an exit assigned to the component
        #    update the corresponding local flag
        # TODO: have to talk about it with NEX
        technology_list=[]  # list of the technologies per step of the part's route
        mould_step_list=[]  # list of all the info needed for the each step of the part's route if it is mould
        design_step_list=[] # list of all the info needed for the each step of the part's route if it is design
        step_list=[]        # list of all the info needed for the each step of the part's route
        exitAssigned=False
        for step in route:
            stepTechnology = step.get('technology',[])
            assert stepTechnology in ROUTE_STEPS_SET, 'the technology provided does not exist'
            stepSequence=step.get('sequence','0')
            parts_needed=step.get('parts_needed',[])
            processingTime=step.get('processingTime',{})
            # if the technology step is in the DESIGN_ROUTE_STEPS_SET
            if stepTechnology in DESIGN_ROUTE_STEPS_SET:
                design_step_list.append((stepTechnology,stepSequence,processingTime,parts_needed))
            # if the technology step is in the MOULD_ROUTE_STEPS_SET
            elif stepTechnology in MOULD_ROUTE_STEPS_SET:
                mould_step_list.append((stepTechnology,stepSequence,processingTime,parts_needed))
            technology_list.append(stepTechnology)
            step_list.append((stepTechnology,stepSequence,processingTime,parts_needed))
            
            # XXX componentType needed
            # XXX the components should not be created if the are not in the WIP or not designs
            # append to the entity list only those entities that are in the current WIP and not those to be created
            # later on, that the entities should be created by the order decomposition or the mould assembly
            #     the assembler or the decomposer must check if they are already created
        
        # find the new route of the component if it is no design or mould
        if not mould_step_list and not design_step_list:
            route_list=getRouteList(step_list)
            componentType='Basic'               # XXX have to figure out the component type
            readyForAssembly=0                  # XXX have to figure out the readyForAssembly flag
            # XXX if the component is not in the WipIDList then do not create it but append it the componentsList of the Order O
            if id in G.WipIDList:
                # initiate the job
                OC=OrderComponent(id, name, route_list, priority=Order.priority, dueDate=Order.dueDate,orderDate=Order.orderDate,
                                  componentType=componentType, order=Order, readyForAssembly=readyForAssembly,
                                  extraPropertyDict=extraPropertyDict)
                G.OrderComponentList.append(OC)
                G.JobList.append(OC)   
                G.WipList.append(OC)  
                G.EntityList.append(OC)
            else:
                componentDict={"_class": "Dream.OrderComponent",
                               "id": id,
                               "name": name,
                               "componentType": componentType,
                               "route": route_list,
                               }
                Order.componentsList.append(componentDict)
            continue
        # create to different routes for the design and for the mould (and different entities)
        if mould_step_list:
            route_list=getRouteList(mould_step_list)
            # XXX if the component is not in the WipIDList then do not create it but append it the componentsList of the Order O
            # XXX it may be that the order is already processed so there is nothing in the WIP from that order
            if id in G.WipIDList:
                # initiate the job
                M=Mould(id, name, route_list, priority=Order.priority, dueDate=Order.dueDate,orderDate=Order.orderDate,
                                    extraPropertyDict=extraPropertyDict, order=Order)
                G.MouldList.append(M)
                G.JobList.append(M)
                G.WipList.append(M)
                G.EntityList.append(M)
            else:
                componentDict={"_class": "Dream.Mould",
                               "id": id,
                               "name": name,
                               "route": route_list,
                               }
                Order.componentsList.append(componentDict)
        if design_step_list:
            route_list=getRouteList(design_step_list)
            # XXX if the design is not in the WipIDList then do create if the Order is not being processed at the moment
            #     if the Order is being processed there may be a need to create the design if the design is in the WIP
            #     otherwise the design has already been decomposed and it must not be added to the compononetsList of the order
            if (id in G.WipIDList) or\
                (not id in G.WipIDList and len(Order.auxiliaryComponentsList+Order.secondaryComponentsList+Order.basicComponentsList)==0):
                # initiate the job
                OD=Design(id, name,route_list,priority=Order.priority,dueDate=Order.dueDate,orderDate=Order.orderDate,
                                  order=Order,extraPropertyDict=extraPropertyDict)
                G.OrderComponentList.append(OD)
                G.DesignList.append(OD)
                G.JobList.append(OD)
                G.WipList.append(OD)
                G.EntityList.append(OD)
            

class EntityIDError(Exception):
    """Exception raised for errors in entities' ids.
    """
    def __init__(self, msg):
        Exception.__init__(self, msg) 
def findEntityById(entityID):
    for entity in G.EntityList:
        try:
            if entity.id==entityID:
                return entity
            else:
                return None
        except:
            raise WIPreadError('There is no Entity to be found')# pass the contents of the input file to the global var InputData

def getWipID():
    ''' create a list with the ids of the entities in the WIP
        the entities that are not in the wip should not be created
    '''
    json_data = G.wip_Data
    G.WipIDList=[]              # list that holds the IDs of the entities that are in the WIP
    #Read the json data
    WIP = json_data['WIP']                                    # read from the dictionary the dict with key 'WIP'
    for work_id in WIP.iterkeys():
        G.WipIDList.append(work_id)

def getStartWip():
    ''' XXX find the current station from the WIP,
        if not in a station, then place the entity in a queue
        XXX then remove the previous stations from the remaining_route
    '''
    json_data = G.wip_Data
    #Read the json data
    WIP = json_data['WIP']                                    # read from the dictionary the dict with key 'WIP'
    for (work_id, work) in WIP.iteritems():
        work['id']=work_id
        entity=findEntityById(work_id)
        # find the entity by its id
        step=work.get('station','')
        assert step!='', 'there must be a stationID given to set the WIP'
        from Globals import findObjectById
        station=Globals.findObjectById(step)
        # find the station by its id, if there is no station then place it 
        # in the starting queue (QCAD), ()
        entry_time=float(work.get('entry','0'))
        exit_time=float(work.get('exit','0'))
    #------------------------------------------------------------------------------ 
    # for all the entities in the entityList
    for entity in entityList:
        # if the entity is of type Job/OrderComponent/Order/Mould
        if entity.type=='Job' or entity.type=='OrderComponent' or entity.type=='Order' or entity.type=='Mould':
            # find the list of starting station of the entity
            currentObjectIds=entity.remainingRoute[0].get('stationIdsList',[])
            # if the list of starting stations has length greater than one then there is a starting WIP definition error 
            try:
                if len(currentObjectIds)==1:
                    objectId=currentObjectIds[0]
                else:
                    raise SetWipTypeError('The starting station of the the entity is not defined uniquely')
            except SetWipTypeError as setWipError:
                print 'WIP definition error: {0}'.format(setWipError)
            # get the starting station of the entity and load it with it
            object = findObjectById(objectId)
            object.getActiveObjectQueue().append(entity)        # append the entity to its Queue
            
            # read the IDs of the possible successors of the object
            nextObjectIds=entity.remainingRoute[1].get('stationIdsList',[])
            # for each objectId in the nextObjects find the corresponding object and populate the object's next list
            nextObjects=[]
            for nextObjectId in nextObjectIds:
                nextObject=findObjectById(nextObjectId)
                nextObjects.append(nextObject)  
            # update the next list of the object
            for nextObject in nextObjects:
                # append only if not already in the list
                if nextObject not in object.next:
                    object.next.append(nextObject)
            
            entity.remainingRoute.pop(0)                        # remove data from the remaining route.   
            entity.schedule.append([object,G.env.now])              #append the time to schedule so that it can be read in the result
            entity.currentStation=object                        # update the current station of the entity 
        # if the currentStation of the entity is of type Machine then the entity 
        #     must be processed first and then added to the pendingEntities list
        #     Its hot flag is not raised
        if not (entity.currentStation in G.MachineList):    
            # variable to inform whether the successors are machines or not
            successorsAreMachines=True
            for nextObject in entity.currentStation.next:
                if not nextObject in G.MachineList:
                    successorsAreMachines=False
                    break
            if not successorsAreMachines:
                entity.hot = False
            else:
                entity.hot = True
            # add the entity to the pendingEntities list
            G.pendingEntities.append(entity)