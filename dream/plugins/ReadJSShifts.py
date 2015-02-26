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
  
  def correctTimePair(self, start, end):
    '''takes a pair of times and returns the corrected pair according to the current time'''
    # if the end of shift shift already finished we do not need to consider in simulation
    if start<0 and end<=0:
      return None
    # if the start of the shift is before now, set the start to 0
    if start<0:
      start=0
    # sometimes the date may change (e.g. shift from 23:00 to 01:00). 
    # these would be declared in the date of the start so add a date (self.timeUnitPerDay) to the end
    if end<start:
      end+=self.timeUnitPerDay
    return (start, end)

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
        toContinue = False
        for record in line:
          if record != None:
            toContinue = True
            break
        if not toContinue:
          continue
        # list to hold the working intervals start times
        timeStartList = []
        # list to hold the working intervals end times
        timeEndList = []
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
        timePair = self.correctTimePair(shiftStart, shiftEnd)
        if not timePair:
          continue
        else:
          shiftStart, shiftEnd = timePair
          timeStartList.append(shiftStart)
          timeEndList.append(shiftEnd)

        if line[-1]:
          offshifts = line[-1].replace(" ", "").split(";")
          for offshift in offshifts:
            limits = offshift.split("-")
            breakStart = self.convertToSimulationTime(strptime("%s %s" % (line[1], limits[0]), '%Y/%m/%d %H:%M'))
            breakEnd = self.convertToSimulationTime(strptime("%s %s" % (line[1], limits[1]), '%Y/%m/%d %H:%M'))
            timePair = self.correctTimePair(breakStart, breakEnd)
            if not timePair:
              continue
            else:
              breakStart, breakEnd = timePair
              timeStartList.append(breakEnd)
              timeEndList.insert(0, breakStart)

        #if it is the current row is an extended row for the information belonging to a resource, and no resource name is entered
        entityID = line[0].split("-")[0]
        if str(entityID) == '': 
          #take it as a continuation for the last entered resource
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            shiftPattern[lastrec].append([start, end])
        #if resource name is defined
        elif str(entityID) not in shiftPattern:
          #take the name of the last entered resource from here
          lastrec = str(entityID)
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            shiftPattern[lastrec] = [[start, end]]
        #to avoid overwriting existing records, if there is another entry for a resource but does not follow it immediately (e.g. W2-FS)
        else:
          lastrec = str(entityID)
          #extend the previous entry for the resource
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            shiftPattern[lastrec].append([start, end])

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