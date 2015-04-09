from copy import copy, deepcopy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class DateTimeConvert(plugin.InputPreparationPlugin, TimeSupportMixin):
    """ Input preparation 
    """

    def preprocess(self, data):
        strptime = datetime.datetime.strptime
        # read the current date and define dateFormat from it
        try:
            now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
            data['general']['dateFormat']='%Y/%m/%d %H:%M'
        except ValueError:
            now = strptime(data['general']['currentDate'], '%Y/%m/%d')
            data['general']['dateFormat']='%Y/%m/%d'
        self.initializeTimeSupport(data)

        BOM = data['input']['BOM']
        
        outputJSONString=json.dumps(BOM, indent=True)
        outputJSONFile=open('DateTimeConvert.json', mode='w')
        outputJSONFile.write(outputJSONString)
        
        orders = BOM.get('productionOrders', [])
        wip = BOM.get('WIP', {})
        
        for ent_key, entity in wip.iteritems():
            task_id = entity.get('task_id', None)
            proc_time = 0;
            timeOut = entity.pop('timeOut', None)
            timeIn = entity.pop('timeIn', 'NA')
            if not timeIn=='NA':
                timeIn = strptime(timeIn, '%Y-%m-%d %H:%M:%S')
            if timeOut:
                entity['remainingProcessingTime'] = 0
            else:
                #calculate the time difference between the TIMEIN and the moment the user wants to run the simulation (e.g. datetime.now())
                print type(now)
                print type(timeIn)
                timeDelta= now - timeIn
                if self.timeUnit == 'second':
                  timeDiff = timeDelta.total_seconds() #24 * 60 * 60
                elif self.timeUnit == 'minute':
                  timeDiff = timeDelta.total_seconds()/60 #24 * 60
                elif self.timeUnit == 'hour':
                  timeDiff = timeDelta.total_seconds()/(60*60)
                elif self.timeUnit == 'day':
                  timeDiff = timeDelta.total_seconds()/(60*60*24) #1.
                elif self.timeUnit == 'week':
                  timeDiff = timeDelta.total_seconds()/(60*60*24*7) #1 / 7.
                elif self.timeUnit == 'month':
                  timeDiff = timeDelta.total_seconds()/(60*60*24*7*30) #1 / 30.
                elif self.timeUnit == 'year':
                  timeDiff = timeDelta.total_seconds()/(60*60*24*7*30*360) #1 / 360.
                else:
                  raise ValueError("Unsupported time unit %s" % self.timeUnit)

                for order in orders:
                    comps = order.get('componentsList', [])
                    for comp in comps:
                        if comp['id'] == ent_key:
                            for step in comp.get('route', []):
                                if step.get('task_id', None) == task_id:
                                    proc_time = step.get('processingTime', {}).get('Fixed',{}).get('mean', 0)
                                    print proc_time
                                    break
                        if proc_time:
                            break
                    if proc_time:
                        break
                #calculate the remaining time the part needs to be processed 
                entity['remainingProcessingTime']= round((proc_time - timeDiff),2) 

        for order in orders:
            orderDate = order.get('orderDate', None)
            order['orderDate'] = self.convertToSimulationTime(strptime("%s" % orderDate, '%Y-%m-%d %H:%M:%S'))
            dueDate = order.get('dueDate', None)
            order['dueDate'] = self.convertToSimulationTime(strptime("%s" % dueDate, '%Y-%m-%d %H:%M:%S'))

        return data