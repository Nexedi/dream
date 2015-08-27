from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin
from dream.KnowledgeExtraction.PilotCases.BatchModel.WIPExtraction import main as KEtoolWIP


class BatchesWIPKEtool(plugin.InputPreparationPlugin):
    """ Input preparation 
        reads the WIP from the short format
    """

    def preprocess(self, data):
        # if the WIP data is to be defined manually just return
        if data['general'].get('wipSource',None)=='Manually':
            return data
    
        nodes=data['graph']['node']
        
        # get the number of units for a standard batch
        standardBatchUnits=0
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchSource':
                standardBatchUnits=int(node['batchNumberOfUnits']) 
            node['wip']=[]
            
        data_uri_encoded_input_data = data['input'].get(self.configuration_dict['input_id'], {})
        try:
            wipData=KEtoolWIP(data_uri_encoded_input_data)
        except TypeError:
            return data
        for batchId,stationId in wipData.iteritems():
            nextBufferId=self.getNextBuffer(data, stationId)      
            if not nextBufferId:
                continue     
            subline=self.checkIfSubline(data, stationId)
                      
            # for stations that we have to create sub-batches
            if subline and (not self.checkIfNextStationIsReassembly(data, stationId)):
                workingBatchSize=nodes[stationId]['workingBatchSize']
                numberOfSubBatches=standardBatchUnits/workingBatchSize
                
                for i in range(numberOfSubBatches):
                    data['graph']['node'][nextBufferId]['wip'].insert(0,{
                          "_class": 'Dream.SubBatch',
                          "id": 'Batch_'+str(batchId)+'_SB_'+str(i)+'_wip', 
                          "name":'Batch_'+str(batchId)+'_SB_'+str(i)+'_wip', 
                          "numberOfUnits":int(standardBatchUnits/numberOfSubBatches),
                          "parentBatchId":'Batch_'+str(batchId),
                          "parentBatchName":'Batch_'+str(batchId)                           
                    })
            # for stations that we have to create batches                                                                       
            else:
                data['graph']['node'][nextBufferId]['wip'].insert(0,{
                      "_class": 'Dream.Batch',
                      "id": 'Batch_'+str(batchId),
                      "name":'Batch_'+str(batchId), 
                      "numberOfUnits":int(standardBatchUnits)
                })               
        return data    
        
        
    # returns true if the station is in a subline
    def checkIfSubline(self,data,stationId):       
        nodes=data['graph']['node']
        current=stationId
        # find all the predecessors that may share batches
        while 1:
            previous=self.getPredecessors(data, current)[0]
            # when a decomposition is reached break  
            if 'Decomposition' in nodes[previous]['_class']:
                return True
            if 'Reassembly' in nodes[previous]['_class']:
                return False
            current=previous     
    
    # returns true if the station is reassembly       
    def checkIfNextStationIsReassembly(self,data,stationId):   
        nodes=data['graph']['node']
        next=self.getSuccessors(data, stationId)[0]
        if 'Reassembly' in nodes[next]['_class']:
            return True
        return False
    
    def getNextBuffer(self,data,stationId):
        nodes=data['graph']['node']
        current=stationId
        # find all the successors that may share batches
        while 1:
            next=self.getSuccessors(data, current)[0]   
            if 'Queue' in nodes[next]['_class'] or 'Clearance' in nodes[next]['_class']:     
                return next
            if 'Exit' in nodes[next]['_class']:
                return None
            current=next 
        
        