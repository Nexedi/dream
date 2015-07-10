from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime

class JSOperatorGantt(plugin.OutputPreparationPlugin, TimeSupportMixin):
  # XXX hard-coded value of the operator class available
  OPERATOR_CLASS_SET = set(["Dream.Operator"])
  def postprocess(self, data):
    """Post process the data for Gantt gadget
    """
    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
      data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d')
      data['general']['dateFormat']='%Y/%m/%d'
    maxSimTime=data['general']['maxSimTime']
    self.initializeTimeSupport(data)
    date_format = '%d-%m-%Y %H:%M'
    
    for result in data['result']['result_list']:
      resultElements=result['elementList']
      task_dict = {}
      # loop in the results to find Operators
      for element in resultElements:
        if element['_class'] in self.OPERATOR_CLASS_SET:
          operatorId=element['id']
      
          k=1
          
          schedule=element['results'].get('schedule', [])
          if schedule:

            # add the operator in the task_dict
            task_dict[element['id']] = dict(
              id=operatorId,
              text=operatorId,
              type='operator',
              open=False,
              color='DodgerBlue')

            for record in schedule:
              entranceTime=record['entranceTime']
              exitTime = record.get("exitTime", None)
              if not exitTime:
                try:
                  exitTime=schedule[k]['entranceTime']
                except IndexError:
                  exitTime=maxSimTime    
              k+=1
              task_id = record.get("task_id", None)
              if not task_id:
                task_id = record["stationId"]
                text_to_display = task_id
              else:
                entityId = record.get("entityId", None)
                if not entityId:
                  text_to_display = task_id + " " + record["stationId"]
                else:
                  text_to_display = task_id + " " + record["stationId"] + " " + entityId
              task_dict[operatorId+task_id+str(k)] = dict(
                id=operatorId+task_id+str(k),
                parent=operatorId,
                text=text_to_display,
                start_date=self.convertToRealWorldTime(
                      entranceTime).strftime(date_format),
                stop_date=self.convertToRealWorldTime(
                      exitTime).strftime(date_format),
                open=False,
                entranceTime=entranceTime,
                color='transparent',
                duration=exitTime-entranceTime,
              )
              if task_id == 'off-shift':
                task_dict[operatorId+task_id+str(k)]['color'] = 'grey'
                
      # return the result to the gadget
      result[self.configuration_dict['output_id']] = dict(
        time_unit=self.getTimeUnitText(),
        task_list=sorted(task_dict.values(),
          key=lambda task: (task.get('parent'),
                            task.get('type') == 'project',
                            task.get('entranceTime'),task.get('id'))))
    return data
