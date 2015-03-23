from dream.plugins import plugin
from copy import copy

class CapacityProjectStationUtilization(plugin.OutputPreparationPlugin):
  """ Output the station utilization metrics in a format compatible with 
  """

  def postprocess(self, data):
    for result in data['result']['result_list']:
      ticks = []
      utilized_data = []
      idle_data = []
      
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
        "label": "Utilized",
        "data": utilized_data
      }, {
        "label": "Idle",
        "data": idle_data
      }
      ];
  
      out = result[self.configuration_dict['output_id']] = {
        "series": series,
        "options": options
      }
  
  
      i = 0
      for obj in result['elementList']:
        if obj.get('family') == self.configuration_dict.get('family'):
          if obj['results']['meanUtilization']:
            utilized_data.append((i, obj['results']['meanUtilization']*100))
            idle_data.append((i, (1- obj['results']['meanUtilization'])*100))
  
          ticks.append((i, obj.get('name', self.getNameFromId(data, obj['id']))))
          i += 1
    
    return data
