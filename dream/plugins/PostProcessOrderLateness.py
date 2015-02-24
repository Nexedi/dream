from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class PostProcessOrderLateness(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Postprocess order lateness for Input_viewResultOrderLateness
  """

  def postprocess(self, data):
    self.initializeTimeSupport(data)
    
    for result in data['result']['result_list']:
      for obj in result['elementList']:
        if obj.get('_class') == "Dream.OrderDesign": # XXX How to find orders ?
          result.setdefault(self.configuration_dict["output_id"], {})[obj["id"]] = {
            "dueDate": self.convertToFormattedRealWorldTime(obj["results"]["completionTime"] - obj["results"].get("delay", 0)),
            "delay": obj["results"].get("delay", 0), 
            "completionDate": self.convertToFormattedRealWorldTime(obj["results"]["completionTime"])
          }

    return data
