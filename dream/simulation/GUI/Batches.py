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
      "property_list": conf['Dream-Queue']['property_list']}
    conf['Dream-BatchSource'] = {
        "_class": "Dream.BatchSource",
        "property_list": conf['Dream-Source']['property_list']\
          + [schema['batchNumberOfUnits']]
    }
    conf['Dream-BatchDecomposition'] = {
      "_class": "Dream.BatchDecomposition",
      "property_list": [schema['processingTime'], schema['numberOfSubBatches'] ]
      }
    conf['Dream-BatchReassembly'] = {
      "_class": "Dream.BatchReassembly",
      "property_list": [schema['processingTime'], schema['numberOfSubBatches'] ]
      }
    conf['Dream-BatchScrapMachine'] = {
      "_class": "Dream.BatchScrapMachine",
      "property_list": conf['Dream-Machine']['property_list']
      }
    return conf

  def run(self, data):
    return DefaultSimulation.run(self._preprocess(data))
