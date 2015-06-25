from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime
from copy import copy

class JSComponentTabSchedule(plugin.OutputPreparationPlugin, TimeSupportMixin):
  '''outputs the Job Schedules in tabular format'''
  def findParentOrderById(self, ID):
    '''returns the parent order of the component with id == ID'''
    orders = self.data["input"]["BOM"].get("productionOrders", [])
    for order in orders:
      components = order.get("componentsList", [])
      for component in components:
        if ID == component["id"]:
          return order
    return {}
    
  # XXX hard-coded; class of the resources
  OPERATOR_CLASS_SET = set(["Dream.Operator"])
  def findOperatorByTaskId(self, ID):
    '''returns the id of the operator that has performed a certain task'''
    # XXX searching in the last solution only
    # XXX synchronize with the solution that is used by postprocess method
    resultElements=self.result['elementList']
    for element in resultElements:
      if element.get("_class", None) in self.OPERATOR_CLASS_SET:
        schedule = element["results"].get("schedule", [])
        for step in schedule:
          taskId = step.get("task_id", None)
          if taskId == ID:
            return element.get("id", "")
    return ""

  # XXX hard-coded; class of the active stations
  STATION_CLASS_SET = set(["Dream.MouldAssembly", "Dream.MachineJobShop"])
  def isActiveStation(self, ID):
    '''returns True if station is an active station'''
    resultElements=self.result['elementList']
    for element in resultElements:
      if element.get("_class", None) in self.STATION_CLASS_SET:
        if  element.get("id", None) == ID:
          return True
    return False

  # XXX hard-coded; class of the order components 
  COMPONENT_CLASS_SET = set(["Dream.Mould", "Dream.OrderComponent", "Dream.OrderDesign"])
  def postprocess(self, data):
    """Post process the job schedules and formats to be presented in tabular format
    """
    self.data = data
    numberOfReplications = int(data['general'].get('numberOfReplications',1))
    '''Time definition'''
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
    
    '''reading results'''
    for result in data['result']['result_list']:
      self.result = result
      resultElements=result['elementList']
      # create the titles row
      result[self.configuration_dict['output_id']] = [['Job ID',
                                                       'Order',
                                                       'Due Date',
                                                       'Task ID',
                                                       'Station ID',
                                                       'Entrance Time',
                                                       'Processing Time',
                                                       'Operator']]
      for element in resultElements:
        if element.get("_class",None) in self.COMPONENT_CLASS_SET:
          elementId = element.get("id", None)
          order = self.findParentOrderById(elementId)
          # due date
          dueDate = order.get("dueDate", None)
          # order
          orderName = order.get("name", None)
          '''schedule'''
          results = element.get("results", {})
          schedule = results.get("schedule", [])
          if schedule:
            for step in schedule:
              # entranceTime
              entranceTime = step.get("entranceTime", None)
              exitTime = step.get("exitTime", None)
              # processing time
              processingTime = 0
              if exitTime != None:
                processingTime = round(exitTime - entranceTime, 2)
              # stationId
              stationId = step.get("stationId", None)
              # task_id
              task_id = step.get("task_id", None)
              # operator
              operatorId = ""
              if self.isActiveStation(stationId):
                operatorId = self.findOperatorByTaskId(task_id)
              # if there is a taskId defined or the station is an assembly station (order decomposition is presented)
              if task_id or stationId.startswith("ASSM"):
                result[self.configuration_dict['output_id']].append([elementId,
                                                                     orderName,
                                                                     self.convertToFormattedRealWorldTime(dueDate),
                                                                     task_id,
                                                                     stationId,
                                                                     self.convertToFormattedRealWorldTime(entranceTime),
                                                                     processingTime,
                                                                     operatorId])
    
    try:
        # remove all the elements that have to do with buffers
        tabElements=copy(result[self.configuration_dict['output_id']])
        tabElements.pop(0)
    
        for row in tabElements:
            stationId=row[4]
            stationClass=data['graph']['node'][stationId]['_class']
            if stationClass in ['Dream.MouldAssemblyBuffer','Dream.ConditionalBuffer','Dream.OrderDecomposition']:
                result[self.configuration_dict['output_id']].remove(row)
        
        # sort the elements according to Entrance Time        
        firstRow=result[self.configuration_dict['output_id']].pop(0) 
        result[self.configuration_dict['output_id']].sort(key=lambda x: x[5])
        result[self.configuration_dict['output_id']].insert(0,firstRow)
    except:
        pass
    return data
