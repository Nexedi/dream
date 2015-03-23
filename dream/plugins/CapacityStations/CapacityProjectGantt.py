from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class CapacityProjectGantt(plugin.OutputPreparationPlugin, TimeSupportMixin):

  def postprocess(self, data):
    """Post process the data for Gantt gadget
    """
    # in this instance there is not need to define start time
    data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    date_format = '%d-%m-%Y %H:%M'
    
    for result in data['result']['result_list']:
      resultElements = result['elementList']
      task_dict = {}
      # loop in the results to find CapacityProjects
      for element in resultElements:
        if element['_class']=="Dream.CapacityProject":
          # add the project in the task_dict
          task_dict[element['id']] = dict(
          id=element['id'],
          text='Project %s' % element['id'],
          type='project',
          color='DodgerBlue',
          open=False)
          
          # loop in the project schedule to create the sub-tasks    
          projectSchedule=element['results'].get('schedule',{})
          
          for record in projectSchedule:
              task_dict[element['id']+record['stationId']] = dict(
                  id=element['id']+record['stationId'],
                  parent=element['id'],
                  text=record['stationId'],
                  start_date=self.convertToRealWorldTime(
                        record['entranceTime']).strftime(date_format),
                  stop_date=self.convertToRealWorldTime(
                        record['exitTime']).strftime(date_format),
                  open=False,
                  duration=int(record['exitTime'])-int(record['entranceTime']),
                  entranceTime=record['entranceTime'],
                  color='cyan'
              )
          
      # return the result to the gadget
      result[self.configuration_dict['output_id']] = dict(
        time_unit=self.getTimeUnitText(),
        task_list=sorted(task_dict.values(),
          key=lambda task: (task.get('parent'),
                            task.get('type') == 'project',
                            task.get('entranceTime'),task.get('id'))))
    return data
