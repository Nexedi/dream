from dream.plugins import plugin
from copy import copy

class JSStationUtilization(plugin.OutputPreparationPlugin):
  """ Output the station utilization metrics in a format compatible with 
  """
  # XXX hardcoded values
  JS_STATION_CLASS_SET = set(["Dream.MouldAssembly", "Dream.MachineJobShop"])
  def postprocess(self, data):
    for result in data['result']['result_list']:

      ticks = []
      working_data = []
      waiting_data = []
      failure_data = []
      blockage_data = []
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
      }, {
        "label": "Failures",
        "data": failure_data
      }, {
        "label": "Blockage",
        "data": blockage_data
      },
      {
        "label": "off_shift",
        "data": off_shift_data
      }];

      out = result[self.configuration_dict['output_id']] = {
        "series": series,
        "options": options
      }

      i = 0
      for obj in result['elementList']:
        if obj.get('_class') in self.JS_STATION_CLASS_SET:
          objResults=copy(obj['results'])
          if objResults['working_ratio']:
            working_data.append((i, objResults['working_ratio'][0]))
          if objResults['waiting_ratio']:
            waiting_data.append((i, objResults['waiting_ratio'][0]))
          if objResults['failure_ratio']:
            failure_data.append((i, objResults['failure_ratio'][0]))
          if objResults['blockage_ratio']:
            blockage_data.append((i, objResults['blockage_ratio'][0]))
          if objResults['off_shift_ratio']:
            off_shift_data.append((i, objResults['off_shift_ratio'][0]))

          ticks.append((i, obj.get('name', self.getNameFromId(data, obj['id']))))
          i += 1
    
    return data
