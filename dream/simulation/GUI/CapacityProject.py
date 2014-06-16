from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.simulation.GUI.Default import Simulation as DefaultSimulation
from dream.simulation.GUI.Default import schema


class Simulation(DefaultSimulation):
  def getConfigurationDict(self):
    conf = DefaultSimulation.getConfigurationDict(self)

    conf["Dream-AbstractCapacityStation"] = {
        "property_list": [
          {
            "id": "isAssembly",
            "name": "Is an assembly station ?",
            "description": "Is this station an assembly ? Yes: 1, No: 0",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 0
          },
        ],
        "_class": 'Dream.AbstractCapacityStation',
        "name": 'Station',
        "short_id": "CS",
    }

    conf["Dream-Configuration"]["gui"]["capacity_by_project_spreadsheet"] = 1
    conf["Dream-Configuration"]["gui"]["capacity_by_station_spreadsheet"] = 1

    conf["Dream-Configuration"]["gui"]["station_utilisation_graph"] = 0
    conf["Dream-Configuration"]["gui"]["capacity_utilisation_graph"] = 1
    conf["Dream-Configuration"]["gui"]["job_schedule_spreadsheet"] = 1
    conf["Dream-Configuration"]["gui"]["job_gantt"] = 1
    conf["Dream-Configuration"]["gui"]["queue_stat"] = 0

    conf["Dream-Configuration"]["gui"]["debug_json"] = 1

    # remove tools that does not make sense here
    conf.pop('Dream-Machine')
    conf.pop('Dream-Queue')
    conf.pop('Dream-Exit')
    conf.pop('Dream-Repairman')
    conf.pop('Dream-Source')
    conf.pop('Dream-EventGenerator')
    return conf

  def _preprocess(self, in_data):
    data = copy(DefaultSimulation._preprocess(self, in_data))
    new_data = copy(data)
    # remove not needed spreadsheet not to polute json
    new_data.pop('shift_spreadsheet', None)
    new_data.pop('wip_part_spreadsheet', None)

    # read the spreadsheets
    # a mapping station id -> list of interval capacity
    available_capacity_by_station = dict()
    for line in data.pop('capacity_by_station_spreadsheet')[1:]:
      available_capacity_by_station[line[0]] = [float(x) for x in line[1:] if x]

    # a mapping project id -> mapping station_id -> required capacity
    required_capacity_by_project = dict()
    for project_id, station_sequence, requirement_sequence \
                    in data['capacity_by_project_spreadsheet'][1:]:
      if project_id:
        required_capacity_by_project[project_id] = {}
        for idx, capacity_station in enumerate(station_sequence.split('-')):
          capacity_station = '%s_Station' % capacity_station.strip()
          required_capacity_by_project[project_id][capacity_station] = \
                float(requirement_sequence.split('-')[idx])

    # a mapping project id -> first station
    first_station_by_project = dict()
    for project_id, station_sequence, requirement_sequence \
                    in data['capacity_by_project_spreadsheet'][1:]:
      if station_sequence:
        first_station_by_project[project_id] = station_sequence.split('-')[0]

    # implicitly add a Queue for wip
    assert 'Qstart' not in new_data['nodes'], "reserved ID used"
    wip = []
    for project, capacityRequirementDict in \
                    required_capacity_by_project.items():
      wip.append(
            dict(_class='Dream.CapacityProject',
                 id=project,
                 name=project,
                 capacityRequirementDict=capacityRequirementDict))

    new_data['nodes']['QStart'] = dict(
        _class='Dream.Queue',
        id='QStart',
        name='Start Queue',
        capacity=-1,
        wip=wip)

    # implicitly add a capacity station controller
    assert 'CSC' not in new_data['nodes'], "reserved ID used"
    new_data['nodes']['CSC'] = dict(
        _class='Dream.CapacityStationController',
        name='CSC',
        start=0,
        interval=1, )

    # "expand" abstract stations
    for node_id, node_data in data['nodes'].items():
      if node_data['_class'] == 'Dream.AbstractCapacityStation':
        # remove the node
        new_data['nodes'].pop(node_id)
        # remove outbound edges, while keeping a reference to the next station
        # to set nextCapacityStationBufferId on the exit
        next_abstract_station = None
        for edge_id, (source, dest, edge_dict) in \
                    list(new_data['edges'].items()):
                    # list because we remove some elements in the loop
          if source == node_id:
            next_abstract_station = dest
            del new_data['edges'][edge_id]

        wip = []
        # set as wip all projects that have to be processed in this station
        # firts
        for project, requirement_dict in required_capacity_by_project.items():
          if first_station_by_project[project] == node_id:
            requirement = requirement_dict['%s_Station' % node_id]
            name = '%s_%s_%s' % (project, node_id, requirement)
            wip.append(
                  dict(_class='Dream.CapacityEntity',
                       id=name,
                       name=name,
                       capacityProjectId=project,
                       requiredCapacity=requirement))

        new_data['nodes']["%s_Buffer" % node_id] = dict(
            _class='Dream.CapacityStationBuffer',
            id="%s_Buffer" % node_id,
            name=node_data['name'],
            wip=wip,
            isAssembly=node_data['isAssembly']
        )

        new_data['nodes']["%s_Station" % node_id] = dict(
            _class='Dream.CapacityStation',
            id="%s_Station" % node_id,
            name=node_data['name'],
            intervalCapacity=available_capacity_by_station[node_id],
        )

        exit = dict(_class='Dream.CapacityStationExit',
                    id="%s_Exit" % node_id,
                    name=node_data['name'],)
        # set nextCapacityStationBufferId
        if next_abstract_station:
          exit['nextCapacityStationBufferId'] = '%s_Buffer' %  next_abstract_station

        new_data['nodes']["%s_Exit" % node_id] = exit

        new_data['edges']['%s_1' % node_id] = [
            "%s_Buffer" % node_id,
            "%s_Station" % node_id,
            {}]
        new_data['edges']['%s_2' % node_id] = [
            "%s_Station" % node_id,
            "%s_Exit" % node_id,
            {}]

    return new_data

