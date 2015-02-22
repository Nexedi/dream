from dream.plugins import plugin
from copy import copy

class BatchesStationUtilization(plugin.OutputPreparationPlugin):
  """ Output the station utilization metrics in a format compatible with 
  """

  def postprocess(self, data):
    result = data['result']['result_list'][-1]
    
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
      if obj.get('_class').startswith('Dream.BatchScrapMachine') or obj.get('_class')=='Dream.M3':
        nextId=self.getSuccessors(data, obj['id'])[0]
        nextClass=data['graph']['node'][nextId]['_class']
        objResults=copy(obj['results'])

        # if a station is before batch-reassembly then the blockage of reassembly is added to the station
        # and reducted from its waiting
        nextResults={}
        if nextClass.startswith('Dream.BatchReassembly'):
            for nextObj in result['elementList']:
                if nextObj['id']==nextId:
                    nextResults=nextObj["results"]
            if nextResults:
                nextBlockage=nextResults['blockage_ratio'][0]
                objResults['blockage_ratio'][0]=nextBlockage
                objResults['waiting_ratio'][0]-=nextBlockage         
        
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
