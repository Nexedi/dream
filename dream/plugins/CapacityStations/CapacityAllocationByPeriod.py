from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from datetime import datetime, timedelta
from copy import deepcopy

class StationAllocations(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph, for the second widget by week.
  """

  def postprocess(self, data):


    startPeriod = datetime.strptime(data['general']['currentDate'], data['general']['dateFormat'])
    for result in data['result']['result_list']:
    #result = data['result']['result_list'][0]
        bottleNeckUtilizationDict = result['bottleneck_utilization_by_week'] = {}
        operationNames = []
        byPeriod = dict((period,{}) for period in range(len(result['elementList'][10]['results']['capacityUsed'])))
        opNo = 0
        for recd in result['elementList']:
            if recd.get('family') == 'CapacityStation':
                operationNames.append(recd.get('id'))
                projectNames = list(set([rc['project'] for rc in recd['results']['detailedWorkPlan']]))
                for prd,pln in enumerate(recd['results']['capacityUsed']):
                    totalCapa = max(0.01,sum([pln.setdefault(project,0) for project in projectNames]))
                    totalUtilization = pln["utilization"]
                    for pr in projectNames:
                        if pr in byPeriod[prd]:#byPeriod[prd]:
                            byPeriod[prd][pr].append([opNo,(pln.setdefault(pr,0)/totalCapa * totalUtilization)])
                        else:
                            byPeriod[prd][pr] = [[opNo,(pln.setdefault(pr,0)/totalCapa * totalUtilization)]]
                opNo += 1
        for pd in byPeriod:
            series = []
            currentPeriod = str(startPeriod + timedelta(days=pd))[:10]
            #ticks = [[num,oprtn] for num,oprtn in enumerate(operationNames)]
            ticks = list(enumerate(operationNames))
            options = {"xaxis": {"minTickSize": 1,"ticks": ticks},"series": {"bars": {"show": True,"barWidth": 0.10,"order": 1,"align": "center"},"stack": False}}
            bottleNeckUtilizationDict[currentPeriod] = {"series": series,"options": options}
            for pj in byPeriod[pd]:
                series.append({"label":pj,"data": byPeriod[pd][pj]})

    return data
