from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.simulation.GUI import ACO
from dream.simulation.GUI.Default import schema

class Simulation(ACO.Simulation):
  def getConfigurationDict(self):
    conf = ACO.Simulation.getConfigurationDict(self)
    conf["Dream-MachineJobShop"] = {
        "property_list": [
          schema["processingTime"],
          schema["failures"]
        ],
        "_class": 'Dream.MachineJobShop',
        "name": 'Machine'
    }
    conf["Dream-QueueJobShop"] = {
        "property_list": [
          schema["capacity"],
          schema["isDummy"],
          schema["schedulingRule"]
        ],
        "_class": 'Dream.QueueJobShop',
        "name": 'Job'
    }
    conf["Dream-ExitJobShop"] = {
        "_class": 'Dream.ExitJobShop',
        "name": 'Exit'
    }
    # XXX remove default machines etc ?
    conf["Dream-Configuration"]["gui"]["wip_spreadsheet"] = 1
    conf["Dream-Configuration"]["gui"]["job_schedule_spreadsheet"] = 1
    conf["Dream-Configuration"]["gui"]["job_gantt"] = 1

    # remove tools that does not make sense here
    conf.pop('Dream-Machine')
    conf.pop('Dream-Queue')
    conf.pop('Dream-Exit')
    return conf

  def _preprocess(self, in_data):
    """ Set the WIP in queue from spreadsheet data.
    """
    data = copy(in_data)

    now = datetime.now()
    if data['general']['currentDate']:
      now = datetime.strptime(data['general']['currentDate'], '%Y/%m/%d')

    if 'wip_spreadsheet' in data:
      wip_dict = {}
      for value_list in data['wip_spreadsheet']:
        if value_list[1] == 'ID' or not value_list[1]:
          continue
        dueDate = (datetime.strptime(value_list[3], '%Y/%m/%d') - now).days

        sequence_list = value_list[6].split('-')
        processing_time_list = value_list[7].split('-')
        wip_dict.setdefault(sequence_list[0], []).append(
          {
            "_class": "Dream.Job",
            "id": value_list[1],
            "name": value_list[0],
            "dueDate": dueDate,
            "route": [
              {
                "processingTime": {
                  "distributionType": "Fixed",
                  "mean": processing_time_list[i],
                  },
                "stationIdsList": sequence_list[i].split(','),
                "stepNumber": i
              } for i in xrange(len(sequence_list))]
          }
        )
      for node_id in data['nodes'].keys():
        if node_id in wip_dict:
          data['nodes'][node_id]['wip'] = wip_dict[node_id]
      del(data['wip_spreadsheet'])
    return data

