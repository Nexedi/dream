from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime
from copy import copy

class BatchesOperatorGantt(plugin.OutputPreparationPlugin, TimeSupportMixin):

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
    
    colorList=['blue','green','red',
               'gold','Aqua',
               'DarkRed','Fuchsia','Gray',
               'magenta','yellow','Olive',
               'orange','purple','pink','BlanchedAlmond',
               'BurlyWood','HotPink','LightGoldenRodYellow'               
               ]
        
    # create a dictionary so that all stations have their own color
    colorDict={}
    nodes=data['graph']['node']
    i=0
    for node_id, node in nodes.iteritems():
        if node['_class'].startswith('Dream.BatchScrapMachine') or node['_class']=='Dream.M3':
            colorDict[node_id]=colorList[i]
            i+=1
            if i==len(colorList):   
                i=0
    # set off-shift color to white
    colorDict['off-shift']='white'
    colorDict['on-break']='black'

    for element in resultElements:
        if element['_class']=="Dream.Operator":
            operatorId=element['id']       
            schedule=copy(element['results']['schedule']) 
            hasOnShift=False
            
            # if the operator was off-shift all through the simulation run no need to be outputted in Gantt
            for record in schedule: 
                if not record['stationId']=='off-shift':
                    hasOnShift=True
                    break
            if not hasOnShift:
                continue
            
            # add the operator in the task_dict
            task_dict[element['id']] = dict(
            id=operatorId,
            text=operatorId,
            type='operator',
            open=False)
                    
            # in the cases the operator exits and the enters in the same station merge those records
            k=0
            for record in schedule:
                for nextRecord in schedule[k+1:]:
                    # break on the first element with different stationId
                    if not (nextRecord['stationId']==record['stationId']):
                        break
                    # if the stationId is the same break
                    if nextRecord['stationId']==record['stationId']\
                            and not record is schedule[-1]:
                        nextExitTime=nextRecord.get('exitTime',maxSimTime)
                        record['exitTime']=nextExitTime
                        schedule.remove(nextRecord)
                    else:
                        continue    
                k+=1     
            # loop though the records   
            k=1
            for record in schedule:
                entranceTime=record['entranceTime']
                exitTime=record.get('exitTime',None)
                if not exitTime:
                    exitTime=maxSimTime
                k+=1     
                task_dict[operatorId+record['stationId']+str(k)] = dict(
                    id=operatorId+record['stationId']+str(k),
                    parent=operatorId,
                    text=record['stationId'],
                    start_date=self.convertToRealWorldTime(
                          entranceTime).strftime(date_format),
                    stop_date=self.convertToRealWorldTime(
                          exitTime).strftime(date_format),
                    open=False,
                    entranceTime=entranceTime,
                    duration=exitTime-entranceTime,
                    color=colorDict[record['stationId']]
                )           
         
    # return the result to the gadget
    result = data['result']['result_list'][-1]
    result[self.configuration_dict['output_id']] = dict(
      time_unit=self.getTimeUnitText(),
      subscales=[dict(unit="hour", step=1, date="%H:%i")],
      task_list=sorted(task_dict.values(),
        key=lambda task: (task.get('parent'),
                          task.get('type') == 'project',
                          task.get('entranceTime'),task.get('id'))))
    return data
