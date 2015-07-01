from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from datetime import datetime, timedelta
from copy import deepcopy

class PeriodUtilizations(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output a line plot of operational capacity utilisations.
  """

  def postprocess(self, data):

    startPeriod = datetime.strptime(data['general']['currentDate'], data['general']['dateFormat'])
    for result in data['result']['result_list']:
        self.initializeTimeSupport(data)

        operationUtil = {}
        for recd in result['elementList']:
            if recd.get('family') == 'CapacityStation':
                operationUtil[recd.get('id')] = []
                for prd,pln in enumerate(recd['results']['capacityUsed']):
                    currentPeriod = startPeriod + timedelta(days=prd)
                    timestamp = (currentPeriod - datetime(1970, 1, 1)).total_seconds()
                    operationUtil[recd.get('id')].append([timestamp*1000,pln["utilization"]])

        series = []
        options = {"xaxis": {"mode":"time", "minTickSize": [1, self.getTimeUnitText()]}}
        result['capacity_utilization'] = {"series": series,"options": options}

        for operation in operationUtil:
            series.append({"label": operation, "data": operationUtil[operation]})

    return data
