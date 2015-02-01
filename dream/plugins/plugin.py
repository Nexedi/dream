from copy import deepcopy
import json

from zope.dottedname.resolve import resolve

from dream.simulation.LineGenerationJSON import main as simulate_line_json

class Plugin(object):
  """Base class for pre-post processing Plugin.
  """
  def __init__(self, logger, configuration_dict):
    self.logger = logger
    self.configuration_dict = configuration_dict

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
    data["result"]["result_list"] = self.runOneScenario(data)['result']['result_list']
    data["result"]["result_list"][-1]["score"] = 0
    data["result"]["result_list"][-1]["key"] = "default"
    return data

class PluginRegistry(object):
  """Registry of plugins.
  """
  def __init__(self, logger, data):

    self.input_preparation_list = []
    for plugin_data in data['application_configuration']['pre_processing_plugin_list']:
      self.input_preparation_list.append(resolve(plugin_data['_class'])(logger, plugin_data))

    self.output_preparation_list = []
    for plugin_data in data['application_configuration']['post_processing_plugin_list']:
      self.output_preparation_list.append(resolve(plugin_data['_class'])(logger, plugin_data))

    plugin_data = data['application_configuration']['processing_plugin']
    self.execution_plugin = resolve(plugin_data['_class'])(logger, plugin_data)

  def run(self, data):
    """Preprocess, execute & postprocess.
    """
    for input_preparation in self.input_preparation_list:
        data = input_preparation.preprocess(deepcopy(data))

    data = self.execution_plugin.run(data)

    for output_preparation in self.output_preparation_list:
        data = output_preparation.postprocess(deepcopy(data))

    return data
