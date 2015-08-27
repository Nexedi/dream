from datetime import datetime
import random
from pprint import pformat

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime
from copy import copy

'''outputs the Operator Schedules in tabular format'''
class JSOperatorTabSchedule(plugin.OutputPreparationPlugin, TimeSupportMixin):

    
    def postprocess(self, data):
        """Post process Operator job schedules and formats to be presented in tabular format
        """
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
        '''reading results'''
        for result in data['result']['result_list']:
            self.result = result
            resultElements=result['elementList']
            # create the titles row
            result[self.configuration_dict['output_id']] = [['Operator',
                                                             'Job ID',
                                                             'Task ID',
                                                             'Station ID',
                                                             'Entrance Time',
                                                             'Exit Time',
                                                             ]]
            for element in resultElements:
                if element.get("_class",None) == 'Dream.Operator':
                    operatorId=element.get('id',None)
                    results = element.get("results", {})
                    schedule = results.get("schedule", [])
                    for step in schedule:
                        # entranceTime
                        entranceTime = step.get("entranceTime", None)
                        exitTime = step.get("exitTime", None)
                        entityId = step.get("entityId", None)
                        stationId = step.get("stationId", None)
                        task_id = step.get("task_id", None)
                        if stationId!='off-shift':
                            result[self.configuration_dict['output_id']].append([operatorId,
                                                                                 entityId,
                                                                                 task_id,
                                                                                 stationId,
                                                                                 self.convertToFormattedRealWorldTime(entranceTime),
                                                                                 self.convertToFormattedRealWorldTime(exitTime)
                                                                        ])
        
        return data
    
    