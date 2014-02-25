import json
import datetime
from dream.simulation.LineGenerationJSON import main as simulate_line_json
from dream.simulation.Queue import Queue

# describe type for properties
schema = {
  "entity": {
    "id": "entity",
    "name": "Entity Class",
    "description": "The Class of entity created",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "Dream.Part"
  },
  "mean": {
    "id": "mean",
    "type": "number",
    "name": "Mean",
    "description": "Mean value of fixed processing time.",
    "_class": "Dream.Property",
    "_default": 0.9
  },
  "distributionType": {
    "id": "distributionType",
    "name": "Distribution Type",
    "description": "The distribution type, one of Fixed, Exp, Normal",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "Fixed"
  },
  "stdev": {
    "id": "stdev",
    "type": "number",
    "name": "Normal distribution standard deviation",
    "_class": "Dream.Property",
    "_default": 0.1
  },
  "min": {
    "id": "min",
    "type": "number",
    "name": "Normal distribution minimum value",
    "_class": "Dream.Property",
    "_default": 0.1
  },
  "max": {
    "id": "max",
    "type": "number",
    "name": "Normal distribution maximum value",
    "_class": "Dream.Property",
    "_default": 1
  },
  "failureDistribution": {
    "id": "failureDistribution",
    "type": "string",
    "name": "Failures Distribution",
    "_class": "Dream.Property",
    "_default": "No"
  },
  "MTTF": {
    "id": "MTTF",
    "type": "number",
    "description": "Mean time to failure",
    "_class": "Dream.Property",
    "_default": 40
  },
  "MTTR": {
    "id": "MTTR",
    "type": "number",
    "description": "Mean time to repair",
    "_class": "Dream.Property",
    "_default": 10
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
    "name": "Scheduling Rule",
    "description": "Scheduling Rule, one of %s" % (" ".join(
        Queue.getSupportedSchedulingRules())),
    "_class": "Dream.Property",
    "_default": "FIFO"
  },
  "capacity": {
    "id": "capacity",
    "type": "number",
    "name": "Capacity",
    "_class": "Dream.Property",
    "_default": 1
  },
  "numberOfReplications": {
    "id": "numberOfReplications",
    "name": "Number of replications",
    "type": "number",
    "_class": "Dream.Property",
    "_default": 10
  },
  "maxSimTime": {
    "id": "maxSimTime",
    "type": "number",
    "name": "Length of experiment",
    "_class": "Dream.Property",
    "_default": 100
  },
  "confidenceLevel": {
    "id": "confidenceLevel",
    "type": "number",
    "name": "Confidence level",
    "description": "Confidence level for statiscal analysis of stochastic experiments",
    "_class": "Dream.Property",
    "_default": 0.5
  },
  "processTimeout": {
    "id": "processTimeout",
    "type": "number",
    "name": "Process Timeout",
    "description": "Number of seconds before the calculation process is interrupted",
    "_class": "Dream.Property",
    "_default": 10
  },
  "batchNumberOfUnits": {
    "id": "batchNumberOfUnits",
    "type": "number",
    "name": "Number of Units",
    "description": "Number of units of the created batch",
    "_class": "Dream.Property",
    "_default": 10
  },
  "numberOfSubBatches": {
    "id": "numberOfSubBatches",
    "type": "number",
    "name": "Number of sub batches",
    "description": "Number of sub batches that the batch is split to",
    "_class": "Dream.Property",
    "_default": 10
  },
  "method": {
    "id": "method",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "Globals.countIntervalThroughput"
  },
  "start": {
    "id": "start",
    "type": "number",
    "_class": "Dream.Property",
    "_default": 1
  },
  "stop": {
    "id": "stop",
    "type": "number",
    "_class": "Dream.Property",
    "_default": -1
  },
  "interval": {
    "id": "interval",
    "type": "number",
    "_class": "Dream.Property",
    "_default": 10
  },
  "duration": {
    "id": "duration",
    "type": "number",
    "_class": "Dream.Property",
    "_default": 10
  },
  "argumentDict": {
    "id": "argumentDict",
    "type": "string", # XXX json encoded ?
    "_class": "Dream.Property",
    "_default": "{}"
  },
  "currentDate": {
    "id": "currentDate",
    "type": "string",
    "name": "Simulation Start Time",
    "description": "The day the experiment starts, in YYYY/MM/DD format",
    "_class": "Dream.Property",
    "_default": datetime.datetime.now().strftime('%Y/%M/%d')
  },
  "trace": {
    "id": "trace",
    "name": "Output Trace",
    "description": "Create an excel trace file (Yes or No)",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "Yes"
  },
}

# complex schemas (Dream.PropertyList)
schema["interarrivalTime"] = {
  "id": "interarrivalTime",
  "property_list": [
    schema["distributionType"],
    schema["mean"]],
  "_class": "Dream.PropertyList"
}

schema["processingTime"] = {
  "id": "processingTime",
  "property_list": [
    schema["distributionType"],
    schema["mean"],
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
           schema["trace"],
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
