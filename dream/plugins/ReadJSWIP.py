from copy import copy
import json
import time
import random
import operator
import datetime
import copy

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class ReadJSWIP(plugin.InputPreparationPlugin, TimeSupportMixin):
  """ Input preparation
      reads the wip from the spreadsheet and inserts it to the BOM
  """

  def preprocess(self, data):
    """ inserts the wip as introduced in the GUI to the BOM
    """
    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
      data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d')
      data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    
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
        # start = WIPitem[5]
        start = self.convertToSimulationTime(strptime("%s %s" % (data['general']['currentDate'], WIPitem[5]), '%Y/%m/%d %H:%M'))
        remainingProcessinTime = start - now
        wip[partID] = {
          "task_id": WP_id,
          "operator": operatorID,
          "station": stationID,
          "remainingProcessinTime": remainingProcessing,
          "sequence": sequence
        }
    return data
    
    