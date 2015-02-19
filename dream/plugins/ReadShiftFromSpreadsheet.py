from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class ReadShiftFromSpreadsheet(plugin.InputPreparationPlugin, TimeSupportMixin):
  """ Input prepration 
      read shift-srpeadsheet data and update the wip property of the stations.
  """

  def preprocess(self, data):
    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
        now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
        data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
        now = strptime(data['general']['currentDate'], '%Y/%m/%d')
        data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    
    shift_by_station = {}
    # XXX machine_shift_spreadsheet should be configuration
    for line in data['input']['machine_shift_spreadsheet'][1:]:
      if line[1]:
        start_time = self.convertToSimulationTime(strptime("%s %s" % (line[0], line[2]), '%Y/%m/%d %H:%M'))
        stop_time = self.convertToSimulationTime(strptime("%s %s" % (line[0], line[3]), '%Y/%m/%d %H:%M'))
        # if the end of shift shift already finished we do not need to consider in simulation
        if start_time<0 and stop_time<=0:
            continue
        # if the start of the shift is before now, set the start to 0
        if start_time<0:
            start_time=0
        # sometimes the date may change (e.g. shift from 23:00 to 01:00). 
        # these would be declared in the date of the start so add a date (self.timeUnitPerDay) to the end
        if stop_time<start_time:
            stop_time+=self.timeUnitPerDay
        for station in line[1].split(','):
          station = station.strip()
          shift_by_station.setdefault(station, []).append(
            (start_time, stop_time) )

    # XXX operator_shift_spreadsheet should be configuration
    if data['input'].get('operator_shift_spreadsheet', None):
      for line in data['input']['operator_shift_spreadsheet'][1:]:
        if line[1]:
          start_time = self.convertToSimulationTime(strptime("%s %s" % (line[0], line[2]), '%Y/%m/%d %H:%M'))
          stop_time = self.convertToSimulationTime(strptime("%s %s" % (line[0], line[3]), '%Y/%m/%d %H:%M'))
          # if the end of shift shift already finished we do not need to consider in simulation
          if start_time<0 and stop_time<=0:
              continue
          # if the start of the shift is before now, set the start to 0
          if start_time<0:
              start_time=0
          # sometimes the date may change (e.g. shift from 23:00 to 01:00). 
          # these would be declared in the date of the start so add a date (self.timeUnitPerDay) to the end
          if stop_time<start_time:
              stop_time+=self.timeUnitPerDay
          for station in line[1].split(','):
            station = station.strip()
            shift_by_station.setdefault(station, []).append(
              (start_time, stop_time) )

    for node, node_data in data['graph']['node'].items():
      if node in shift_by_station:
        interruptions=node_data.get('interruptions',{})
        if not interruptions:
            node_data['interruptions']={}
        node_data['interruptions']['shift'] = {'shiftPattern': shift_by_station.pop(node),
                              'endUnfinished': 0} # XXX shall we make this
                                                  # configurable ?
    return data
