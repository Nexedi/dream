from copy import copy
import json
import time
import random
import operator
import datetime
import copy

from dream.plugins import plugin
from dream.plugins.JobShop import ReadJSWorkPlan
from dream.plugins.TimeSupport import TimeSupportMixin

class ReadJSWIP(ReadJSWorkPlan.ReadJSWorkPlan, TimeSupportMixin):
  """ Input preparation
      reads the wip from the spreadsheet and inserts it to the BOM
  """

  def preprocess(self, data):
    """ inserts the wip as introduced in the GUI to the BOM
    """
    self.data = data
    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
      [nowDate, nowTime] = data['general']['currentDate'].split(" ")
      now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
      data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
      nowDate = data['general']['currentDate']
      nowTime = str(datetime.datetime.now().hour)+":"+str(datetime.datetime.now().minute)
      now = strptime(data['general']['currentDate'], '%Y/%m/%d')
      data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    
    WIPdata = data["input"].get("wip_spreadsheet",[])
    BOM = data["input"].get("BOM",{})
    if not BOM:
      BOM = data["input"]["BOM"] = {}
    wip = BOM.get("WIP",{})
    if not wip:
      wip = data["input"]["BOM"]["WIP"] = {}
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
        # calculate the time that the part has been already processed for
        startTime = self.convertToSimulationTime(strptime("%s %s" % (nowDate, WIPitem[5]), '%Y/%m/%d %H:%M'))
        currentTime = self.convertToSimulationTime(strptime("%s %s" % (nowDate, nowTime), '%Y/%m/%d %H:%M'))
        elapsedTime = currentTime - startTime
        # find the processing time of part for the WP_id
        part = self.findEntityByID(partID)
        assert part, "the parts must already be defined before calculating the remaining processing time"
        route = part.get("route",[])
        for step in route:
          if step["task_id"] == WP_id:
            processingTime = step.get("processingTime", {"Fixed":{"meam":0}})
            # the distribution of the processing time is supposed to be fixed (see ReadJSWorkPlan))
            processingTime = float(processingTime["Fixed"].get("mean",0))
        # calculate the remaining Processing Time
        remainingProcessingTime = processingTime - elapsedTime
        assert remainingProcessingTime>=0, "the remaining processing cannot be negative"
        wip[partID] = {
          "task_id": WP_id,
          "operator": operatorID,
          "station": stationID,
          "remainingProcessingTime": remainingProcessingTime,
          "sequence": sequence
        }
    return data
    
    
