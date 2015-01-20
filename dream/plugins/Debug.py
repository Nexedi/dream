from dream.plugins import plugin
from pprint import pformat

class Debug(plugin.InputPreparationPlugin):

  def preprocess(self, data):
    """Preprocess the data.
    """
    self.logger.info("%s: %s " % (self.name, pformat(data)))
    return data
