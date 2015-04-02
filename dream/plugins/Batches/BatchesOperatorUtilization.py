from dream.plugins import plugin
from copy import copy

class BatchesOperatorUtilization(plugin.OutputPreparationPlugin):
  """ Output the station utilization metrics in a format compatible with 
  """

  def postprocess(self, data):
    result = data['result']['result_list'][-1]
    
    ticks = []
    working_data = []
    waiting_data = []
    off_shift_data = []
     
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
    }
    ];
 
    out = result[self.configuration_dict['output_id']] = {
      "series": series,
      "options": options
    }
    
    i = 0
    for obj in result['elementList']:
        if obj.get('_class') == 'Dream.Operator':
            working_ratio=obj['results']['working_ratio'][0]
            waiting_ratio=obj['results']['waiting_ratio'][0]
            # if there is no working or waiting time do not output for this operator
            if (not working_ratio) and (not waiting_ratio):
                continue
            if obj['results']['working_ratio']:
                working_data.append((i, 100*(working_ratio/(working_ratio+waiting_ratio))))
            if obj['results']['waiting_ratio']:
                waiting_data.append((i, 100*(waiting_ratio/(working_ratio+waiting_ratio))))
            ticks.append((i, obj.get('name', self.getNameFromId(data, obj['id']))))
            i += 1
  
    return data
