from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from datetime import datetime, timedelta

class StationAllocations(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the periodic operational capacity utilisation per project in a bar chart
  """

  def postprocess(self, data):

    startPeriod = datetime.strptime(data['general']['currentDate'], data['general']['dateFormat'])
    for result in data['result']['result_list']:
        bottleNeckUtilizationDict = result['bottleneck_utilization_by_week'] = {}
        operationNames = []
        for station in result['elementList']:
            if station.get('family') == 'CapacityStation':
                byPeriod = dict((period,{}) for period in range(len(station['results']['capacityUsed'])))
                break

        opNo = 0
        for station in result['elementList']:
            if station.get('family') == 'CapacityStation':
                operationNames.append(station.get('id'))
                projectNames = list(set([rc['project'] for rc in station['results']['detailedWorkPlan']]))
                for period,record in enumerate(station['results']['capacityUsed']):
                    totalCapa = max(0.01,sum([record.setdefault(project,0) for project in projectNames]))
                    totalUtilization = record["utilization"]
                    for pr in projectNames:
                        if pr in byPeriod[period]:
                            byPeriod[period][pr].append([opNo,(record.setdefault(pr,0)/totalCapa * totalUtilization)])
                        else:
                            byPeriod[period][pr] = [[opNo,(record.setdefault(pr,0)/totalCapa * totalUtilization)]]
                opNo += 1
        for prd in byPeriod:
            series = []
            currentPeriod = str(startPeriod + timedelta(days=prd))[:10]
            ticks = list(enumerate(operationNames))
            options = {"xaxis": {"minTickSize": 1,"ticks": ticks},"series": {"bars": {"show": True,"barWidth": 0.10,"order": 1,"align": "center"},"stack": False}}
            bottleNeckUtilizationDict[currentPeriod] = {"series": series,"options": options}
            for pj in byPeriod[prd]:
                series.append({"label":pj,"data": byPeriod[prd][pj]})

    return data
