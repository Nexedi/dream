from dream.plugins import plugin

class PostProcessStationUtilization(plugin.OutputPreparationPlugin):
  """ Output the station utilization metrics in a format compatible with Output_viewGraph
  """

  def postprocess(self, data):
    result = data['result']['result_list'][-1]
    
    ticks = []
    working_data = []
    waiting_data = []
    failure_data = []
    blockage_data = []
    setup_data = []
    
    options = {
      "xaxis": {
        "minTickSize": 1,
        "ticks": ticks
      },
      "yaxis": {
        "max": 100
      },
      "series": {
        "bars": {
          "show": True,
          "barWidth": 0.8,
          "align": "center"
        },
        "stack": True
      }
    }
  
    series = [{
      "label": "Working",
      "data": working_data
    }, {
      "label": "Waiting",
      "data": waiting_data
    }, {
      "label": "Failures",
      "data": failure_data
    }, {
      "label": "Blockage",
      "data": blockage_data
    },
    {
      "label": "Setup",
      "data": setup_data
    }];

    out = result[self.configuration_dict['output_id']] = {
      "series": series,
      "options": options
    }

    i = 0
    for obj in result['elementList']:
      if obj.get('family') == self.configuration_dict.get('family'):
        if obj['results']['working_ratio']:
          working_data.append((i, obj['results']['working_ratio'][0]))
        if obj['results']['waiting_ratio']:
          waiting_data.append((i, obj['results']['waiting_ratio'][0]))
        if obj['results']['failure_ratio']:
          failure_data.append((i, obj['results']['failure_ratio'][0]))
        if obj['results']['blockage_ratio']:
          blockage_data.append((i, obj['results']['blockage_ratio'][0]))
        if obj['results']['setup_ratio']:
          setup_data.append((i, obj['results']['setup_ratio'][0]))

        ticks.append((i, obj.get('name', obj['id'])))
        i += 1
  
    return data
