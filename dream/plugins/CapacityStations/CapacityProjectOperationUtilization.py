from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from datetime import datetime, timedelta
from copy import deepcopy

class PeriodUtilizations(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph, for the second widget by week.
  """

  def postprocess(self, data):

    startPeriod = datetime.strptime(data['general']['currentDate'], data['general']['dateFormat'])
    for result in data['result']['result_list']:
        self.initializeTimeSupport(data)
        #bottleNeckUtilizationDict = result['capacity_utilization'] = {}
        operationNames = []
        byPeriod = dict((period,{}) for period in range(len(result['elementList'][10]['results']['capacityUsed'])))
        opNo = 0
        operationUtil = {}
        for recd in result['elementList']:
            if recd.get('family') == 'CapacityStation':
                operationNames.append(recd.get('id'))
                operationUtil[recd.get('id')] = []
                #projectNames = list(set([rc['project'] for rc in recd['results']['detailedWorkPlan']]))
                for prd,pln in enumerate(recd['results']['capacityUsed']):
                    currentPeriod = str(startPeriod + timedelta(days=prd))[:10]
                    #totalCapa = max(0.01,sum([pln.setdefault(project,0) for project in projectNames]))
                    totalUtilization = pln["utilization"]
                    operationUtil[recd.get('id')].append([prd,pln["utilization"]])
                ticks = [lb[0] for lb in operationUtil[recd.get('id')]]

        series = []
        options = {"xaxis": {"ticks": ticks, "minTickSize": [1, self.getTimeUnitText()]}}
        result['capacity_utilization'] = {"series": series,"options": options}

        for operation in operationUtil:
            series.append({"label": operation, "data": operationUtil[operation]})
            #currentPeriod = str(startPeriod + timedelta(days=pd))[:10]
            #ticks = [[num,oprtn] for num,oprtn in enumerate(operationNames)]
            #label = operation
            #ticks = list(enumerate(operationNames))

            #options = {"xaxis": {"minTickSize": 1,"ticks": ticks},"series": {"bars": {"show": True,"barWidth": 0.10,"order": 1,"align": "center"},"stack": False}}
            #bottleNeckUtilizationDict = {"series": series,"options": options}
            #for pj in byPeriod[pd]:
            #series.append({"label":operation,"data": operationUtil[operation]})

    return data
