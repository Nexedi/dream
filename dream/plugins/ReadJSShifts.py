from copy import copy
import json
import time
import random
import copy
import datetime
from operator import itemgetter

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class ReadJSShifts(plugin.InputPreparationPlugin, TimeSupportMixin):
  """ Input preparation
      reads the shifts from a spreadsheet
  """

  def preprocess(self, data):
    """ reads the shifts from a spreadsheet and updates the interruptions of the corresponding node objects
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
    
    shiftData = data["input"].get("shift_spreadsheet",[])
    nodes = data["graph"]["node"]

    shiftPattern = {} #shift pattern dictionary
    if shiftData:
      shiftData.pop(0)
      #iteration through the raw data to structure it into ManPy config
      for line in shiftData:
        # if all the records of that line are none then continue
        if any(record==None for record in line):
          continue        
        #if no shift start was given, assume standard 8:00
        startTime = line[2]
        if startTime == '':
          startTime = "08:00"
        shiftStart = self.convertToSimulationTime(strptime("%s %s" % (line[1], startTime), '%Y/%m/%d %H:%M'))
        #if no shift end was given, assume standard 18:00
        endTime = line[3]
        if endTime == '':
          endTime = "18:00"
        shiftEnd = self.convertToSimulationTime(strptime("%s %s" % (line[1], endTime), '%Y/%m/%d %H:%M'))
        #if it is the current row is an extended row for the information belonging to a resource, and no resource name is entered
        entityID = line[0].split("-")[0]
        if str(entityID) == '': 
          #take it as a continuation for the last entered resource
          shiftPattern[lastrec].append([shiftStart,shiftEnd])
        #if resource name is defined
        elif str(entityID) not in shiftPattern:
          #take the name of the last entered resource from here
          lastrec = str(entityID)
          shiftPattern[str(entityID)] = [[shiftStart,shiftEnd]]
        #to avoid overwriting existing records, if there is another entry for a resource but does not follow it immediately (e.g. W2-FS)
        else:
          lastrec = str(entityID)
          #extend the previous entry for the resource
          shiftPattern[str(entityID)].append([shiftStart,shiftEnd])

      #sorts the list in case the records were not entered in correct ascending order
      for info in shiftPattern:
          shiftPattern[info].sort(key=itemgetter(0))
      
      for node, node_data in nodes.items():
        if node in shiftPattern:
          interruptions = node_data.get("interruptions", {})
          if not interruptions:
            node_data["interruptions"] = {}
          node_data["interruptions"]["shift"] = {"shiftPattern": shiftPattern.pop(node),
                                                 "endUnfinished": 0}
	
    return data