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
Created on 8 Nov 2012

@author: George
'''
'''
carries some global variables
'''

#from SimPy.Simulation import *
from Machine import Machine
from Queue import Queue
from Repairman import Repairman
import xlwt
import xlrd
from random import Random, expovariate, gammavariate, normalvariate
import simpy

# ===========================================================================
# globals
# ===========================================================================
class G:   
    seed=1450                       #the seed of the random number generator
    Rnd = Random(seed)              #random number generator
    import numpy
    numpyRnd=numpy    

    ObjList=[]                      #a list that holds all the CoreObjects 
    EntityList=[]                   #a list that holds all the Entities 
    ObjectResourceList=[]
    ObjectInterruptionList=[]
    
    numberOfReplications=1          #the number of replications default=1git 
    confidenceLevel=0.9             #the confidence level default=90%
    Base=1                          #the Base time unit. Default =1 minute
    maxSimTime=0                    #the total simulation time
    
    # flag for printing in console
    console=""
    
    # data for the trace output in excel
    trace=""                        #this is written from input. If it is "Yes" then you write to trace, else we do not
    traceIndex=0                    #index that shows in what row we are
    sheetIndex=1                    #index that shows in what sheet we are
    traceFile = xlwt.Workbook()     #create excel file
    traceSheet = traceFile.add_sheet('sheet '+str(sheetIndex), cell_overwrite_ok=True)  #create excel sheet    
    
    
    # variables for excel output
    outputIndex=0                   #index that shows in what row we are
    sheetIndex=1                    #index that shows in what sheet we are
    outputFile = xlwt.Workbook()    #create excel file
    outputSheet = outputFile.add_sheet('sheet '+str(sheetIndex), cell_overwrite_ok=True)  #create excel sheet
    
    #variables for json output
    outputJSON={}
    outputJSONFile=None
    
    numberOfEntities = 0
    
    #object that routes the operators in the model
    Router=None 
    
    #                define the lists of each object type
    SourceList=[]
    MachineList=[]
    ExitList=[]
    QueueList=[]    
    RepairmanList=[]
    AssemblyList=[]
    DismantleList=[]
    ConveyerList=[]
    MachineJobShopList=[]
    QueueJobShopList=[]
    ExitJobShopList=[]
    BatchDecompositionList=[]
    BatchSourceList=[]
    BatchReassemblyList=[]
    LineClearanceList=[]
    EventGeneratorList=[]
    OperatorsList = []
    OperatorManagedJobsList = []
    OperatorPoolsList = []
    BrokersList = []
    OperatedMachineList = []
    BatchScrapMachineList=[]
    OrderDecompositionList=[]
    ConditionalBufferList=[]
    MouldAssemblyBufferList=[]
    MouldAssemblyList=[]
    MachineManagedJobList=[]
    QueueManagedJobList=[]
    ModelResourceList=[]
    
    JobList=[]
    WipList=[]
    EntityList=[]  
    PartList=[]
    OrderComponentList=[]
    OrderList=[]
    MouldList=[]
    BatchList=[]
    SubBatchList=[]
    # entities that just finished processing in a station 
    # and have to enter the next machine 
    pendingEntities=[]
    env=simpy.Environment()

    totalPulpTime=0     # temporary to track how much time PuLP needs to run 
    
# =======================================================================
# method to move entities exceeding a certain safety stock
# =======================================================================
def moveExcess(consumption=1,safetyStock=70, giverId=None, receiverId=None):
    giver=findObjectById(giverId)
    receiver=findObjectById(receiverId)
    safetyStock=int(safetyStock)
    consumption=int(consumption)
    if giver and receiver:
        if len(giver.getActiveObjectQueue())>safetyStock:
            giver.receiver=receiver
            receiver.giver=giver
            for i in range(consumption):
                receiver.getEntity()         
            giver.next=[]
            receiver.previous=[]
    else:
        print "Giver and/or Receiver not defined"

# =======================================================================
# Import a class from a dotted name used in json.
# =======================================================================
def getClassFromName(dotted_name):
    from zope.dottedname.resolve import resolve
    import logging
    logger = logging.getLogger("dream.platform")
    parts = dotted_name.split('.')
    # this is added for backwards compatibility
    if dotted_name.startswith('Dream'):
        class_name = dotted_name.split('.')[-1]
        new_dotted_name = 'dream.simulation.%s.%s' % (class_name, class_name)
        #logger.info(("Old style name %s used, using %s instead" % (dotted_name, new_dotted_name)))
        dotted_name = new_dotted_name
    return resolve(dotted_name)

# =======================================================================
# returns a method by its name. name should be given as Dream.ClassName.MethodName
# =======================================================================
def getMethodFromName(dotted_name):
    name=dotted_name.split('.')
    methodName=name[-1]
    # if the method is in this script
    if 'Globals' in name:
        methodName=name[name.index('Globals')+1]
        possibles = globals().copy()
        possibles.update(locals())
        method = possibles.get(methodName)
    # if the method is in a class
    else:
        clsName=''
        #clsName=name[0]+'.'+name[1]
        for i in range(len(name)-1):
            clsName+=name[i]
            clsName+='.'
        clsName=clsName[:-1]
        cls=getClassFromName(clsName)
        method = getattr(cls, methodName)
    if not method:
        raise Exception("Method %s not implemented" % method_name)
    return method
      
# =======================================================================
# method finding objects by ID
# =======================================================================
def findObjectById(id):
    for obj in G.ObjList + G.ObjectResourceList + G.EntityList + G.ObjectInterruptionList + G.OrderList:
        if obj.id==id:
            return obj
    return None

# =======================================================================
# Error in the setting up of the WIP
# =======================================================================
class SetWipTypeError(Exception):
    def __init__(self, setWipError):
        Exception.__init__(self, setWipError) 
# =======================================================================
# method to set-up the entities in the current stations 
# as Work In Progress
# in this case the current station must be defined! 
# otherwise there is no current station but a list of possible stations
# although the entity cannot be in more than one stations
# =======================================================================
def setWIP(entityList):
    # for all the entities in the entityList
    for entity in entityList:
        # if the entity is of type Part
        if entity.type in ['Part', 'Batch', 'SubBatch','CapacityEntity']:
            # these entities have to have a currentStation. 
            # TODO apply a more generic approach so that all need to have
            if entity.currentStation:   
                object=entity.currentStation                        #identify the object
                object.getActiveObjectQueue().append(entity)        #append the entity to its Queue
                entity.schedule.append([object,G.env.now])              #append the time to schedule so that it can be read in the result
            
        
        # if the entity is of type Job/OrderComponent/Order/Mould
        # XXX Orders do no more run in the system, instead we have OrderDesigns
        elif entity.type in ['Job', 'OrderComponent', 'Order','OrderDesign', 'Mould']:
            
            # find the list of starting station of the entity
            # XXX if the entity is in wip then the current station is already defined and the remainingRoute has to be redefined
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
            # if the entity is to be appended to a mouldAssemblyBuffer then it is readyForAsselbly
            if object.__class__.__name__=='MouldAssemblyBuffer':
                entity.readyForAssembly=1
            
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

        # if the currentStation of the entity is of type Machine then the entity 
        #     must be processed first and then added to the pendingEntities list
        #     Its hot flag is not raised        
        # the following to be performed only if there is a current station. Orders, Projects e.t.c do not have
        # TODO, maybe we should loop in wiplist here
        if (not (entity.currentStation in G.MachineList)) and entity.currentStation:    
            # add the entity to the pendingEntities list
            G.pendingEntities.append(entity)
            
        # if the station is buffer then sent the canDispose signal
        from Queue import Queue
        if entity.currentStation:
            if issubclass(entity.currentStation.__class__, Queue):
                # send the signal only if it is not already triggered
                if not entity.currentStation.canDispose.triggered:
                    if entity.currentStation.expectedSignals['canDispose']:
                        succeedTuple=(G.env,G.env.now)
                        entity.currentStation.canDispose.succeed(succeedTuple)   
                        entity.currentStation.expectedSignals['canDispose']=0
        # if we are in the start of the simulation the object is of server type then we should send initialWIP signal
        # TODO, maybe use 'class_family attribute here'
        if G.env.now==0 and entity.currentStation:
            if entity.currentStation.class_name:
                stationClass=entity.currentStation.__class__.__name__
                if stationClass in ['Machine', 'BatchScrapMachine', 'MachineJobShop','BatchDecomposition', 'BatchReassembly','M3',
                                    'BatchReassemblyBlocking','BatchDecompositionBlocking','BatchScrapMachineAfterDecompose',
                                    'BatchDecompositionStartTime']:
                    entity.currentStation.currentEntity=entity
                    # trigger initialWIP event only if it has not been triggered. Otherwise
                    # if we set more than one entities (e.g. in reassembly) it will crash
                    if not (entity.currentStation.initialWIP.triggered):
                        if entity.currentStation.expectedSignals['initialWIP']:
                            succeedTuple=(G.env,G.env.now)
                            entity.currentStation.initialWIP.succeed(succeedTuple)
                            entity.currentStation.expectedSignals['initialWIP']=0


def countIntervalThroughput(**kw):
    from Exit import Exit
    currentExited=0  
    for obj in G.ObjList:
        if isinstance(obj, Exit):
            totalExited=obj.totalNumberOfUnitsExited
            previouslyExited=sum(obj.intervalThroughPutList)
            currentExited+=totalExited-previouslyExited
            obj.intervalThroughPutList.append(currentExited)

    
# #===========================================================================
# # printTrace
# #===========================================================================
# def printTrace(entity='',station='', **kw):
#     assert len(kw)==1, 'only one phrase per printTrace supported for the moment'
#     from Globals import G
#     time=G.env.now
#     charLimit=60
#     remainingChar=charLimit-len(entity)-len(str(time))
#     if(G.console=='Yes'):
#         print time,entity,
#         for key in kw:
#             if key not in getSupportedPrintKwrds():
#                 raise ValueError("Unsupported phrase %s for %s" % (key, station.id))
#             element=getPhrase()[key]
#             phrase=element['phrase']
#             prefix=element.get('prefix',None)
#             suffix=element.get('suffix',None)
#             arg=kw[key]
#             if prefix:
#                 print prefix*remainingChar,phrase,arg
#             elif suffix:
#                 remainingChar-=len(phrase)+len(arg)
#                 suffix*=remainingChar
#                 if key=='enter':
#                     suffix=suffix+'>'
#                 print phrase,arg,suffix
#             else:
#                 print phrase,arg
    
#===========================================================================
# get the supported print Keywords
#===========================================================================
def getSupportedPrintKwrds():
    return ("create",
            "signal", "signalReceiver", "signalGiver",
            "attemptSignal","attemptSignalGiver", "attemptSignalReceiver",
            "preempt", "preempted",
            "startWork", "finishWork", 
            "processEnd", "interrupted",
            "enter", "destroy",
            "waitEvent", "received", "isRequested","canDispose",
            "interruptionEnd", "loadOperatorAvailable", "resourceAvailable","entityRemoved",
            'conveyerEnd', 'conveyerFull','moveEnd')
        
#===========================================================================
# get the phrase to print from the keyword
#===========================================================================
def getPhrase():
    printKwrds={'create':{'phrase':'created an entity'},
                "destroy":{'phrase':'destroyed at', 'suffix':' * '},
                'signal':{'phrase':'signalling'},
                'signalGiver':{'phrase':'signalling giver', 'prefix':'_'},
                'signalReceiver':{'phrase':'signalling receiver','prefix':'_'}, 
                'attemptSignal':{'phrase':'will try to signal'},
                'attemptSignalGiver':{'phrase':'will try to signal a giver'}, 
                'attemptSignalReceiver':{'phrase':'will try to signal a receiver'}, 
                'preempt': {'phrase':'preempts','suffix':' .'}, 
                'preempted': {'phrase':'is being preempted','suffix':'. '},
                'startWork':{'phrase':'started working in'},
                'finishWork':{'phrase':'finished working in'},
                'processEnd':{'phrase':'ended processing in'},
                'interrupted':{'phrase':'interrupted at','suffix':' .'},
                'enter':{'phrase':'got into','suffix':'='}, 
                'waitEvent':{'phrase':'will wait for event'},
                'received':{'phrase':'received event'},
                'isRequested':{'phrase':'received an isRequested event from'},
                'canDispose':{'phrase':'received an canDispose event'},
                'interruptionEnd':{'phrase':'received an interruptionEnd event at'},
                "loadOperatorAvailable":{'phrase':'received a loadOperatorAvailable event at'},
                "resourceAvailable":{'phrase':'received a resourceAvailable event'},
                "entityRemoved":{'phrase':'received an entityRemoved event from'},
                'moveEnd':{'phrase':'received a moveEnd event'},
                "conveyerEnd":{'phrase':'has reached conveyer End', 'suffix':'.!'},
                'conveyerFull':{'phrase':'is now Full, No of units:', 'suffix':'(*)'}}
    return printKwrds

def runSimulation(objectList=[], maxSimTime=100, numberOfReplications=1, trace='No', seed=1):
    G.numberOfReplications=numberOfReplications
    G.trace=trace
    G.maxSimTime=float(maxSimTime)
    G.seed=seed
    
    G.ObjList=[]
    G.ObjectInterruptionList=[]
    G.ObjectResourceList=[]
    from CoreObject import CoreObject
    from ObjectInterruption import ObjectInterruption
    from ObjectResource import ObjectResource
    from Entity import Entity
    for object in objectList:
        if issubclass(object.__class__, CoreObject):
            G.ObjList.append(object)
        elif issubclass(object.__class__, ObjectInterruption):
            G.ObjectInterruptionList.append(object)
        elif issubclass(object.__class__, ObjectResource):
            G.ObjectResourceList.append(object)  

    #run the replications
    for i in range(G.numberOfReplications):    
        G.seed+=1       #increment the seed so that we get different random numbers in each run.
        
        G.env=simpy.Environment()   # define a simpy environment
                                    # this is where all the simulation object 'live'

        G.EntityList=[]
        for object in objectList:
            if issubclass(object.__class__, Entity):
                G.EntityList.append(object)   

        #initialize all the objects
        for object in G.ObjList + G.ObjectInterruptionList + G.ObjectResourceList + G.EntityList:
            object.initialize()
    
        #activate all the objects
        for object in G.ObjectInterruptionList:
            G.env.process(object.run())
        #activate all the objects
        for object in G.ObjList:
            G.env.process(object.run())

        #set the WIP
        setWIP(G.EntityList)
    
        G.env.run(until=G.maxSimTime)    #run the simulation

        # identify from the exits what is the time that the last entity has ended. 
        endList=[]
        from Exit import Exit
        for object in G.ObjList:
            if issubclass(object.__class__,Exit):
                endList.append(object.timeLastEntityLeft)
        
        # identify the time of the last event
        if G.env.now==float('inf'):    
            G.maxSimTime=float(max(endList))
        # do not let G.maxSimTime=0 so that there will be no crash
        if G.maxSimTime==0:
            print "simulation ran for 0 time, something may have gone wrong"
            import sys
            sys.exit()         
               
        #carry on the post processing operations for every object in the topology
        for object in G.ObjList + G.ObjectResourceList:
            object.postProcessing()

    


    
