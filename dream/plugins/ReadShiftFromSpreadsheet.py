from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class ReadShiftFromSpreadsheet(plugin.InputPreparationPlugin):
  """ Input prepration 
      read shift-srpeadsheet data and update the wip property of the stations.
  """

  def preprocess(self, data):
    strptime = datetime.datetime.strptime
    now = strptime(data['general']['currentDate'], '%Y/%m/%d')

    shift_by_station = {}
    
    for line in data['input']['machine_shift_spreadsheet'][1:]:
      if line[1]:
        # Get the dates, and convert them to simulation clock time units.
        # In this class, time unit is a minute (XXX it can be an option)
        start_date = strptime("%s %s" % (line[0], line[2]), '%Y/%m/%d %H:%M')
        start_time = (start_date - now).total_seconds() // 60
        stop_date = strptime("%s %s" % (line[0], line[3]), '%Y/%m/%d %H:%M')
        stop_time = (stop_date - now).total_seconds() // 60
        for station in line[1].split(','):
          station = station.strip()
          shift_by_station.setdefault(station, []).append(
            (start_time, stop_time) )

    for line in data['input']['operator_shift_spreadsheet'][1:]:
      print line
      if line[1]:
        # Get the dates, and convert them to simulation clock time units.
        # In this class, time unit is a minute (XXX it can be an option)
        start_date = strptime("%s %s" % (line[0], line[2]), '%Y/%m/%d %H:%M')
        start_time = (start_date - now).total_seconds() // 60
        stop_date = strptime("%s %s" % (line[0], line[3]), '%Y/%m/%d %H:%M')
        stop_time = (stop_date - now).total_seconds() // 60
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