from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy
import routeQuery

from dream.plugins import plugin

class ReadJSWIP(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the wip from the spreadsheet and inserts it to the BOM
  """

  def preprocess(self, data):
    """ inserts the wip as introduced in the GUI to the BOM
    """
    WIPdata = data["input"]["wip_spreadsheet"]
    wip = data["input"]["BOM"]["WIP"]
    if WIPdata:
      WIPdata.pop(0)  # pop the column names
      for WIPitem in WIPdata:
        partID = WIPitem[0]
        if not partID:
          continue
        stationID = WIPitem[1]
        operatorID = WIPitem[2]
        sequence = WIPitem[3]
        WP_id = WIPitem[4]
        start = WIPitem[5]
        end = WIPitem[6]
        wip[partID] = {
          "task_id": WP_id,
          "operator": operatorID,
          "station": stationID,
          "entry": start,
          "exit": end,
          "sequence": sequence
        }
    return data