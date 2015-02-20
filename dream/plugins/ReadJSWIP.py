from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class ReadJSWIP(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the wip from the spreadsheet and inserts it to the BOM
  """

  def preprocess(self, data):
    """ inserts the wip as introduced in the GUI to the BOM
    """
    WIPdata = data["input"].get("wip_spreadsheet",[])
    workPlanData = data["input"].get("workplan_spreadsheet",[])
    try:
      BOM = data["input"]["BOM"]
    except:
      BOM = data["input"]["BOM"]={}
    try:
      wip = BOM["WIP"]
    except:
      wip = BOM["WIP"] = {}
    if WIPdata:
      WIPdata.pop(0)  # pop the column names
      for WIPitem in WIPdata:
        partID = WIPitem[0]
        if not partID:
          continue
        stationID = WIPitem[3]
        operatorID = WIPitem[4]
        sequence = WIPitem[1]
        WP_id = WIPitem[2]
        start = WIPitem[5]
        # end = WIPitem[6]
        wip[partID] = {
          "task_id": WP_id,
          "operator": operatorID,
          "station": stationID,
          "entry": start,
          "exit": end,
          "sequence": sequence
        }
    return data
    
    '''
    {
			"name": "Part ID",
      "type": "string"
    }, {
      "name": "Sequence",
      "type": "string"
    }, {
      "name": "task ID",
      "type": "string"
    }, {
      "name": "Station ID",
      "type": "string"
    }, {
      "name": "Personnel ID",
      "type": "string"
    }, {
      "name": "Start time",
      "type": "string",
      "format": "date-time"
    }
  '''