from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime

class JSComponentTabSchedule(plugin.OutputPreparationPlugin, TimeSupportMixin):
  '''outputs the Job Schedules in tabular format'''
  # XXX hard-coded; class of the order components 
  COMPONENT_CLASS_SET = set(["Dream.Mould", "Dream.OrderComponent", "Dream.OrderDesign"])
  def postprocess(self, data):
    """Post process the job schedules and formats to be presented in tabular format
    """
    numberOfReplications = int(data['general']['numberOfReplications'])

    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
      data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d')
      data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    date_format = '%d-%m-%Y %H:%M'
    
    

    resultElements=data['result']['result_list'][-1]['elementList']
    # create the titles row
    result = data['result']['result_list'][-1]
    result[self.configuration_dict['output_id']] = [['Job ID',
                                                     'Order',
                                                     'Task ID',
                                                     'Station ID',
                                                     'Entrance Time',
                                                     'Processing Time',
                                                     'Operator']]
    for element in resultElements:
      if element.get("_class",None) in self.COMPONENT_CLASS_SET:
        elementId = element.get("id", None)
        # due date                    ????
        # order                       ????
        
        '''schedule'''
        results = element.get("results", {})
        schedule = results.get("schedule", [])
        if schedule:
          for step in schedule:
            # entranceTime
            entranceTime = step.get("entranceTime", None)
            exitTime = step.get("exitTime", None)
            # processing time
            if exitTime != None:
              processingTime = exitTime - entranceTime
            # stationId
            stationId = step.get("stationId", None)
            # operator                    ????
            
            # task_id
            task_id = step.get("task_id", None)
            if task_id:
              print "task_id", task_id
              result[self.configuration_dict['output_id']].append([elementId,
                                                                   "",
                                                                   task_id,
                                                                   stationId,
                                                                   self.convertToFormattedRealWorldTime(entranceTime),
                                                                   processingTime,
                                                                   ""])
    return data
