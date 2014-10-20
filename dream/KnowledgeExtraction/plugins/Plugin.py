from copy import deepcopy
import json

from zope.dottedname.resolve import resolve

from dream.simulation.LineGenerationJSON import main as simulate_line_json

class Plugin(object):
  """Base class for Knowledge Extraction Plugin.
  """
  def __init__(self, logger=None):
    self.logger = logger

class ExecutionPlugin(Plugin):
  """Plugin to handle the execution of multiple simulation runs.
  """
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
    return json.loads(simulate_line_json(input_data=json.dumps(data)))

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

    data = self.execution_plugin.run(data)

    for output_preparation in self.output_preparation_list:
        data = output_preparation.postprocess(deepcopy(data))

    return data


