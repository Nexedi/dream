from copy import copy
import json
import time
import random
import operator

from dream.simulation.GUI.Default import Simulation as DefaultSimulation
from dream.simulation.GUI.Default import schema

class Simulation(DefaultSimulation):
  def getConfigurationDict(self):
    conf = DefaultSimulation.getConfigurationDict(self)
    conf['Dream-LineClearance'] = {
      "_class": "Dream.LineClearance",
      "name": "Clearance",
      "property_list": conf['Dream-Queue']['property_list']}
    conf['Dream-BatchSource'] = {
        "_class": "Dream.BatchSource",
        "name": "Source",
        "property_list": conf['Dream-Source']['property_list']\
          + [schema['batchNumberOfUnits']]
    }
    conf['Dream-BatchDecomposition'] = {
      "_class": "Dream.BatchDecomposition",
      "name": "Decomposition",
      "property_list": [schema['processingTime'], schema['numberOfSubBatches'] ]
      }
    conf['Dream-BatchReassembly'] = {
      "_class": "Dream.BatchReassembly",
      "name": "Reassembly",
      "property_list": [schema['processingTime'], schema['numberOfSubBatches'] ]
      }
    conf['Dream-BatchScrapMachine'] = {
      "_class": "Dream.BatchScrapMachine",
      "name": "Station",
      "property_list": conf['Dream-Machine']['property_list']
      }
    conf['Dream-EventGenerator'] = {
      "_class": "Dream.EventGenerator",
      "name": "Attainment",
      "property_list": [schema['start'], schema['stop'], schema['duration'],
                        schema['method'], schema['argumentDict']]
      }
    conf["Dream-Configuration"]["gui"]["exit_stat"] = 1
    conf["Dream-Configuration"]["gui"]["debug_json"] = 1
    conf["Dream-Configuration"]["gui"]["shift_spreadsheet"] = 1
    return conf

