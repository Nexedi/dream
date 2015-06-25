from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class CapacityStationGantt(plugin.OutputPreparationPlugin, TimeSupportMixin):

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
        if element['_class']=="Dream.CapacityStation":
          # add the project in the task_dict
          task_dict[element['id']] = dict(
          id=element['id'],
          text='Station %s' % element['id'],
          type='station',
          open=False,
          color='DodgerBlue')
          
          # loop in the project schedule to create the sub-tasks    
          detailedWorkPlan=element['results'].get('detailedWorkPlan',{})
          
          projectIds=[]
          for record in detailedWorkPlan:
              if record['project'] not in projectIds:
                  projectIds.append(record['project'])
          for projectId in projectIds:
              timesInStation=[]
              for record in detailedWorkPlan:
                  if record['project']==projectId:
                      timesInStation.append(float(record['time']))
              entranceTime=int(min(timesInStation))
              exitTime=int(max(timesInStation)+1)
              task_dict[element['id']+projectId] = dict(
                  id=element['id']+projectId,
                  parent=element['id'],
                  text=projectId,
                  start_date=self.convertToRealWorldTime(entranceTime).strftime(date_format),
                  stop_date=self.convertToRealWorldTime(exitTime).strftime(date_format),
                  open=False,
                  duration=exitTime-entranceTime,
                  color='cyan',
                  entranceTime=entranceTime
              )

      # sort the tasks for an order according to the entrance time of the first component
      for task_id, task in task_dict.iteritems():
          if not task.get('entranceTime',None):
              childrenTimes=[]
              for t_id, t in task_dict.iteritems():
                  if t.get('parent',None)==task_id and not (t.get('entranceTime',None)==None):
                      childrenTimes.append(t['entranceTime'])
              if childrenTimes:
                  task['entranceTime']=min(childrenTimes)      

      # return the result to the gadget
      result[self.configuration_dict['output_id']] = dict(
        time_unit=self.getTimeUnitText(),
        task_list=sorted(task_dict.values(),
          key=lambda task: (task.get('parent'),
                            task.get('type') == 'station',
                            task.get('entranceTime'),
                            task.get('id'))))
    return data
