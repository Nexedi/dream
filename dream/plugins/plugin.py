from copy import deepcopy
import json

from zope.dottedname.resolve import resolve

from dream.simulation.LineGenerationJSON import main as simulate_line_json

# helper function to overload a property
def overloaded_property(prop, overload):
  prop = deepcopy(prop)
  prop.update(overload)
  return prop

# helper function to return a default configuration dictionary
def getConfigurationDict(self):
  """Returns the possible nodes to use in the graph editor, and the global
  configuration.
  """
  return NotImplementedError

class Plugin(object):
  """Base class for pre-post processing Plugin.
  """
  def __init__(self, logger=None):
    self.logger = logger

class ExecutionPlugin(Plugin):
  """Plugin to handle the execution of multiple simulation runs.
  """
  def runOneScenario(self, data):
    """default method for running one scenario
    """
    return json.loads(simulate_line_json(input_data=json.dumps(data)))

  def run(self, data):
    """General execution plugin.
    """
    raise NotImplementedError

class InputPreparationPlugin(Plugin):
  def preprocess(self, data):
    """Preprocess the data before simulation run.
    """
    return data

class OutputPreparationPlugin(Plugin):
  def postprocess(self, data):
    """Postprocess the data after simulation run.
    """
    return data

class DefaultExecutionPlugin(ExecutionPlugin):
  """Default Execution Plugin just executes one scenario.
  """
  def run(self, data):
    """Run simulation and return result to the GUI.
    """
    data["result"]["result_list"].append(self.runOneScenario(data))
    # data["result"] = self.runOneScenario(data)
    data["result"]["result_list"][-1]["score"] = 0
    data["result"]["result_list"][-1]["key"] = "default"
    return data

class PluginRegistry(object):
  """Registry of plugins.
  """
  def __init__(self, logger,
               input_preparation_class_list,
               output_preparation_class_list,
               execution_plugin_class):
    self.input_preparation_list = tuple([resolve(name)(logger) for name in
        input_preparation_class_list])
    self.output_preparation_list = tuple([resolve(name)(logger) for name in
        output_preparation_class_list])
    self.execution_plugin = resolve(execution_plugin_class)(logger)

  def run(self, data):
    """Preprocess, execute & postprocess.
    """
    for input_preparation in self.input_preparation_list:
        data = input_preparation.preprocess(deepcopy(data))
    from DefaultWIPAlgorithm import preprocess as pp
    data=pp(deepcopy(data))
    
    data = self.execution_plugin.run(data)

    for output_preparation in self.output_preparation_list:
        data = output_preparation.postprocess(deepcopy(data))

    print '^'*100
    print data['result']