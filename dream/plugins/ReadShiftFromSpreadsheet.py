from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class ReadShiftFromSpreadsheet(plugin.InputPreparationPlugin):
  """ Input prepration 
      read shift-srpeadsheet data and update the wip property of the stations.
  """

  def preprocess(self, data):
    self.initializeTimeSupport(data)
    strptime = datetime.datetime.strptime

    shift_by_station = {}
    # XXX machine_shift_spreadsheet should be configuration
    for line in data['input']['machine_shift_spreadsheet'][1:]:
      if line[1]:
        start_time = self.convertToSimulationTime(strptime("%s %s" % (line[0], line[2]), '%Y/%m/%d %H:%M'))
        stop_time = self.convertToSimulationTime(strptime("%s %s" % (line[0], line[3]), '%Y/%m/%d %H:%M'))
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
