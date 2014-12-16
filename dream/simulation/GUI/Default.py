import json
import datetime
from dream.simulation.LineGenerationJSON import main as simulate_line_json
from dream.simulation.Queue import Queue
from copy import deepcopy

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
    "_default": 1,
  },
  "distributionType": {
    "id": "distributionType",
    "name": "Distribution Type",
    "description": "The distribution type, one of Fixed, Exp, Normal",
    "type": "string",
    "choice": ([["Fixed", "Fixed"],
                ["Exp", "Exp"],
                ["Normal", "Normal"]]),
    "_class": "Dream.Property",
    "_default": "Fixed"
  },
  "stdev": {
    "id": "stdev",
    "type": "number",
    "name": "Standard Deviation",
    "_class": "Dream.Property",
  },
  "min": {
    "id": "min",
    "type": "number",
    "name": "Minimum Value",
    "_class": "Dream.Property",
  },
  "max": {
    "id": "max",
    "type": "number",
    "name": "Maximum Value",
    "_class": "Dream.Property",
  },
  "timeUnitPerDay": {
    "id": "timeUnitPerDay",
    "type": "number",
    "name": "Number of time units per day",
    "description": "Used for input and reporting widgets."
    " For example, 24 means that simulation clock time unit is one hour.",
    "_class": "Dream.Property",
    "_default": 24
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
    "name": "Repairman",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "None"
  },
  "operationType": {
    "id": "operationType",
    "type": "string",
    "name": "Operation Type",
    "choice": [["Auto", "MT-Load-Setup"],
               ["Manual", "MT-Load-Processing"]],
    "_class": "Dream.Property",
    "_default": "MT-Load-Processing"
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
    "choice": [(rule, rule) for rule in Queue.getSupportedSchedulingRules()],
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
    "_default": 0.95
  },
  "processTimeout": {
    "id": "processTimeout",
    "type": "number",
    "name": "Process Timeout",
    "description": "Number of seconds before the calculation process is interrupted",
    "_class": "Dream.Property",
    "_default": 10
  },
  "seed": {
    "id": "seed",
    "name": "Seed for random number generator",
    "description": "When using the same seed, the random number generator"
                   " produce the same sequence of numbers",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "",
  },
  "ke_url": {
    "id": "ke_url",
    "name": "URL for Knowledge Extraction Spreadsheet",
    "description": "The URL for knowledge extraction to access its data"
                   " for example "
                   "http://git.erp5.org/gitweb/dream.git/blob_plain/HEAD:/dream/KnowledgeExtraction/Mockup_Processingtimes.xls",
    "type": "string",
    "_class": "Dream.Property",
    "_default":
    "http://git.erp5.org/gitweb/dream.git/blob_plain/HEAD:/dream/KnowledgeExtraction/Mockup_Processingtimes.xls",
  },
  "batchNumberOfUnits": {
    "id": "batchNumberOfUnits",
    "type": "number",
    "name": "Number of Units",
    "description": "Number of units of the created batch",
    "_class": "Dream.Property",
    "_default": 80
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
    "_default": datetime.datetime.now().strftime('%Y/%m/%d')
  },
  "trace": {
    "id": "trace",
    "name": "Output Trace",
    "description": "Create an excel trace file (Yes or No)",
    "type": "string",
    "_class": "Dream.Property",
    "_default": "No"
  },
}

# helper function to overload a property
def overloaded_property(prop, overload):
  prop = deepcopy(prop)
  prop.update(overload)
  return prop

# complex schemas (Dream.PropertyList)
schema["processingTime"] = {
  "id": "processingTime",
  "name": "Processing Time",
  "property_list": [
    schema["distributionType"],
    overloaded_property(schema["mean"], {"_default": 0.75}),
    schema["stdev"],
    schema["min"],
    schema["max"]
  ],
  "_class": "Dream.PropertyList"
}

schema["interarrivalTime"] = {
  "id": "interarrivalTime",
  "name": "Interarrival Time",
  "property_list": [
    schema["distributionType"],
    schema["mean"],
    schema["stdev"],
    schema["min"],
    schema["max"],
  ],
  "_class": "Dream.PropertyList"
}


schema["failures"] = {
  "id": "failures",
  "name": "Failures",
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
        "short_id": "S",
        "_class": 'Dream.Source'
      },
      "Dream-Machine": {
        "property_list": [
          schema["processingTime"],
          schema["failures"]
        ],
        "short_id": "M",
        "_class": 'Dream.Machine'
      },
      "Dream-Queue": {
        "property_list": [
          schema["capacity"],
          # schema["isDummy"],
          schema["schedulingRule"]
        ],
        "short_id": "Q",
        "_class": 'Dream.Queue'
      },
      "Dream-Exit": {
        "short_id": "E",
        "_class": 'Dream.Exit'
      },
      "Dream-Repairman": {
        "short_id": "R",
        "property_list": [schema["capacity"]],
        "_class": 'Dream.Repairman'
      },
      "Dream-EventGenerator": {
        "name": "Event Generator",
        "short_id": "EG",
        "property_list": [schema['start'], schema['stop'], schema['duration'],
            schema['interval'], schema['method'], schema['argumentDict']],
        "_class": "Dream.EventGenerator",
      },
      # global configuration
      "Dream-Configuration": {
        "property_list": [
           schema["numberOfReplications"],
           schema["maxSimTime"],
           schema["confidenceLevel"],
           schema["processTimeout"],
           schema["currentDate"],
           schema["timeUnitPerDay"],
           schema["trace"],
           schema["seed"],
           schema["ke_url"],
        ],
        "gui": {
          'debug_json': 1,
          'wip_spreadsheet': 0,
          'wip_part_spreadsheet': 0,
          'shift_spreadsheet': 0,

          'station_utilisation_graph': 1,
          'job_schedule_spreadsheet': 0,
          'download_excel_spreadsheet': 0,
          'job_gantt': 0,
          'exit_stat': 1,
          'queue_stat': 1,
        },
        "_class": 'Dream.Configuration'
      },
    }

  def runOneScenario(self, data):
    """Run one scenario.
    To be reused by subclasses.
    """
    return json.loads(simulate_line_json(input_data=json.dumps(data)))

  def _preprocess(self, data):
    """Preprocess the data, for instance reading spreadsheet.
    """
    # by default we add an event generator if using queue stats
    # if self.getConfigurationDict()["Dream-Configuration"]["gui"]["queue_stat"]:
    if data["application_configuration"]["output"]["view_queue_stats"]:
      for node in data["graph"]["node"].values():
        if node['_class'] in ('Dream.Queue', ):
          node['gatherWipStat'] = 1
    return data

  def run(self, data):
    """Run simulation and return result to the GUI.
    """
    prepocessed_data = self._preprocess(data)
    return [{"key": "default",
             "score": 0,
             "result": self.runOneScenario(prepocessed_data),
             "input": prepocessed_data}]
