from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from datetime import datetime

class DemandPlanningLine(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph
  """

  def postprocess(self, data):
 
    from dream.simulation.applications.DemandPlanning.Globals import G
    utilisation=G.Utilisation
    bottleNeckUtilization=G.Utilisation['BE_T_BE1S_TEST_EQ_FLEX_T417_3']      
    dateList=[]
    for record_id,record in bottleNeckUtilization.iteritems():
        year=str(record_id)[0:4]
        week=str(record_id)[4:]
        fullDate=datetime.strptime(year+'-'+week+'-0', '%Y-%W-%w')
        dateList.append(fullDate)
    currentDate=str(min(dateList))
    currentDate=currentDate.replace('-', '/')
    print currentDate
    data['general']['currentDate']=currentDate
    data['general']['timeUnit']='week'
    self.initializeTimeSupport(data)
    result = data['result']['result_list'][-1]

    series = []
    options = {
      "xaxis": {
        "mode": "time",
        "minTickSize": [1, self.getTimeUnitText()],
      }
    }
 
    result[self.configuration_dict['output_id']] = {
      "series": series,
      "options": options
    }
    
    for utilizationType in ['averageUtilization','minUtilization','maxUtilization']:
        utilizationList=[]
        for record_id,record in bottleNeckUtilization.iteritems():
            year=str(record_id)[0:4]
            week=str(record_id)[4:]
            fullDate=datetime.strptime(year+'-'+week+'-0', '%Y-%W-%w')
            utilizationList.append([fullDate,record[utilizationType]])
            
        utilizationList.sort(key=lambda x: x[0], reverse=True)    
        print utilizationList
        series.append({
            "label": utilizationType,
            "data": [((time-datetime(1970, 1, 1)).total_seconds()*1000, value) for (time, value) in utilizationList]
        })
    return data
