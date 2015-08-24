from copy import copy
import json
import math
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
      # calculate the hours to end the first day
      hoursToEndFirstDay = datetime.datetime.combine(now.date(), datetime.time(23,59,59)) - datetime.datetime.combine(now.date(), now.time())
      data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d')
      hoursToEndFirstDay = datetime.time(23,59,59)
      data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    
    shiftData = data["input"].get("shift_spreadsheet",[])
    nodes = data["graph"]["node"]

    defaultShiftPattern = {} #default shift pattern dictionary (if no pattern is defined for certain dates)
    exceptionShiftPattern = {} # exceptions for shift pattern dictionary as defined in the spreadsheet
    
    if shiftData:
      shiftData.pop(0)
      #iteration through the raw data to structure it into ManPy config
      lastrec=None
      for line in shiftData:
        # if all the records of that line are none then continue
        toContinue = False
        for record in line:
          if record != None and record!='':
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
        if startTime == '' or startTime == None:
          startTime = "08:00"
        shiftStart = self.convertToSimulationTime(strptime("%s %s" % (line[1], startTime), '%Y/%m/%d %H:%M'))
        #if no shift end was given, assume standard 18:00
        endTime = line[3]
        if endTime == '' or endTime == None:
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
        # sort the list before proceeding
        timeEndList.sort()
        timeStartList.sort()
        #if it is the current row is an extended row for the information belonging to a resource, and no resource name is entered
        if line[0]:
          entityID = line[0].split("-")[0]
        else:
          entityID = ""  
        if str(entityID) == '': 
          #take it as a continuation for the last entered resource
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            exceptionShiftPattern[lastrec].append([start, end])
        #if resource name is defined
        elif str(entityID) not in exceptionShiftPattern:
          #take the name of the last entered resource from here
          lastrec = str(entityID)
          exceptionShiftPattern[lastrec] = []
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            # if there is no other entry
            if not len(exceptionShiftPattern[lastrec]):
              exceptionShiftPattern[lastrec] = [[start, end]]
            else:
              exceptionShiftPattern[lastrec].append([start, end])
        #to avoid overwriting existing records, if there is another entry for a resource but does not follow it immediately (e.g. W2-FS)
        else:
          lastrec = str(entityID)
          #extend the previous entry for the resource
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            exceptionShiftPattern[lastrec].append([start, end])

      #sorts the list in case the records were not entered in correct ascending order
      for info in exceptionShiftPattern:
        exceptionShiftPattern[info].sort(key=itemgetter(0))

      # ================================================================
      #create default pattern for all operators (10 days long)
      timeStartList = []
      timeEndList = []

      for dayNumber in range(0,20):
        # check the day, if it is weekend do not create shift entry
        dayDate=now+datetime.timedelta(days=dayNumber)
        if dayDate.weekday() in [5,6]:
            continue
        startTime = "08:00"
        endTime = "18:00"
        upDate = now.date()+datetime.timedelta(days=dayNumber)
        shiftStart = self.convertToSimulationTime(strptime("%s %s" % (upDate, startTime), '%Y-%m-%d %H:%M'))
        shiftEnd = self.convertToSimulationTime(strptime("%s %s" % (upDate, endTime), '%Y-%m-%d %H:%M'))
        timePair = self.correctTimePair(shiftStart, shiftEnd)
        shiftStart, shiftEnd = timePair
        timeStartList.append(shiftStart)
        timeEndList.append(shiftEnd)
      #for every operator (can be also machine) create an entry on the defaultShiftPattern 
      for node, node_data in nodes.iteritems():
        #if the node is an operator
        if node_data.get('_class', None) == 'Dream.Operator':
          for index, start in enumerate(timeStartList):
            end = timeEndList[index]
            if not start and not end:
              continue
            if not node in defaultShiftPattern:
              defaultShiftPattern[node] = [[start, end]]
            else:
              defaultShiftPattern[node].append([start, end])
      # ================================================================
      
      for node, node_data in nodes.items():
        if node_data.get('_class', None) == 'Dream.Operator':
          modifiedDefaultDays = [] # the days of the defaultShiftPattern that have been modified according to the exceptionShiftPattern
          if node in exceptionShiftPattern:
            for index1, exception in enumerate(exceptionShiftPattern[node]):
              # XXX think of the case where the exception starts one day and finishes the next
              # calculate the time difference in hours from the end of the first day to the end of the exception
              # check if we are still in the first day
              if hoursToEndFirstDay.total_seconds()/3600 > exception[-1]:
                exceptionDay = 0
              # calculate the number of days till the end of the exception
              else:
                exceptionDay = math.floor((exception[-1] - hoursToEndFirstDay.total_seconds()/3600)/24) + 1
              # check the weekday 
              exceptionDate=now+datetime.timedelta(days=exceptionDay)
              # if it is weekend create shift entry for that date. The default pattern does not need to be changed
              if exceptionDate.weekday() in [5,6]:
                  defaultShiftPattern[node].append(exception)
              # for exceptions in weekdays
              else:                
                  for index2, default in enumerate(defaultShiftPattern[node]):
                    # check if we still are in the first day
                    if hoursToEndFirstDay.total_seconds()/3600 > default[-1]:
                      defaultDay = 0
                    # calculate the number of days till the end of the default shift
                    else:
                      defaultDay = math.floor((default[-1] - hoursToEndFirstDay.total_seconds()/3600)/24) + 1
                    if exceptionDay == defaultDay:
                      # update the defaultShiftPattern of the node (operator or machine)
                      # if the exception day has not been modified then delete the previous entry and use the first exception that occurs
                      if not exceptionDay in modifiedDefaultDays:
                        defaultShiftPattern[node][index2] = exception
                      # otherwise append it at the end 
                      else:
                        defaultShiftPattern[node].append(exception)
                      modifiedDefaultDays.append(exceptionDay) # the day has been modified, add to the modified days
                      break
          # update the interruptions of the nodes that have a defaultShiftPattern
          if node in defaultShiftPattern:
            # sort the shift pattern of every node
            defaultShiftPattern[node].sort(key=itemgetter(0))
            # get the interruptions of the object
            interruptions = node_data.get("interruptions", {})
            if not interruptions:
              node_data["interruptions"] = {}
            node_data["interruptions"]["shift"] = {"shiftPattern": defaultShiftPattern.pop(node),
                                                   "endUnfinished": 0}
	
    return data
