from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime

class JSComponentGantt(plugin.OutputPreparationPlugin, TimeSupportMixin):
  '''class that gets the results and prepares the data for the component gantt graph'''

  # XXX hard-coded classes of different components to be displayed in the gantt
  COMPONENT_CLASS_SET = set(["Dream.OrderComponent", "Dream.OrderDesign", "Dream.Mould"])
  # XXX hard-coded classes of stations to be displayed in the gantt
  STATION_CLASS_SET = set(["Dream.MachineJobShop", "Dream.MouldAssembly"])
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
    resultElements=data['result']['result_list'][-1]['elementList']
    task_dict = {}
    # loop in the results to find Operators
    for element in resultElements:
      if element['_class'] in self.COMPONENT_CLASS_SET:
        componentId=element['id']
        # add the component in the task_dict
        task_dict[element['id']] = dict(
          id=componentId,
          text=componentId,
          type='component',
          open=False)
    
        k=1
        
        schedule=element['results'].get('schedule', [])
        if schedule:
          for record in schedule:
            stationId = record['stationId']
            stationClass = data["graph"]["node"][stationId]["_class"]
            entranceTime=record['entranceTime']
            taskId = record.get("task_id", None)
            # text to be displayed (if there is no task id display just the stationId)
            if not taskId:
              task_to_display = record['stationId']
            else:
              task_to_display = taskId + "; " + record['stationId']
            # get the exitTime from the record
            exitTime = record.get("exitTime", None)
            if exitTime == None:
              # if there is no exitTime get it from the entranceTime of the next step
              try:
                exitTime=schedule[k]['entranceTime']
              # if there is no next step
              except IndexError:
                exitTime=maxSimTime
            k+=1
            if stationClass in self.STATION_CLASS_SET:
              task_dict[componentId+record['stationId']+str(k)] = dict(
                id=componentId+record['stationId']+str(k),
                parent=componentId,
                text=task_to_display, #record['stationId']+"; "+taskId,
                start_date=self.convertToRealWorldTime(
                      entranceTime).strftime(date_format),
                stop_date=self.convertToRealWorldTime(
                      exitTime).strftime(date_format),
                open=False,
                entranceTime=entranceTime,
                duration=exitTime-entranceTime,
              )           
         
    # return the result to the gadget
    result = data['result']['result_list'][-1]
    result[self.configuration_dict['output_id']] = dict(
      time_unit=self.getTimeUnitText(),
      task_list=sorted(task_dict.values(),
        key=lambda task: (task.get('parent'),
                          task.get('type') == 'project',
                          task.get('entranceTime'),task.get('id'))))
    return data
