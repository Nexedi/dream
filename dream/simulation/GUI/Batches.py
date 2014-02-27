import copy
import json
import time
import random
import operator

from dream.simulation.GUI.Shifts import Simulation as ShiftsSimulation
from dream.simulation.GUI.Default import schema

class Simulation(ShiftsSimulation):
  def getConfigurationDict(self):
    conf = ShiftsSimulation.getConfigurationDict(self)
    conf['Dream-LineClearance'] = {
      "_class": "Dream.LineClearance",
      "name": "Clearance",
      "short_id": "C",
      "property_list": conf['Dream-Queue']['property_list']}

    batch_source_entity = copy.deepcopy(schema["entity"])
    batch_source_entity['_default'] = "Dream.Batch"
    conf['Dream-BatchSource'] = {
        "_class": "Dream.BatchSource",
        "name": "Source",
        "short_id": "S",
        "property_list": [schema['interarrivalTime'],
                          batch_source_entity,
                          schema['batchNumberOfUnits']]
    }

    zeroProcessingTime = copy.deepcopy(schema['processingTime'])
    for prop in zeroProcessingTime['property_list']:
      if prop['id'] == 'mean':
        prop['_default'] = 0.0

    perUnitProcessingTime = copy.deepcopy(schema['processingTime'])
    for prop in perUnitProcessingTime['property_list']:
      if prop['id'] == 'mean':
        prop['description'] = "Processing time per unit"

    conf['Dream-BatchDecompositionStartTime'] = {
      "_class": "Dream.BatchDecompositionStartTime",
      "name": "Decomposition",
      "short_id": "D",
      "property_list": [zeroProcessingTime, schema['numberOfSubBatches'] ]
      }
    conf['Dream-BatchReassembly'] = {
      "_class": "Dream.BatchReassembly",
      "name": "Reassembly",
      "short_id": "R",
      "property_list": [zeroProcessingTime, schema['numberOfSubBatches'] ]
      }

    conf['Dream-BatchScrapMachine'] = {
      "_class": "Dream.BatchScrapMachine",
      "name": "Station",
      "short_id": "St",
      "property_list": [perUnitProcessingTime, schema['failures'] ]
      }
    conf['Dream-EventGenerator'] = {
      "_class": "Dream.EventGenerator",
      "name": "Attainment",
      "short_id": "A",
      "property_list": [schema['start'], schema['stop'], schema['duration'],
          schema['interval'], schema['method'], schema['argumentDict']]
      }
    conf["Dream-Configuration"]["gui"]["exit_stat"] = 1
    conf["Dream-Configuration"]["gui"]["debug_json"] = 1
    conf["Dream-Configuration"]["gui"]["shift_spreadsheet"] = 1

    # some more global properties
    conf["Dream-Configuration"]["property_list"].append( {
      "id": "throughputTarget",
      "name": "Daily Throughput Target",
      "description": "The daily throughput target in units.",
      "type": "number",
      "_class": "Dream.Property",
      "_default": 10 })

    # remove tools that does not make sense here
    conf.pop('Dream-Machine')
    conf.pop('Dream-Repairman')
    conf.pop('Dream-Source')
    return conf

