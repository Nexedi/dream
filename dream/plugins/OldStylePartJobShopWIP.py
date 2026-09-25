from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

# XXX could use getClassFromName & isinstance instead
MACHINE_TYPE_SET = set(["Dream.MachineManagedJob", "Dream.MouldAssembly"])

class OldStylePartJobShopWIP(plugin.InputPreparationPlugin, TimeSupportMixin):
  """ Input prepration 
      read wip-spreadsheet data and update the wip property of the stations.
  """

  def getMachineNameSet(self, step_name):
    """
    Give list of machines given a particular step name. For example
    if step_name is "CAM", it will return ["CAM1", "CAM2"]
    """
    machine_name_set = set()
    for machine_name in self.data['graph']["node"].keys():
      if machine_name.startswith(step_name):
        machine_name_set.add(machine_name)
    if not machine_name_set:
      raise ValueError("No machine found for step %s" % step_name)
    return machine_name_set

  def getNotMachineNodePredecessorList(self, step_name):
    """
    Give the list of all predecessors that are not of type machine
    For example, for step_name "CAM", it may return "QCAM"
    """
    predecessor_list = []
    machine_name_set = self.getMachineNameSet(step_name)
    for edge in self.data['graph']["edge"].values():
      if edge['destination'] in machine_name_set:
        predecessor_step = edge['source']
        if predecessor_step in predecessor_list:
          continue
        if not self.data['graph']["node"][predecessor_step]["_class"] in MACHINE_TYPE_SET:
          predecessor_list = [predecessor_step] + predecessor_list
          predecessor_list = [x for x in self.getNotMachineNodePredecessorList(predecessor_step) \
                                   if x not in predecessor_list] + predecessor_list
    return predecessor_list

  def getRouteList(self, sequence_list, processing_time_list, prerequisite_list):
    # use to record which predecessor has been already done, used to avoid doing
    # two times Decomposition
    predecessor_set = set()
    route_list = []
    for j, sequence_step in enumerate(sequence_list):
      for predecessor_step in self.getNotMachineNodePredecessorList(sequence_step):
        # We avoid having two time Decomposition in the route. XXX Is this correct ?
        if predecessor_step == "Decomposition" and predecessor_step in predecessor_set:
          continue
        predecessor_set.add(predecessor_step)
        route = {"stationIdsList": [predecessor_step],
                  }
        route_list.append(route)
      route = {"stationIdsList": list(self.getMachineNameSet(sequence_step)),
                "processingTime": {"distributionType": "Fixed",
                                   "mean": float(processing_time_list[j])},
                "setupTime": {"distributionType": "Fixed",
                              "mean": .5}, # XXX hardcoded value
              }
     # XXX distribution format changed !
      route = {"stationIdsList": list(self.getMachineNameSet(sequence_step)),
                "processingTime": {"Fixed": {
                                   "mean": float(processing_time_list[j])}},
                "setupTime": {"Fixed": {
                              "mean": .5}}, # XXX hardcoded value
              }

      # XXX Quick and dirty way to change to stochastic
      if 'Stochastic' in self.data['general']['name']:
          input_processing_time = float(processing_time_list[j])
          route = {"stationIdsList": list(self.getMachineNameSet(sequence_step)),
                    "processingTime": {"Triangular": {
                                       "mean": input_processing_time,
                                       "min": max(input_processing_time - 2, 0),
                                       "max": input_processing_time + 2,
                                       }},
                    "setupTime": {"Fixed": {
                                  "mean": .5}}, # XXX hardcoded value
                  }
      if prerequisite_list:
        route["prerequisites"] = prerequisite_list
      route_list.append(route)
    return route_list

  def getListFromString(self, my_string):
    my_list = []
    if not my_string in (None, ''):
      my_list = my_string.split('-')
    return my_list


  def preprocess(self, data):
    """ Set the WIP in queue from spreadsheet data.
    """
    self.initializeTimeSupport(data)
    self.data = copy(data)

    input_id = self.configuration_dict['input_id']
    wip_list = []
    i = 0
    wip_part_spreadsheet_length = len(data['input'][input_id])
    while i < wip_part_spreadsheet_length:
      value_list = data['input'][input_id][i]
      if value_list[0] == 'Order ID' or not value_list[4]:
        i += 1
        continue
      order_dict = {}
      wip_list.append(order_dict)
      order_id, due_date, priority, project_manager, part, part_type,\
        sequence_list, processing_time_list, prerequisite_string = value_list
      due_date = (datetime.strptime(due_date, '%Y/%m/%d') - self.now).days * 24
      prerequisite_list = self.getListFromString(prerequisite_string)
      sequence_list = sequence_list.split('-')
      processing_time_list = processing_time_list.split('-')

      order_dict["_class"] = "Dream.Order"
      order_dict["id"] = order_id
      order_dict["manager"] = project_manager
      order_dict["name"] = order_id
      order_dict["dueDate"] = due_date
      order_dict["priority"] = float(priority)
      # XXX make it dynamic by writing a function that will reuse the
      # code available a bit after
      order_dict["route"] = self.getRouteList(sequence_list, processing_time_list,
                                              prerequisite_list)
      i += 1
      component_list = []
      if i < wip_part_spreadsheet_length:
        while data['input'][input_id][i][0] in (None, ''):
          value_list = data['input'][input_id][i]
          if value_list[4] in (None, ''):
            break
          order_id, due_date, priority, project_manager, part, part_type,\
            sequence_list, processing_time_list, prerequisite_string = value_list
          sequence_list = sequence_list.split('-')
          prerequisite_list = self.getListFromString(prerequisite_string)
          processing_time_list = processing_time_list.split('-')
          component_dict = {}
          component_dict["_class"] = "Dream.OrderComponent"
          if part_type == "Mould":
            component_dict["_class"] = "Dream.Mould"
          component_dict["componentType"] = part_type
          component_dict["id"] = "%i" % i # XXX hack, we use it in UI to retrieve spreadsheet line
          component_dict["name"] = part
          component_list.append(component_dict)
          route_list = self.getRouteList(sequence_list, processing_time_list,
                                         prerequisite_list)
          if part_type == "Mould":
            route_list = route_list[1:]
          component_dict["route"] = route_list
          i+=1
        order_dict["componentsList"] = component_list
    data['graph']["node"]["QStart"]["wip"] = wip_list
    del data['input'][input_id]
    return data
