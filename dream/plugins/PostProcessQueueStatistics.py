from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class PostProcessQueueStatistics(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph
  """

  def postprocess(self, data):
      
      
    self.initializeTimeSupport(data)
    result = data['result']['result_list'][-1]

    series = []
    options = {
      "xaxis": {
        "mode": "time",
        "minTickSize": [1, self.getTimeUnitText()],
      }
    }

    result[self.configuration_dict['output_id']] = {
      "series": series,
      "options": options
    }

    for obj in result['elementList']:
      if obj.get('family') == self.configuration_dict.get('family', 'Buffer'):
        series.append({
         "label": obj.get('name', obj['id']),
         "data": [(self.convertToTimeStamp(time) * 1000, value) for (time, value) in obj['results']['wip_stat_list'][0] 
                  if not time==float("inf")]
        })
    return data
