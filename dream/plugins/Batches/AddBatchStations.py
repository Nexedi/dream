from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class AddBatchStations(plugin.InputPreparationPlugin):
    """ Input preparation 
        checks if the Batch Station processes Batchs or SubBatches and in the former case adds a decomposition/reassembly 
        to set to the working batch
    """

    def preprocess(self, data):
        nodes=copy(data['graph']['node'])
        edges=copy(data['graph']['edge'])

        # get the number of units for a standard batch
        standardBatchUnits=0
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchSource':
                standardBatchUnits=int(node['batchNumberOfUnits'])    
                
        # loop through all the objects and set that the name will be equal to the id
        for node_id, node in nodes.iteritems():
            node['name']=node_id
        
        # loop in BatchScrapMachines to change the classes if need be       
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchScrapMachine':
                # get the first successor. If it is BatchReassembly set the class to M3
                successorIdList=self.getSuccessors(data, node_id)
                if successorIdList:
                    successorId=successorIdList[0]
                    successorClass=nodes[successorId]['_class']
                    if successorClass=='Dream.BatchReassembly':
                        data['graph']['node'][node_id]['_class']='Dream.M3'
                # get the first predecessor. If it is BatchDecomposition set the class to BatchScrapMachineAfterDecompose
                predecessorIdList=self.getPredecessors(data, node_id)
                if predecessorIdList:
                    predecessorId=predecessorIdList[0]
                    predecessorClass=nodes[predecessorId]['_class']
                    if predecessorClass=='Dream.BatchDecomposition':
                        data['graph']['node'][node_id]['_class']='Dream.BatchScrapMachineAfterDecompose'

        # loop through the nodes to find the machines that do need addition
        machinesThatNeedAddition={}
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchScrapMachine' and self.checkIfMachineNeedsAddition(data,node_id,standardBatchUnits):
                machinesThatNeedAddition[node_id]=node
               
        # loop in BatchDecompositions to change the classes to BatchDecompositionBlocking   
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchDecomposition':
                data['graph']['node'][node_id]['_class']='Dream.BatchDecompositionBlocking'
                
        # loop in BatchReassemblies to change the classes to BatchReassemblyBlocking   
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchReassembly':
                data['graph']['node'][node_id]['_class']='Dream.BatchReassemblyBlocking'
                data['graph']['node'][node_id]['outputResults']=1
            
        # loop in BatchDecompositions to change the classes to BatchDecompositionStartTime for the ones that 
        # are just after the source   
        # XXX this is not generic. In the future the user may have to define it  
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchDecompositionBlocking':
                predecessorId=self.getPredecessors(data, node_id)[0]
                predecessorClass=nodes[predecessorId]['_class']
                if predecessorClass=='Dream.BatchSource':
                    data['graph']['node'][node_id]['_class']='Dream.BatchDecompositionStartTime'
   
        # loop through the nodes
        for node_id, node in machinesThatNeedAddition.iteritems():
            # find BatchScrapMachines that process batches
            import math
            workingBatchSize=int((node.get('workingBatchSize')))
            numberOfSubBatches=int((math.ceil((standardBatchUnits/float(workingBatchSize)))))
            
            #create a batchDecomposition
            batchDecompositionId=node_id+'_D'
            data['graph']['node'][batchDecompositionId]={
                "name": batchDecompositionId,
                "processingTime": {
                     "Fixed": {
                          "mean": 0
                     }
                }, 
                "numberOfSubBatches": numberOfSubBatches, 
                "wip": [],
                "element_id": "DreamNode_39", 
                "_class": "Dream.BatchDecompositionBlocking", 
                "id": batchDecompositionId                                                            
            }
            #put the batchDecomposition between the predecessor and the node
            for edge_id, edge in edges.iteritems():
                if edge['destination']==node_id:
                    source=edge['source']
                    # remove the edge
                    data['graph']['edge'].pop(edge_id,None)
                    # add an edge from source to batchDecomposition
                    self.addEdge(data, source, batchDecompositionId)
                    # add an edge from batchDecomposition machine
                    self.addEdge(data, batchDecompositionId, node_id)
            #create a batchReassembly
            batchReassemblyId=node_id+'_R'
            data['graph']['node'][batchReassemblyId]={
                "name": batchReassemblyId, 
                "processingTime": {
                     "Fixed": {
                          "mean": 0
                     }
                }, 
                "outputResults": 1, 
                "numberOfSubBatches": numberOfSubBatches, 
                "wip": [],
                "_class": "Dream.BatchReassemblyBlocking", 
                "id": batchReassemblyId
            }
            #put the batchReassembly between the node and the successor
            for edge_id, edge in edges.iteritems():
                if edge['source']==node_id:
                    destination=edge['destination']
                    # remove the edge
                    data['graph']['edge'].pop(edge_id,None)
                    # add an edge from machine to batchReassembly
                    self.addEdge(data, node_id, batchReassemblyId)
                    # add an edge from batchReassembly to destination
                    self.addEdge(data, batchReassemblyId, destination)             

        # set all the Queue types to gether wip data
        for node in data["graph"]["node"].values():
            if node['_class'] in ['Dream.Queue', 'Dream.LineClearance', 'Dream.RoutingQueue']:
                node['gatherWipStat'] = 1


        return data

    # returns true if it is needed to add decomposition/reassembly
    def checkIfMachineNeedsAddition(self, data, machineId,standardBatchUnits):
        nodes=copy(data['graph']['node']) 
        workingBatchSize=(nodes[machineId].get('workingBatchSize',standardBatchUnits))
        if workingBatchSize:
            workingBatchSize=int(workingBatchSize)
        else:   # if the workingBatchSize is not defined by the user set it to standardBatchUnits
            workingBatchSize=standardBatchUnits
        # if the workingBatchSize is equal or higher to standardBatchUnits we do not need to add decomposition/reassembly
        if workingBatchSize>=standardBatchUnits:
             return False   
        # loop in the predecessors   
        currentId=machineId
        while 1:
            predecessorIdsList=self.getPredecessors(data, currentId)
            # get the first. In this model every machine is fed by one point
            if predecessorIdsList:
                predecessorId=predecessorIdsList[0]
            # if there is no predecessor, i.e. the start was reached break
            else:
                break
            predecessorClass=nodes[predecessorId]['_class']
            # if BatchDecomposition is reached we are in subline so return False
            if predecessorClass=='Dream.BatchDecomposition':
                return False
            # if BatchReassembly is reached we are not in subline so return True
            elif predecessorClass=='Dream.BatchReassembly':
                return True    
            currentId=predecessorId 
        return True
    