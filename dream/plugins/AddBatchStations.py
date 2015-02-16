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
        data_uri_encoded_input_data = data['input'].get(self.configuration_dict['input_id'], {})  
              
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchScrapMachine' and self.checkIfMachineProcessesBatches(node_id):
                #create a batchDecomposition
                batchDecompositionId=node_id+'_D'
                data['graph']['node'][batchDecompositionId]={
                    "name": batchDecompositionId,
                    "processingTime": {
                         "Fixed": {
                              "mean": 0
                         }
                    }, 
                    "numberOfSubBatches": 8, 
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
                        data['graph']['edge'][source+'_to_'+batchDecompositionId]={
                            "source": source, 
                            "destination": batchDecompositionId, 
                            "data": {}, 
                            "_class": "Dream.Edge"                                                                  
                        }
                        # add an edge from batchDecomposition machine
                        data['graph']['edge'][batchDecompositionId+'_to_'+node_id]={
                            "source": batchDecompositionId, 
                            "destination": node_id, 
                            "data": {}, 
                            "_class": "Dream.Edge"                                                                  
                        }                
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
                    "numberOfSubBatches": 8, 
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
                        # add an edge from node to destination
                        data['graph']['edge'][node_id+'_to_'+batchReassemblyId]={
                            "source": node_id, 
                            "destination": batchReassemblyId, 
                            "data": {}, 
                            "_class": "Dream.Edge"                                                                  
                        }
                        # add an edge from batchDecomposition machine
                        data['graph']['edge'][batchReassemblyId+'_to_'+destination]={
                            "source": batchReassemblyId, 
                            "destination": destination, 
                            "data": {}, 
                            "_class": "Dream.Edge"                                                                  
                        }                   
#         dataString=json.dumps(data['graph']['edge'], indent=5)
#         print dataString
        return data

    # returns true is a machine processes full batches
    def checkIfMachineProcessesBatches(self, machinId_id):
        # dummy implementation for now
        return True
    