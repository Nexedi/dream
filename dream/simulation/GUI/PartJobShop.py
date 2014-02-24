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
    conf["Dream-QueueManagedJob"] = {
        "property_list": [
          schema["capacity"],
          schema["isDummy"],
          schema["schedulingRule"]
        ],
        "_class": 'Dream.QueueManagedJob',
        "name": 'Queue'
    }
    conf["Dream-ConditionalBuffer"] = {
        "property_list": [
          schema["capacity"],
          schema["isDummy"],
          schema["schedulingRule"]
        ],
        "_class": 'Dream.ConditionalBuffer',
        "name": 'Buffer'
    }
    conf["Dream-ExitJobShop"] = {
        "_class": 'Dream.ExitJobShop',
        "name": 'Exit'
    }
    conf["Dream-OrderDecomposition"] = {
        "_class": 'Dream.OrderDecomposition',
        "name": 'Decompo'
    }
    # XXX remove default machines etc ?
    conf["Dream-Configuration"]["gui"]["wip_part_spreadsheet"] = 1
    conf["Dream-Configuration"]["gui"]["job_schedule_spreadsheet"] = 1
    conf["Dream-Configuration"]["gui"]["job_gantt"] = 1

    conf["Dream-Configuration"]["gui"]["debug_json"] = 1

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

    if 'wip_part_spreadsheet' in data:
      # Data is presented as follow, with first line the order, then only parts of this order
      # Order ID | Due Date | Priority | Project Manager | Parts | Part Type | Sequence | Processing Time | Electrodes needed
      # Order 1  | 2013/02/15 | 1      |   PM1           | P1    |  type1    | Mach1-Mach2 | 3-5          |
      wip_dict = {}
      print "wip part data : %r" % (data['wip_part_spreadsheet'],)
      for value_list in data['wip_part_spreadsheet']:
        print "first value_list: %r" % (value_list,)
        if value_list[0] == 'Order ID' or not value_list[4]:
          continue
        print "still there after first continue"
        order_id, due_date, priority, project_manager, part, part_type,\
          sequence_list, processing_time_list, electrode_needed = value_list
        
        due_date = (datetime.strptime(due_date, '%Y/%m/%d') - now).days
        sequence_list = sequence_list.split('-')
        processing_time_list = processing_time_list.split('-')

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
      del(data['wip_part_spreadsheet'])
    return data

