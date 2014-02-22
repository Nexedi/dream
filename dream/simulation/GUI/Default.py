import json
from dream.simulation.LineGenerationJSON import main as simulate_line_json

# describe type for properties
schema = {
  "entity": {
    "id": "entity",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "Dream.Part"
  },
  "mean": {
    "id": "mean",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "0.9"
  },
  "distributionType": {
    "id": "distributionType",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "Fixed"
  },
  "stdev": {
    "id": "stdev",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "0.1"
  },
  "min": {
    "id": "min",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "0.1"
  },
  "max": {
    "id": "max",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "1"
  },
  "failureDistribution": {
    "id": "failureDistribution",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "No"
  },
  "MTTF": {
    "id": "MTTF",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "40"
  },
  "MTTR": {
    "id": "MTTR",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "repairman": {
    "id": "repairman",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "None"
  },
  "isDummy": {
    "id": "isDummy",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "0"
  },
  "schedulingRule": {
    "id": "schedulingRule",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "FIFO"
  },
  "capacity": {
    "id": "capacity",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "1"
  },
  "numberOfReplications": {
    "id": "numberOfReplications",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "maxSimTime": {
    "id": "maxSimTime",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "100"
  },
  "confidenceLevel": {
    "id": "confidenceLevel",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "0.5"
  },
  "processTimeout": {
    "id": "processTimeout",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "batchNumberOfUnits": {
    "id": "batchNumberOfUnits",
    "type": "integer",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "numberOfSubBatches": {
    "id": "numberOfSubBatches",
    "type": "integer",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "method": {
    "id": "method",
    "type": "string",
    "_class": "Dream.Property",
    "_default": ""
  },
  "start": {
    "id": "start",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "1"
  },
  "stop": {
    "id": "stop",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "-1"
  },
  "interval": {
    "id": "interval",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "duration": {
    "id": "duration",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "10"
  },
  "argumentDict": {
    "id": "argumentDict",
    "type": "string", # XXX json encoded ?
    "_class": "Dream.Property",
    "_default": "{}"
  },
  "currentDate": {
    "id": "currentDate",
    "type": "string", # XXX format ?
    "_class": "Dream.Property",
    "_default": ""
  },
}

# complex schemas (Dream.PropertyList)
schema["interarrivalTime"] = {
  "id": "interarrivalTime",
  "property_list": [
    schema["mean"],
    schema["distributionType"]],
  "_class": "Dream.PropertyList"
}

schema["processingTime"] = {
  "id": "processingTime",
  "property_list": [
    schema["mean"],
    schema["distributionType"],
    schema["stdev"],
    schema["min"],
    schema["max"]
  ],
  "_class": "Dream.PropertyList"
}

schema["failures"] = {
  "id": "failures",
  "property_list": [
    schema["failureDistribution"],
    schema["MTTF"],
    schema["MTTR"],
    schema["repairman"]
  ],
  "_class": "Dream.PropertyList"
}


class Simulation(object):
  def __init__(self, logger=None):
    self.logger = logger

  def getConfigurationDict(self):
    """Returns the possible nodes to use in the graph editor, and the global
    configuration.
    """
    return {
      "Dream-Source": {
        "property_list": [
          schema["interarrivalTime"],
          schema["entity"]
        ],
        "_class": 'Dream.Source'
      },
      "Dream-Machine": {
        "property_list": [
          schema["processingTime"],
          schema["failures"]
        ],
        "_class": 'Dream.Machine'
      },
      "Dream-Queue": {
        "property_list": [
          schema["capacity"],
          schema["isDummy"],
          schema["schedulingRule"]
        ],
        "_class": 'Dream.Queue'
      },
      "Dream-Exit": {
        "_class": 'Dream.Exit'
      },
      "Dream-Repairman": {
        "property_list": [schema["capacity"]],
        "_class": 'Dream.Repairman'
      },

      # global configuration
      "Dream-Configuration": {
        "property_list": [
           schema["numberOfReplications"],
           schema["maxSimTime"],
           schema["confidenceLevel"],
           schema["processTimeout"],
           schema["currentDate"],
        ],
        "gui": {
          'debug_json': 0,
          'wip_spreadsheet': 0,
          'wip_part_spreadsheet': 0,
          'shift_spreadsheet': 0,

          'station_utilisation_graph': 1,
          'job_schedule_spreadsheet': 0,
          'job_gantt': 0,
          'exit_stat': 0,
        },
        "_class": 'Dream.Configuration'
      },
    }

  def runOneScenario(self, data):
    """Run one scenario.
    To be reused by subclasses.
    """
    return json.loads(simulate_line_json(
      input_data=json.dumps(self._preprocess(data))))

  def _preprocess(self, data):
    """Preprocess the data, for instance reading spreadsheet.
    """
    return data

  def run(self, data):
    """Run simulation and return result to the GUI.
    """
    return [{"key": "default",
             "score": 0,
             "result": self.runOneScenario(data)}]
