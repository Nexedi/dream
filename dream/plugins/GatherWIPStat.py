from dream.plugins import plugin

class GatherWIPStat(plugin.InputPreparationPlugin):

  def preprocess(self, data):
    """Preprocess the data, for instance reading spreadsheet.
    """
    # by default we add an event generator if using queue stats
    if data["application_configuration"]["output"]["view_queue_stats"]:
      for node in data["graph"]["node"].values():
        if node['_class'] in ('Dream.Queue', ):
          node['gatherWipStat'] = 1
    return data
