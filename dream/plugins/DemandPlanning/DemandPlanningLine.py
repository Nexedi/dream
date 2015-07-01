from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from datetime import datetime

class DemandPlanningLine(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph
  """

  def postprocess(self, data):
 
    from dream.simulation.applications.DemandPlanning.Globals import G
    
    result = data['result']['result_list'][-1]
    bottleNeckUtilizationDict = result['bottleneck_utilization'] = {}

    for bottleneck, bottleNeckUtilization in G.Utilisation.iteritems():

        dateList=[]
        # get the current date from the data
        for record_id,record in bottleNeckUtilization.iteritems():
            year=str(record_id)[0:4]
            week=str(record_id)[4:]
            fullDate=datetime.strptime(year+'-'+week+'-0', '%Y-%W-%w')
            dateList.append(fullDate)
        
        # XXX We need to make TimeSupportMixin resuable. We should not have to do this.
        currentDate=str(min(dateList))
        currentDate=currentDate.replace('-', '/')
        data['general']['currentDate']=currentDate
        data['general']['timeUnit']='week'
        self.initializeTimeSupport(data)
        
        series = []
        options = {
          "xaxis": {
            "mode": "time",
            "minTickSize": [1, self.getTimeUnitText()],
          }
        }
     
        bottleNeckUtilizationDict[bottleneck] = {
          "series": series,
          "options": options
        }
        
        # create the 3 lines
        for (utilizationType, utilizationLabel) in [
                ( 'minUtilization', 'Min Utilization' ),
                ( 'averageUtilization', 'Actual Utilization' ),
                ( 'maxUtilization', 'Target Utilization' ) ]:
            utilizationList=[]
            for record_id, record in bottleNeckUtilization.iteritems():
                year=str(record_id)[0:4]
                week=str(record_id)[4:]
                fullDate=datetime.strptime(year+'-'+week+'-0', '%Y-%W-%w')
                utilizationList.append([fullDate,record[utilizationType]])

            utilizationList.sort(key=lambda x: x[0], reverse=True)    
            series.append({
                "label": utilizationLabel,
                "data": [((time-datetime(1970, 1, 1)).total_seconds()*1000, value) for (time, value) in utilizationList]
            })
            
    return data



class BottleNeckByWeek(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph, for the second widget by week.
  """

  def postprocess(self, data):
 
    from dream.simulation.applications.DemandPlanning.Globals import G
    
    result = data['result']['result_list'][-1]
    bottleNeckUtilizationDict = result['bottleneck_utilization_by_week'] = {}

    by_week = {}
    # change {bottleneck: {week: data }} in {week: {bottleneck: data}}
    for bottleneck, bottleNeckUtilization in G.Utilisation.iteritems():
      for record_id, record in bottleNeckUtilization.iteritems():
        by_week.setdefault(record_id, {})[bottleneck] = record

    for week, bottleneckData in by_week.items():
      series = []
      ticks = list(enumerate(bottleneckData.keys()))
      
      options = {
        "xaxis": {
          "minTickSize": 1,
          "ticks": ticks
        },
        "series": {
          "bars": {
            "show": True,
            "barWidth": 0.10,
            "order": 1,
            "align": "center"
          },
          "stack": False
        }
      }
      
      weekLabel = "%s %s" % (str(week)[:4], str(week)[4:])
      bottleNeckUtilizationDict[weekLabel] = {
        "series": series,
        "options": options
      }
      
      # create the 3 bars
      for (utilizationType, utilizationLabel) in [
                ( 'minUtilization', 'Min Utilization' ),
                ( 'averageUtilization', 'Actual Utilization' ),
                ( 'maxUtilization', 'Target Utilization' ) ]:
        series.append({
            "label": utilizationLabel,
            "data": list(enumerate([x[utilizationType] for x in bottleneckData.values()])),
        })
            
    return data
