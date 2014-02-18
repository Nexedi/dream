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
from Batch import Batch
from SubBatch import SubBatch
from BatchSource import BatchSource
from BatchDecomposition import BatchDecomposition
from BatchReassembly import BatchReassembly
from BatchScrapMachine import BatchScrapMachine
from LineClearance import LineClearance
from EventGenerator import EventGenerator
from Operator import Operator
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


# ===========================================================================
#                       reads general simulation inputs
# ===========================================================================
def readGeneralInput():
    general=G.JSONData['general']                                           # read the dict with key 'general'
    G.numberOfReplications=int(general.get('numberOfReplications', '1'))    # read the number of replications / default 1
    G.maxSimTime=float(general.get('maxSimTime', '100'))                    # get the maxSimTime / default 100
    G.trace=general.get('trace', 'No')                                      # get trace in order to check if trace is requested
    G.confidenceLevel=float(general.get('confidenceLevel', '0.95'))         # get the confidence level

# ===========================================================================
#                       creates the simulation objects
# ===========================================================================
def createObjects():

    json_data = G.JSONData
    #Read the json data
    nodes = json_data['nodes']                      # read from the dictionary the dicts with key 'nodes'
    edges = json_data['edges']                      # read from the dictionary the dicts with key 'edges'


    # -----------------------------------------------------------------------
    #                getSuccesorList method to get the successor 
    #                       list of object with ID = id
    #                         XXX slow implementation
    # -----------------------------------------------------------------------
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
    # -----------------------------------------------------------------------
    #                define the lists of each object type
    # -----------------------------------------------------------------------
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
    G.LineClearanceList=[]
    G.EventGeneratorList=[]
    G.OperatorsList = []
    G.OperatorPoolsList = []
    G.BrokersList = []
    G.OperatedMachineList = []
    G.BatchScrapMachineList=[]
    G.OrderDecompositionList=[]
    G.ConditionalBufferList=[]
    G.MouldAssemblyBufferList=[]
    G.MouldAssemblyList=[]
    G.MachineManagedJobList=[]
    G.QueueManagedJobList=[]
    G.ModelResourceList=[]
    
    # -----------------------------------------------------------------------
    #                loop through all the model resources 
    #      search for repairmen and operators in order to create them
    #                   read the data and create them
    # -----------------------------------------------------------------------
    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
                                                                    # the key is the element_id and the second is the 
                                                                    # element itself 
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
                                                                    # with key 'id' and value the the element_id
        resourceClass = element.get('_class', 'not found')          # get the class type of the element
        if resourceClass=='Dream.Repairman':                        # check the object type
            id = element.get('id', 'not found')                     # get the id of the element
            name = element.get('name', id)                          # get the name of the element / default 'not_found'
            capacity = int(element.get('capacity') or 1)
            R = Repairman(element_id, name, capacity)               # create a repairman object
            R.coreObjectIds=getSuccessorList(id)                    # update the list of objects that the repairman repairs
                                                                    # calling the getSuccessorList() method on the repairman
            G.RepairmanList.append(R)                               # add the repairman to the RepairmanList
            G.ModelResourceList.append(R) 
        elif resourceClass=='Dream.Operator':
            id = element.get('id', 'not found')                     # get the id of the element   / default 'not_found'
            name = element.get('name', 'not found')                 # get the name of the element / default 'not_found'
            capacity = int(element.get('capacity') or 1)
            O = Operator(element_id, name, capacity)                # create an operator object
            O.coreObjectIds=getSuccessorList(id)                	# update the list of objects that the operator operates
																	# calling the getSuccesorList() method on the operator
            G.OperatorsList.append(O)                               # add the operator to the RepairmanList
            G.ModelResourceList.append(O) 
    # -----------------------------------------------------------------------
    #                loop through all the model resources 
    #          search for operatorPools in order to create them
    #                   read the data and create them
    # -----------------------------------------------------------------------
    for (element_id, element) in nodes.iteritems():                 # use an iterator to go through all the nodes
                                                                    # the key is the element_id and the second is the 
                                                                    # element itself 
        element['id'] = element_id                                  # create a new entry for the element (dictionary)
                                                                    # with key 'id' and value the the element_id
        resourceClass = element.get('_class', 'not found')          # get the class type of the element
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
    # -----------------------------------------------------------------------
    #                    loop through all the elements    
    #                    read the data and create them
    # -----------------------------------------------------------------------
    for (element_id, element) in nodes.iteritems():
        element['id'] = element_id
        objClass=element.get('_class', 'not found')   
        if objClass=='Dream.Source':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            interarrivalTime=element.get('interarrivalTime',{})
            distributionType=interarrivalTime.get('distributionType', 'not found')
            mean=float(interarrivalTime.get('mean') or 0)
            entity=str_to_class(element['entity'])     # initialize entity
            S=Source(id, name, distributionType, mean, entity)          # initialize Source
            S.nextIds=getSuccessorList(id)
            G.SourceList.append(S)
            G.ObjList.append(S)
            
        if objClass=='Dream.BatchSource':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            interarrivalTime=element.get('interarrivalTime',{})
            distributionType=interarrivalTime.get('distributionType', 'not found')
            mean=float(interarrivalTime.get('mean') or 0)
            entity=str_to_class(element['entity'])          
            batchNumberOfUnits=int(element.get('batchNumberOfUnits', 'not found'))
            S=BatchSource(id, name, distributionType, mean, entity, batchNumberOfUnits)
            S.nextIds=getSuccessorList(id)
            G.BatchSourceList.append(S)
            G.SourceList.append(S)
            G.ObjList.append(S)
            
        elif objClass=='Dream.Machine':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime',{})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            # type of operation and related times 
            operationType=element.get('operationType','not found')
            setupTime = element.get('setupTime',{})
            setupDistribution = setupTime.get('setupDistribution','not found')
            setupMean = float(setupTime.get('setupMean') or 0)
            setupStdev=float(setupTime.get('setupStdev') or 0)
            setupMin=float(setupTime.get('setupMin') or 0)
            setupMax=float(setupTime.get('setupMax') or 0)
            loadTime = element.get('loadTime',{})
            loadDistribution = loadTime.get('loadDistribution','not found')
            loadMean = float(loadTime.get('loadMean') or 0)
            loadStdev = float(loadTime.get('loadStdev') or 0)
            loadMin=float(loadTime.get('loadMin') or 0)
            loadMax=float(loadTime.get('loadMax') or 0)
            preemption=element.get('preemption',{})
            isPreemptive=resetOnPreemption=False
            if len(preemption)>0:
                isPreemptive=bool(int(preemption.get('isPreemptive') or 0))
                resetOnPreemption=bool(int(preemption.get('isPreemptive') or 0))
            
            if len(G.OperatorPoolsList)>0:
                for operatorPool in G.OperatorPoolsList:                    # find the operatorPool assigned to the machine
                    if(id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
                        machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
                                                                            # otherwise only one of them will be taken into account
                    else:
                        machineOperatorPoolList=[]                          # if there is no operatorPool assigned to the machine
            else:                                                           # then machineOperatorPoolList/operatorPool is a list
                machineOperatorPoolList=[]                                  # if there are no operatorsPool created then the 
                                                                            # then machineOperatorPoolList/operatorPool is a list
            if (type(machineOperatorPoolList) is list):                 # if the machineOperatorPoolList is a list
                                                                        # find the operators assigned to it and add them to the list
                for operator in G.OperatorsList:                        # check which operator in the G.OperatorsList
                    if(id in operator.coreObjectIds):                   # (if any) is assigned to operate
                        machineOperatorPoolList.append(operator)        # the machine with ID equal to id
                                                                        # if there is no operator assigned then the list will be empty
            r='None'
            for repairman in G.RepairmanList:                   # check which repairman in the G.RepairmanList
                if(id in repairman.coreObjectIds):              # (if any) is assigned to repair 
                    r=repairman                                 # the machine with ID equal to id
            M=Machine(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, #repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max,
                                                    operatorPool=machineOperatorPoolList, operationType=operationType,
                                                    loadDistribution=loadDistribution, setupDistribution=setupDistribution,
                                                    setupMean=setupMean,setupStdev=setupStdev,setupMin=setupMin,setupMax=setupMax,
                                                    loadMean=loadMean,loadStdev=loadStdev,loadMin=loadMin,loadMax=loadMax,
                                                    repairman=r, isPreemptive=isPreemptive, resetOnPreemption=resetOnPreemption)
            M.nextIds=getSuccessorList(id)                      # update the nextIDs list of the machine
            G.MachineList.append(M)                             # add machine to global MachineList
            if M.operatorPool!="None":
                G.OperatedMachineList.append(M)                 # add the machine to the operatedMachines List
            G.ObjList.append(M)                                 # add machine to ObjList
            
        elif objClass=='Dream.BatchScrapMachine':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime',{})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            scrapQuantity=element.get('scrapQuantity', {})
            scrapDistributionType=scrapQuantity.get('distributionType', 'not found')
            scrMean=int(scrapQuantity.get('mean') or 0)
            scrStdev=float(scrapQuantity.get('stdev') or 0)
            scrMin=int(scrapQuantity.get('min') or 0)
            scrMax=int(scrapQuantity.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            r='None'
            for repairman in G.RepairmanList:                   # check which repairman in the G.RepairmanList
                if(id in repairman.coreObjectIds):              # (if any) is assigned to repair 
                    r=repairman                                 # the machine with ID equal to id
                    
            M=BatchScrapMachine(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max, scrMean=scrMean, 
                                                    scrStdev=scrStdev,scrMin=scrMin,scrMax=scrMax)
            M.nextIds=getSuccessorList(id)                      # update the nextIDs list of the machine
            G.MachineList.append(M)                             # add machine to global MachineList
            G.BatchScrapMachineList.append(M)
            G.ObjList.append(M)                                 # add machine to ObjList


        elif objClass=='Dream.M3':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            scrapQuantity=element.get('scrapQuantity', {})
            scrapDistributionType=scrapQuantity.get('distributionType', 'not found')
            scrMean=int(scrapQuantity.get('mean') or 0)
            scrStdev=float(scrapQuantity.get('stdev') or 0)
            scrMin=int(scrapQuantity.get('min') or 0)
            scrMax=int(scrapQuantity.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            r='None'
            for repairman in G.RepairmanList:                   # check which repairman in the G.RepairmanList
                if(id in repairman.coreObjectIds):              # (if any) is assigned to repair 
                    r=repairman                                 # the machine with ID equal to id
                    
            M=M3(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max, scrMean=scrMean, 
                                                    scrStdev=scrStdev,scrMin=scrMin,scrMax=scrMax)
            M.nextIds=getSuccessorList(id)                      # update the nextIDs list of the machine
            G.MachineList.append(M)                             # add machine to global MachineList
            G.BatchScrapMachineList.append(M)
            G.ObjList.append(M)                                 # add machine to ObjList
            
        elif objClass=='Dream.MachineJobShop':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            # type of operation and related times 
            operationType=element.get('operationType','not found')
            setupTime = element.get('setupTime',{})
            setupDistribution = setupTime.get('setupDistribution','not found')
            setupMean = float(setupTime.get('setupMean') or 0)
            setupStdev=float(setupTime.get('setupStdev') or 0)
            setupMin=float(setupTime.get('setupMin') or 0)
            setupMax=float(setupTime.get('setupMax', '0'))
            loadTime = element.get('loadTime',{})
            loadDistribution = loadTime.get('loadDistribution','not found')
            loadMean = float(loadTime.get('loadMean') or 0)
            loadStdev = float(loadTime.get('loadStdev') or 0)
            loadMin=float(loadTime.get('loadMin') or 0)
            loadMax=float(loadTime.get('loadMax') or 0)
            preemption=element.get('preemption',{})
            isPreemptive=resetOnPreemption=False
            if len(preemption)>0:
                isPreemptive=bool(int(preemption.get('isPreemptive') or 0))
                resetOnPreemption=bool(int(preemption.get('resetOnPreemption') or 0))
            
            if len(G.OperatorPoolsList)>0:
                for operatorPool in G.OperatorPoolsList:                    # find the operatorPool assigned to the machine
                    if(id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
                        machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
                                                                            # otherwise only one of them will be taken into account
                    else:
                        machineOperatorPoolList=[]                          # if there is no operatorPool assigned to the machine
            else:                                                           # then machineOperatorPoolList/operatorPool is a list
                machineOperatorPoolList=[]                                  # if there are no operatorsPool created then the 
                                                                            # then machineOperatorPoolList/operatorPool is a list
            if (type(machineOperatorPoolList) is list):                 # if the machineOperatorPoolList is a list
                                                                        # find the operators assigned to it and add them to the list
                for operator in G.OperatorsList:                        # check which operator in the G.OperatorsList
                    if(id in operator.coreObjectIds):                   # (if any) is assigned to operate
                        machineOperatorPoolList.append(operator)        # the machine with ID equal to id
                                                                        # if there is no operator assigned then the list will be empty
            r='None'
            for repairman in G.RepairmanList:
                if(id in repairman.coreObjectIds):
                    r=repairman
                    
            M=MachineJobShop(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, #repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max,
                                                    operatorPool=machineOperatorPoolList, operationType=operationType,
                                                    loadDistribution=loadDistribution, setupDistribution=setupDistribution,
                                                    setupMean=setupMean,setupStdev=setupStdev,setupMin=setupMin,setupMax=setupMax,
                                                    loadMean=loadMean,loadStdev=loadStdev,loadMin=loadMin,loadMax=loadMax,
                                                    repairman=r, isPreemptive=isPreemptive, resetOnPreemption=resetOnPreemption)
            M.nextIds=getSuccessorList(id)
            G.MachineJobShopList.append(M)
            G.MachineList.append(M)
            if M.operatorPool!="None":
                G.OperatedMachineList.append(M)                     # add the machine to the operatedMachines List
            G.ObjList.append(M)

        elif objClass=='Dream.MachineManagedJob':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            # type of operation and related times 
            operationType=element.get('operationType','not found')
            setupTime = element.get('setupTime',{})
            setupDistribution = setupTime.get('setupDistribution','not found')
            setupMean = float(setupTime.get('setupMean') or 0)
            setupStdev=float(setupTime.get('setupStdev') or 0)
            setupMin=float(setupTime.get('setupMin') or 0)
            setupMax=float(setupTime.get('setupMax') or 0)
            loadTime = element.get('loadTime',{})
            loadDistribution = loadTime.get('loadDistribution','not found')
            loadMean = float(loadTime.get('loadMean') or 0)
            loadStdev = float(loadTime.get('loadStdev') or 0)
            loadMin=float(loadTime.get('loadMin') or 0)
            loadMax=float(loadTime.get('loadMax') or 0)
            preemption=element.get('preemption',{})
            isPreemptive=resetOnPreemption=False
            if len(preemption)>0:
                isPreemptive=bool(int(preemption.get('isPreemptive') or 0))
                resetOnPreemption=bool(int(preemption.get('resetOnPreemption') or 0))
            
            if len(G.OperatorPoolsList)>0:
                for operatorPool in G.OperatorPoolsList:                    # find the operatorPool assigned to the machine
                    if(id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
                        machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
                                                                            # otherwise only one of them will be taken into account
                    else:
                        machineOperatorPoolList=[]                          # if there is no operatorPool assigned to the machine
            else:                                                           # then machineOperatorPoolList/operatorPool is a list
                machineOperatorPoolList=[]                                  # if there are no operatorsPool created then the 
                                                                            # then machineOperatorPoolList/operatorPool is a list
            if (type(machineOperatorPoolList) is list):                 # if the machineOperatorPoolList is a list
                                                                        # find the operators assigned to it and add them to the list
                for operator in G.OperatorsList:                        # check which operator in the G.OperatorsList
                    if(id in operator.coreObjectIds):                   # (if any) is assigned to operate
                        machineOperatorPoolList.append(operator)        # the machine with ID equal to id
                                                                        # if there is no operator assigned then the list will be empty
            r='None'
            for repairman in G.RepairmanList:
                if(id in repairman.coreObjectIds):
                    r=repairman
                    
            M=MachineManagedJob(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, #repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max,
                                                    operatorPool=machineOperatorPoolList, operationType=operationType,
                                                    loadDistribution=loadDistribution, setupDistribution=setupDistribution,
                                                    setupMean=setupMean,setupStdev=setupStdev,setupMin=setupMin,setupMax=setupMax,
                                                    loadMean=loadMean,loadStdev=loadStdev,loadMin=loadMin,loadMax=loadMax,
                                                    repairman=r, isPreemptive=isPreemptive, resetOnPreemption=resetOnPreemption)
            M.nextIds=getSuccessorList(id)
            G.MachineManagedJobList.append(M)
            G.MachineJobShopList.append(M)
            G.MachineList.append(M)
            if M.operatorPool!="None":
                G.OperatedMachineList.append(M)                     # add the machine to the operatedMachines List
            G.ObjList.append(M)
             
        elif objClass=='Dream.Exit':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            E=Exit(id, name)
            G.ExitList.append(E)
            G.ObjList.append(E)
            
        elif objClass=='Dream.ExitJobShop':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            E=ExitJobShop(id, name)
            G.ExitJobShopList.append(E)
            G.ExitList.append(E)
            G.ObjList.append(E)
            
        elif objClass=='Dream.Queue':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            capacity=int(element.get('capacity') or 1)
            isDummy=bool(int(element.get('isDummy') or 0))
            schedulingRule=element.get('schedulingRule', 'FIFO')
            Q=Queue(id, name, capacity, isDummy, schedulingRule=schedulingRule)
            Q.nextIds=getSuccessorList(id)
            G.QueueList.append(Q)
            G.ObjList.append(Q)
            
        elif objClass=='Dream.QueueJobShop':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            capacity=int(element.get('capacity') or 1)
            isDummy=bool(int(element.get('isDummy') or 0))
            schedulingRule=element.get('schedulingRule', 'FIFO')
            Q=QueueJobShop(id, name, capacity, isDummy, schedulingRule=schedulingRule)
            Q.nextIds=getSuccessorList(id)
            G.QueueList.append(Q)
            G.QueueJobShopList.append(Q)
            G.ObjList.append(Q)
            
        elif objClass=='Dream.QueueManagedJob':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            capacity=int(element.get('capacity') or 1)
            isDummy=bool(int(element.get('isDummy') or 0))
            schedulingRule=element.get('schedulingRule', 'FIFO')
            Q=QueueManagedJob(id, name, capacity, isDummy, schedulingRule=schedulingRule)
            Q.nextIds=getSuccessorList(id)
            G.QueueList.append(Q)
            G.QueueManagedJobList.append(Q)
            G.QueueJobShopList.append(Q)
            G.ObjList.append(Q)
                       
        elif objClass=='Dream.QueueLIFO':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            successorList=element.get('successorList', 'not found')
            capacity=int(element.get('capacity') or 1)
            isDummy=bool(int(element.get('isDummy') or 0))
            Q=QueueLIFO(id, name, capacity, isDummy)
            Q.nextIds=successorList
            G.QueueList.append(Q)
            G.ObjList.append(Q)
            
        elif objClass=='Dream.Assembly':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            A=Assembly(id, name, distribution=distributionType, mean=mean,stdev=stdev,min=min,max=max)
            A.nextIds=getSuccessorList(id)
            G.AssemblyList.append(A)
            G.ObjList.append(A)
            
        elif objClass=='Dream.Dismantle':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            D=Dismantle(id, name, distribution=distributionType, mean=mean,stdev=stdev,min=min,max=max)
            # get the successorList for the 'Parts'
            D.nextPartIds=getSuccessorList(id, lambda source, destination, edge_data: edge_data.get('entity') == 'Part')
            # get the successorList for the 'Frames'
            D.nextFrameIds=getSuccessorList(id, lambda source, destination, edge_data: edge_data.get('entity') == 'Frame')
            D.nextIds=getSuccessorList(id)
            G.DismantleList.append(D)
            G.ObjList.append(D)
            
        elif objClass=='Dream.Conveyer':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            length=float(element.get('length') or 10)
            speed=float(element.get('speed') or 1)
            C=Conveyer(id, name, length, speed)
            C.nextIds=getSuccessorList(id)
            G.ObjList.append(C)
            G.ConveyerList.append(C)
              
        elif objClass=='Dream.BatchDecomposition':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element['processingTime']
            distributionType=processingTime['distributionType']
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            numberOfSubBatches=int(element.get('numberOfSubBatches') or 0)
            BD=BatchDecomposition(id, name, distribution=distributionType,  numberOfSubBatches=numberOfSubBatches,
                                                    mean=mean,stdev=stdev,min=min,max=max)
            BD.nextIds=getSuccessorList(id)
            G.BatchDecompositionList.append(BD)
            G.ObjList.append(BD)       

        elif objClass=='Dream.BatchDecompositionStartTime':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            numberOfSubBatches=int(element.get('numberOfSubBatches') or 0)
            BD=BatchDecompositionStartTime(id, name, distribution=distributionType,  numberOfSubBatches=numberOfSubBatches,
                                                    mean=mean,stdev=stdev,min=min,max=max)
            BD.nextIds=getSuccessorList(id)
            G.BatchDecompositionList.append(BD)
            G.ObjList.append(BD) 

            
        elif objClass=='Dream.BatchReassembly':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            numberOfSubBatches=int(element.get('numberOfSubBatches') or 0)
            BR=BatchReassembly(id, name, distribution=distributionType,  numberOfSubBatches=numberOfSubBatches,
                                                    mean=mean,stdev=stdev,min=min,max=max)
            BR.nextIds=getSuccessorList(id)
            G.BatchReassemblyList.append(BR)
            G.ObjList.append(BR)       
            
        elif objClass=='Dream.LineClearance':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            capacity=int(element.get('capacity') or 1)
            isDummy=bool(int(element.get('isDummy') or 0))
            schedulingRule=element.get('schedulingRule', 'FIFO')
            LC=LineClearance(id, name, capacity, isDummy, schedulingRule=schedulingRule)
            LC.nextIds=getSuccessorList(id)
            G.LineClearanceList.append(LC)
            G.ObjList.append(LC)
            
        elif objClass=='Dream.OperatedMachine':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime', {})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            
            operationType=element.get('operationType','not found')
            setupTime = element.get('setupTime',{})
            setupDistribution = setupTime.get('setupDistribution','not found')
            setupMean = float(setupTime.get('setupMean') or 0)
            setupStdev=float(setupTime.get('setupStdev') or 0)
            setupMin=float(setupTime.get('setupMin') or 0)
            setupMax=float(setupTime.get('setupMax') or 0)
            loadTime = element.get('loadTime',{})
            loadDistribution = loadTime.get('loadDistribution','not found')
            loadMean = float(loadTime.get('loadMean') or 0)
            loadStdev = float(loadTime.get('loadStdev') or 0)
            loadMin=float(loadTime.get('loadMin') or 0)
            loadMax=float(loadTime.get('loadMax') or 0)
            
            if len(G.OperatorPoolsList)>0:
                for operatorPool in G.OperatorPoolsList:                    # find the operatorPool assigned to the machine
                    if(id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
                        machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
                                                                            # otherwise only one of them will be taken into account
                    else:
                        machineOperatorPoolList=[]                          # if there is no operatorPool assigned to the machine
            else:                                                           # then machineOperatorPoolList/operatorPool is a list
                machineOperatorPoolList=[]                                  # if there are no operatorsPool created then the 
                                                                            # then machineOperatorPoolList/operatorPool is a list
            if (type(machineOperatorPoolList) is list):                 # if the machineOperatorPoolList is a list
                                                                        # find the operators assigned to it and add them to the list
                for operator in G.OperatorsList:                        # check which operator in the G.OperatorsList
                    if(id in operator.coreObjectIds):                   # (if any) is assigned to operate
                        machineOperatorPoolList.append(operator)        # the machine with ID equal to id
                                                                        # if there is no operator assigned then the list will be empty
#             try:
#                 for operatorPool in G.operatorPoolsList:                    # find the operatorPool assigned to the machine
#                     if(id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
#                         machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
#                                                                             # otherwise only one of them will be taken into account
#             except:
# #                 pass
# #             if len(machineOperatorPoolList)==None:                      # if there is no operatorPool assigned to the machine
#                 machineOperatorPoolList=[]                          # find the operators assigned to it and add them to a list
#                 for operator in G.OperatorsList:                    # check which operator in the G.OperatorsList
#                     if(id in operator.coreObjectIds):               # (if any) is assigned to operate
#                         machineOperatorPoolList.append(operator)    # the machine with ID equal to id
#                                                                     # if there is no operator assigned then the list will be empty

            r='None'
            for repairman in G.RepairmanList:                   # check which repairman in the G.RepairmanList
                if(id in repairman.coreObjectIds):              # (if any) is assigned to repair 
                    r=repairman                                 # the machine with ID equal to id
            
            OM=OperatedMachine(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, #repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max,
                                                    operatorPool=machineOperatorPoolList, operationType=operationType,
                                                    loadDistribution=loadDistribution, setupDistribution=setupDistribution,
                                                    setupMean=setupMean,setupStdev=setupStdev,setupMin=setupMin,setupMax=setupMax,
                                                    loadMean=loadMean,loadStdev=loadStdev,loadMin=loadMin,loadMax=loadMax,
                                                    repairman=r)
            OM.nextIds=getSuccessorList(id)                             # update the nextIDs list of the machine
            G.OperatedMachineList.append(OM)                            # add the machine to the operatedMachines List
            G.MachineList.append(OM)                                    # add machine to global MachineList
            G.ObjList.append(OM)                                        # add machine to ObjList
            
        elif objClass=='Dream.OrderDecomposition':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            OD=OrderDecomposition(id, name)
            G.OrderDecompositionList.append(OD)
            G.ObjList.append(OD)
            
        elif objClass=='Dream.ConditionalBuffer':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            CB=ConditionalBuffer(id, name)
            CB.nextIds=getSuccessorList(id)
            G.QueueList.append(CB)
            G.QueueJobShopList.append(CB)
            G.ConditionalBufferList.append(CB)
            G.ObjList.append(CB)
            
        elif objClass=='Dream.MouldAssemblyBuffer':
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            MAB=MouldAssemblyBuffer(id, name)
            MAB.nextIds=getSuccessorList(id)
            G.QueueList.append(MAB)
            G.QueueJobShopList.append(MAB)
            G.MouldAssemblyBufferList.append(MAB)
            G.ObjList.append(MAB)
            
        elif objClass=='Dream.MouldAssembly':
            from MouldAssembly import MouldAssembly
            id=element.get('id', 'not found')
            name=element.get('name', 'not found')
            processingTime=element.get('processingTime',{})
            distributionType=processingTime.get('distributionType', 'not found')
            mean=float(processingTime.get('mean') or 0)
            stdev=float(processingTime.get('stdev') or 0)
            min=float(processingTime.get('min') or 0)
            max=float(processingTime.get('max') or 0)
            failures=element.get('failures', {})  
            failureDistribution=failures.get('failureDistribution', 'not found')
            MTTF=float(failures.get('MTTF') or 0)
            MTTR=float(failures.get('MTTR') or 0)
            availability=float(failures.get('availability') or 0)
            resetOnPreemption=bool(int(element.get('resetOnPreemption') or 0))
            # type of operation and related times 
            operationType=element.get('operationType','not found')
            setupTime = element.get('setupTime',{})
            setupDistribution = setupTime.get('setupDistribution','not found')
            setupMean = float(setupTime.get('setupMean') or 0)
            setupStdev=float(setupTime.get('setupStdev') or 0)
            setupMin=float(setupTime.get('setupMin') or 0)
            setupMax=float(setupTime.get('setupMax') or 0)
            loadTime = element.get('loadTime',{})
            loadDistribution = loadTime.get('loadDistribution','not found')
            loadMean = float(loadTime.get('loadMean') or 0)
            loadStdev = float(loadTime.get('loadStdev') or 0)
            loadMin=float(loadTime.get('loadMin') or 0)
            loadMax=float(loadTime.get('loadMax') or 0)
            resetOnPreemption=bool(int(element.get('resetOnPreemption') or 0))
            
            if len(G.OperatorPoolsList)>0:
                for operatorPool in G.OperatorPoolsList:                    # find the operatorPool assigned to the machine
                    if(id in operatorPool.coreObjectIds):                   # and add it to the machine's operatorPool
                        machineOperatorPoolList=operatorPool                # there must only one operator pool assigned to the machine,
                                                                            # otherwise only one of them will be taken into account
                    else:
                        machineOperatorPoolList=[]                          # if there is no operatorPool assigned to the machine
            else:                                                           # then machineOperatorPoolList/operatorPool is a list
                machineOperatorPoolList=[]                                  # if there are no operatorsPool created then the 
                                                                            # then machineOperatorPoolList/operatorPool is a list
            if (type(machineOperatorPoolList) is list):                 # if the machineOperatorPoolList is a list
                                                                        # find the operators assigned to it and add them to the list
                for operator in G.OperatorsList:                        # check which operator in the G.OperatorsList
                    if(id in operator.coreObjectIds):                   # (if any) is assigned to operate
                        machineOperatorPoolList.append(operator)        # the machine with ID equal to id
                                                                        # if there is no operator assigned then the list will be empty
            r='None'
            for repairman in G.RepairmanList:
                if(id in repairman.coreObjectIds):
                    r=repairman
                    
            MA=MouldAssembly(id, name, 1, distribution=distributionType,  failureDistribution=failureDistribution,
                                                    MTTF=MTTF, MTTR=MTTR, availability=availability, #repairman=r,
                                                    mean=mean,stdev=stdev,min=min,max=max,
                                                    operatorPool=machineOperatorPoolList, operationType=operationType,
                                                    loadDistribution=loadDistribution, setupDistribution=setupDistribution,
                                                    setupMean=setupMean,setupStdev=setupStdev,setupMin=setupMin,setupMax=setupMax,
                                                    loadMean=loadMean,loadStdev=loadStdev,loadMin=loadMin,loadMax=loadMax,
                                                    repairman=r, resetOnPreemption=resetOnPreemption)
            MA.nextIds=getSuccessorList(id)
            G.MachineJobShopList.append(MA)
            G.MachineList.append(MA)
            G.MouldAssemblyList.append(MA)
            if MA.operatorPool!="None":
                G.OperatedMachineList.append(MA)                 # add the machine to the operatedMachines List
            G.ObjList.append(MA)
            
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
                stop=infinity            
            interval = float(element.get('interval') or 1)
            duration = float(element.get('duration') or 0)
            method = (element.get('method', None))                    # get the method to be run / default None
            method = method.split('.')                                  #the method is given as 'Path.MethodName'
            method=getattr(str_to_class(method[0]),method[1])           #and then parsed with getattr
            argumentDict=(element.get('argumentDict', {}))      # get the arguments of the method as a dict / default {}
               
            EV = EventGenerator(id, name, start=start, stop=stop, interval=interval, 
                                duration=duration, method=method, argumentDict=argumentDict)       # create the EventGenerator object
                                                                    # calling the getSuccessorList() method on the repairman
            G.EventGeneratorList.append(EV)                               # add the Event Generator to the RepairmanList
            
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
    for element in G.ObjList:
        element.initialize()
    for repairman in G.ModelResourceList:
        repairman.initialize()
    for entity in G.EntityList:
        entity.initialize()
    for ev in G.EventGeneratorList:
        ev.initialize()
    for oi in G.ObjectInterruptionList:
        oi.initialize()

# ===========================================================================
#                        activates all the objects
# ===========================================================================
def activateObjects():
    for element in G.ObjList:
        activate(element, element.run())
    for ev in G.EventGeneratorList:
        activate(ev, ev.run())
    for oi in G.ObjectInterruptionList:
        activate(oi, oi.run())

# ===========================================================================
#                reads the WIP of the stations
# ===========================================================================
def createWIP():
    G.JobList=[]
    G.WipList=[]
    G.EntityList=[]  
    G.PartList=[]
    G.OrderComponentList=[]
    G.OrderList=[]
    G.MouldList=[]
    
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
                route = [None for i in range(len(JSONRoute))]       #    variable that holds the argument used in the Job initiation
                                                                    #    hold None for each entry in the 'route' list
                
                for routeentity in JSONRoute:                                          # for each 'step' dictionary in the JSONRoute
                    stepNumber=int(routeentity.get('stepNumber', '0'))                 #    get the stepNumber
                    route[stepNumber]=routeentity
                
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
                route = [None for i in range(len(JSONRoute))]       #    variable that holds the argument used in the Job initiation
                                                                    #    hold None for each entry in the 'route' list
                
                for routeentity in JSONRoute:                                          # for each 'step' dictionary in the JSONRoute
                    stepNumber=int(routeentity.get('stepNumber', '0'))                 #    get the stepNumber
                    route[stepNumber]=routeentity
                
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
                route = [None for i in range(len(JSONRoute))]       #    variable that holds the argument used in the Job initiation
                                                                    #    hold None for each entry in the 'route' list
                
                for routeentity in JSONRoute:                                          # for each 'step' dictionary in the JSONRoute
                    stepNumber=int(routeentity.get('stepNumber', '0'))                 #    get the stepNumber
                    route[stepNumber]=routeentity
                
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
                P.currentStation=object

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
                route = [None for i in range(len(JSONRoute))]       #    variable that holds the argument used in the Job initiation
                                                                    #    hold None for each entry in the 'route' list
                                                                    
                for routeentity in JSONRoute:                                          # for each 'step' dictionary in the JSONRoute
                    stepNumber=int(routeentity.get('stepNumber', '0'))                 #    get the stepNumber
                    route[stepNumber]=routeentity
                
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
                # initiate the Order
                O=Order(id, name, route, priority=priority, dueDate=dueDate,orderDate=orderDate,
                        isCritical=isCritical, basicsEnded=basicsEnded, manager=manager, componentsList=componentsList,
                        componentsReadyForAssembly=componentsReadyForAssembly, extraPropertyDict=extraPropertyDict)
                G.OrderList.append(O)   
                G.WipList.append(O)  
                G.EntityList.append(O)
                G.JobList.append(O)                     
                
# ===========================================================================
#                reads the interruptions of the stations
# ===========================================================================
def createObjectInterruptions():
    G.ObjectInterruptionList=[]
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
            G.ObjectInterruptionList.append(SM)
            G.ScheduledMaintenanceList.append(SM)
        failure=element.get('failures', {})
        # if there are failures assigned 
        # initiate them   
        if len(failure):
            distributionType=failure.get('failureDistribution', 'No')
            if distributionType=='No':
                pass
            else:
                MTTF=float(failure.get('MTTF') or 0)
                MTTR=float(failure.get('MTTR') or 0)
                availability=float(failure.get('availability') or 0)
                victim=Globals.findObjectById(element['id'])
                F=Failure(victim, distributionType, MTTF, MTTR, availability, victim.id, victim.repairman)
                G.ObjectInterruptionList.append(F)
                G.FailureList.append(F)
        # if there is a shift pattern defined 
        # initiate them             
        shift=element.get('shift', {})
        if len(shift):
            victim=Globals.findObjectById(element['id'])
            shiftPattern=list(shift.get('shiftPattern', []))
            endUnfinished=bool(int(shift.get('endUnfinished', 0)))
            SS=ShiftScheduler(victim, shiftPattern, endUnfinished)
            G.ObjectInterruptionList.append(SS)
            G.ShiftSchedulerList.append(SS)
                
# ===========================================================================
#        used to convert a string read from the input to object type
# ===========================================================================
def str_to_class(str):
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
        #logger.info("start run number "+str(i+1)) 
        G.seed+=1
        G.Rnd=Random(G.seed)     
        initialize()                        #initialize the simulation 
        createWIP()
        initializeObjects()
        Globals.setWIP(G.EntityList)        
        activateObjects()
        
        # if the simulation is ran until no more events are scheduled, 
        # then we have to find the end time as the time the last entity ended.
        if G.maxSimTime==-1:
            simulate(until=infinity)    # simulate until there are no more events. 
                                        # If someone does it for a model that has always events, then it will run forever!
            # identify from the exits what is the time that the last entity has ended. 
            endList=[]
            for exit in G.ExitList:
                endList.append(exit.timeLastEntityLeft)
            G.maxSimTime=float(max(endList))    
        #else we simulate until the given maxSimTime
        else:            
            simulate(until=G.maxSimTime)      #simulate until the given maxSimTime
        
        #carry on the post processing operations for every object in the topology       
        for element in G.ObjList:
            element.postProcessing()
            
        #carry on the post processing operations for every model resource in the topology       
        for model_resource in G.ModelResourceList:
            model_resource.postProcessing()       
            
        #output trace to excel      
        if(G.trace=="Yes"):
            ExcelHandler.outputTrace('trace'+str(i))  
    
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
    for model_resource in G.ModelResourceList:
        model_resource.outputResultsJSON()
        
    for job in G.JobList:
        job.outputResultsJSON()
         
    outputJSONString=json.dumps(G.outputJSON, indent=True)
    G.outputJSONFile.write(outputJSONString)
          
    #logger.info("execution time="+str(time.time()-start))
    if input_data:
      return outputJSONString
    
if __name__ == '__main__':
    main()

