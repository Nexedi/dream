from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class BatchesWIPSpreadsheet(plugin.InputPreparationPlugin):
  """ Input prepration 
      read wip-srpeadsheet data and update the wip property of the stations.
  """

  def preprocess(self, data):
    """ Set the WIP in queue from spreadsheet data.
    """
    # if the WIP data is to be read by KE tool just return
    if data['general'].get('wipSource',None)=='By KE':
        return data
    
    wipData=data['input'].get('wip_spreadsheet', None)
    nodes=data['graph']['node']

    # get the number of units for a standard batch
    standardBatchUnits=0
    for node_id, node in nodes.iteritems():
        if node['_class']=='Dream.BatchSource':
            standardBatchUnits=int(node['batchNumberOfUnits']) 
        node['wip']=[]

    if wipData:
      wipData.pop(0)  # pop the column names
      for wipItem in wipData:
        partId=wipItem[0]
        # in case there is no id, do not process the element
        if not partId:
          continue
        stationId=wipItem[1]
        numberOfUnits=wipItem[2]
        unitsToProcess=wipItem[3]
        if not unitsToProcess:
            unitsToProcess=numberOfUnits
        _class="Dream."+wipItem[4]
        parentBatchId=wipItem[5]
        
        wip=nodes[stationId].get('wip',[])
        if not wip:
          nodes[stationId]['wip']=[]
        stationClass=nodes[stationId]['_class']
        
        # if the wip is in a buffer
        if stationClass in ['Dream.RoutingQueue', 'Dream.Queue', 'Dream.LineClearance']:
            wipDict={
              "_class": _class,
              "id": partId, 
              "name": 'Batch_'+partId+'_wip',
              "numberOfUnits":numberOfUnits,
            }  
            if parentBatchId:
                wipDict['parentBatchId']=parentBatchId
                wipDict['name']='Batch'+parentBatchId+'_SB'+partId+'wip'
            nodes[stationId]['wip'].append(wipDict)
        # if the wip is in a decomposition
        elif 'Decomposition' in stationClass:
            wipDict={
              "_class": _class,
              "id": partId, 
              "name": 'Batch_'+partId+'_wip',
              "numberOfUnits":numberOfUnits,
              "parentBatchId":parentBatchId,
              "name":'Batch'+parentBatchId+'_SB'+partId+'wip'
              }         
            nodes[stationId]['wip'].append(wipDict)
        # if the wip is in a server
        else:
            workingBatchSize=int(nodes[stationId].get(('workingBatchSize'), standardBatchUnits))
            nextObject=self.getSuccessors(data, stationId)[0]
            previousObject=self.getPredecessors(data, stationId)[0]
            
            # if the station has inherent decomposition/reassembly
            if nodes[nextObject]['_class'].startswith('Dream.BatchReassembly')\
                and nodes[previousObject]['_class'].startswith('Dream.BatchDecomposition'):
                sbId=0
                SBinReassembly=(int(numberOfUnits)-int(unitsToProcess))/workingBatchSize
                SBinDecomposition=int(unitsToProcess)/workingBatchSize
                for i in range(SBinReassembly):
                    nodes[nextObject]['wip'].append({
                      "_class": 'Dream.SubBatch',
                      "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                      "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                      "numberOfUnits":workingBatchSize,  
                      "parentBatchId":partId,
                      "parentBatchName":'Batch'+partId+"WIP"                    
                    })
                    sbId+=1  
                remainingUnitsInWorkingBatch=int(unitsToProcess) % workingBatchSize
                if remainingUnitsInWorkingBatch:
                    nodes[stationId]['wip'].append({
                          "_class": 'Dream.SubBatch',
                          "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                          "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                          "numberOfUnits":workingBatchSize,  
                          "parentBatchId":partId,
                          "unitsToProcess": remainingUnitsInWorkingBatch, 
                          "parentBatchName":'Batch'+partId+"WIP"                                                
                    })       
                    sbId+=1   
                for i in range(SBinDecomposition):
                    nodes[previousObject]['wip'].append({
                      "_class": 'Dream.SubBatch',
                      "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                      "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                      "numberOfUnits":workingBatchSize,  
                      "parentBatchId":partId,
                      "parentBatchName":'Batch'+partId+"WIP"                    
                    })
                    sbId+=1            
            # if the station is after routing queue and before reassembly
            elif nodes[nextObject]['_class'].startswith('Dream.BatchReassembly')\
                and nodes[previousObject]['_class'].startswith('Dream.RoutingQueue'):    
                sbId=0
                SBinReassembly=(int(numberOfUnits)-int(unitsToProcess))/workingBatchSize
                SBinDecomposition=int(unitsToProcess)/workingBatchSize
                for i in range(SBinReassembly):
                    nodes[nextObject]['wip'].append({
                      "_class": 'Dream.SubBatch',
                      "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                      "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                      "numberOfUnits":workingBatchSize,  
                      "parentBatchId":partId,
                      "parentBatchName":'Batch'+partId+"WIP"                    
                    })
                    sbId+=1  
                remainingUnitsInWorkingBatch=int(unitsToProcess) % workingBatchSize
                if remainingUnitsInWorkingBatch:
                    nodes[stationId]['wip'].append({
                          "_class": 'Dream.SubBatch',
                          "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                          "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                          "numberOfUnits":workingBatchSize,  
                          "parentBatchId":partId,
                          "unitsToProcess": remainingUnitsInWorkingBatch, 
                          "parentBatchName":'Batch'+partId+"WIP"                                                
                    })       
                    sbId+=1   
                for i in range(SBinDecomposition):
                    nodes[previousObject]['wip'].append({
                      "_class": 'Dream.SubBatch',
                      "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                      "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                      "numberOfUnits":workingBatchSize,  
                      "parentBatchId":partId,
                      "parentBatchName":'Batch'+partId+"WIP",          
                      "receiver":stationId          
                    })
                    sbId+=1            
            # if the station is after batch decomposition and before routing queue
            elif nodes[nextObject]['_class'].startswith('Dream.RoutingQueue')\
                and nodes[previousObject]['_class'].startswith('Dream.BatchDecomposition'): 
                sbId=0
                SBinReassembly=(int(numberOfUnits)-int(unitsToProcess))/workingBatchSize
                SBinDecomposition=int(unitsToProcess)/workingBatchSize
                for i in range(SBinReassembly):
                    nodes[nextObject]['wip'].append({
                      "_class": 'Dream.SubBatch',
                      "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                      "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                      "numberOfUnits":workingBatchSize,  
                      "parentBatchId":partId,
                      "parentBatchName":'Batch'+partId+"WIP"                    
                    })
                    sbId+=1  
                remainingUnitsInWorkingBatch=int(unitsToProcess) % workingBatchSize
                if remainingUnitsInWorkingBatch:
                    nodes[stationId]['wip'].append({
                          "_class": 'Dream.SubBatch',
                          "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                          "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                          "numberOfUnits":workingBatchSize,  
                          "parentBatchId":partId,
                          "unitsToProcess": remainingUnitsInWorkingBatch, 
                          "parentBatchName":'Batch'+partId+"WIP"                                                
                    })       
                    sbId+=1   
                for i in range(SBinDecomposition):
                    nodes[previousObject]['wip'].append({
                      "_class": 'Dream.SubBatch',
                      "id": 'B_'+partId+'_WIP_SB_'+str(sbId), 
                      "name":'Batch'+partId+'_SubBatch_'+str(sbId)+'_wip',
                      "numberOfUnits":workingBatchSize,  
                      "parentBatchId":partId,
                      "parentBatchName":'Batch_'+partId+"_WIP"                    
                    })
                    sbId+=1         
            # for the stations in the end of a sub-line
            elif nodes[stationId]['_class'] == 'Dream.M3':
                # if there are no more units to process, put the sub-batch in reassembly
                if int(unitsToProcess)==0:
                    nodes[nextObject]['wip'].append({
                      "_class": _class,
                      "id": partId, 
                      "name":'Batch'+parentBatchId+'_SubBatch_'+partId+'_wip',
                      "numberOfUnits":numberOfUnits,  
                      "parentBatchId":parentBatchId,
                      "parentBatchName":'Batch_'+parentBatchId+"_WIP"                    
                    })
                # else put the sub-batch in the station   
                else:
                    nodes[stationId]['wip'].append({
                      "_class": _class,
                      "id": partId, 
                      "name":'Batch'+parentBatchId+'_SubBatch_'+partId+'_wip',
                      "numberOfUnits":numberOfUnits,  
                      "parentBatchId":parentBatchId,
                      "unitsToProcess": unitsToProcess, 
                      "parentBatchName":'Batch_'+parentBatchId+"_WIP"                    
                    })
            # for the stations at the start of a sub-line
            elif nodes[stationId]['_class'] == 'Dream.BatchScrapMachineAfterDecompose':
                # if there are no more units to process, put the sub-batch in reassembly
                if int(unitsToProcess)==workingBatchSize:
                    nodes[previousObject]['wip'].append({
                      "_class": _class,
                      "id": partId, 
                      "name":'Batch'+parentBatchId+'_SubBatch_'+partId+'_wip',
                      "numberOfUnits":numberOfUnits,  
                      "parentBatchId":parentBatchId,
                      "parentBatchName":'Batch_'+parentBatchId+"_WIP"                    
                    })
                # else put the sub-batch in the station   
                else:
                    nodes[stationId]['wip'].append({
                      "_class": _class,
                      "id": partId, 
                      "name":'Batch'+parentBatchId+'_SubBatch_'+partId+'_wip',
                      "numberOfUnits":numberOfUnits,  
                      "parentBatchId":parentBatchId,
                      "unitsToProcess": unitsToProcess, 
                      "parentBatchName":'Batch_'+parentBatchId+"_WIP"                    
                    })
            # if it is a standard BatchScrapMachine
            elif nodes[stationId]['_class'] == 'Dream.BatchScrapMachine':
                if _class=='Dream.SubBatch':
                    nodes[stationId]['wip'].append({
                      "_class": _class,
                      "id": partId, 
                      "name":'Batch'+parentBatchId+'_SubBatch_'+partId+'_wip',
                      "numberOfUnits":numberOfUnits,  
                      "parentBatchId":parentBatchId,
                      "unitsToProcess": unitsToProcess, 
                      "parentBatchName":'Batch_'+parentBatchId+"_WIP"                    
                    })    
                elif _class=='Dream.Batch':            
                    nodes[stationId]['wip'].append({
                      "_class": _class,
                      "id": partId, 
                      "name":'Batch_'+partId+'_wip',
                      "numberOfUnits":numberOfUnits,  
                      "unitsToProcess": unitsToProcess, 
                    })         
    return data