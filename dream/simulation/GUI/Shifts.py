from copy import copy
import json
import time
import random
import operator
import datetime

from dream.simulation.GUI.Default import Simulation as DefaultSimulation

import logging
logger = logging.getLogger('dream.platform')

class Simulation(DefaultSimulation):
  def _preprocess(self, data):
    """Preprocess data, reading shift spreadsheet
    """
    strptime = datetime.datetime.strptime
    now = strptime(data['general']['currentDate'], '%Y/%m/%d')

    shift_by_station = {}

    for line in data['shift_spreadsheet'][1:]:
      if line[1]:
        # Get the dates, and convert them to simulation clock time units.
        # In this class, time unit is a minute (XXX it can be an option)
        start_date = strptime("%s %s" % (line[0], line[2]), '%Y/%m/%d %H:%M')
        start_time = (start_date - now).total_seconds() // 60
        stop_date = strptime("%s %s" % (line[0], line[3]), '%Y/%m/%d %H:%M')
        stop_time = (stop_date - now).total_seconds() // 60
        for station in line[1].split(','):
          shift_by_station.setdefault(station, []).append(
            (start_time, stop_time) )

    for node, node_data in data['nodes'].items():
      if node in shift_by_station:
        node_data['shift'] = {'shiftPattern': shift_by_station.pop(node),
                              'endUnfinished': 0} # XXX shall we make this
                                                  # configurable ?

    assert not shift_by_station, \
        "Some stations only exist in shift but not in graph: %r"\
        % shift_by_station.keys()

#    from pprint import pformat
#    logger.info(pformat(data))
    return data

