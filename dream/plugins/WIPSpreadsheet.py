from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class WIPSpreadsheet(plugin.InputPreparationPlugin):
  """ Input prepration 
      read wip-srpeadsheet data and update the wip property of the stations.
  """

  def preprocess(self, data):
    """ Set the WIP in queue from spreadsheet data.
    """
    wipData=data['input'].get('wip_spreadsheet', None)
    node=data['graph']['node']
    if wipData:
      wipData.pop(0)  # pop the column names
      for wipItem in wipData:
        partId=wipItem[0]
        # in case there is no id, do not process the element
        if not partId:
          continue
        stationId=wipItem[1]
        remainingProcessingTime=wipItem[2]
        wip=node[stationId].get('wip',[])
        if not wip:
          node[stationId]['wip']=[]
        node[stationId]['wip'].append({
          "_class": "Dream.Part",
          "id": partId, 
          "name": partId,
          "remainingProcessingTime":{"Fixed":{"mean":remainingProcessingTime}}
        })
    return data