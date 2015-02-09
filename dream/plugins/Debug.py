from dream.plugins import plugin
from pprint import pformat

class Debug(plugin.InputPreparationPlugin, plugin.OutputPreparationPlugin):

  def preprocess(self, data):
    """Preprocess the data.
    """
    self.logger.info("%s: %s" % (self.configuration_dict, pformat(data)))
    return data
  postprocess = preprocess