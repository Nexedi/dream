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
    wipData=data['input'].get('wip_spreadsheet', None)
    nodes=data['graph']['node']

    # get the number of units for a standard batch
    standardBatchUnits=0
    for node_id, node in nodes.iteritems():
        if node['_class']=='Dream.BatchSource':
            standardBatchUnits=int(node['numberOfUnits']) 

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
        # if the wip is in a server
        else:
            workingBatchSize=int(nodes[stationId].get(('workingBatchSize'), standardBatchUnits))
            print stationId, workingBatchSize
    return data