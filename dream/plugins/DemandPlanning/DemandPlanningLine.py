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
            #"minTickSize": [1, self.getTimeUnitText()],
            "minTickSize": [1, "day"],
          },
          "legend": {
            "backgroundOpacity": 0.1,
            "position":"se",
            },
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
      #ticks = list(enumerate(bottleneckData.keys()))
      ticks = list(enumerate(G.Bottlenecks))
      
      options = { 
        "xaxis": {
          "minTickSize": 1,
          "ticks": ticks
        },
        "legend": {
            "backgroundOpacity": 0.1,
            "position":"se",
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
            "data": list(enumerate([bottleneckData[x][utilizationType] for x in G.Bottlenecks])),
        })
            
    return data

class BottleNeckLoadByWeek(plugin.OutputPreparationPlugin, TimeSupportMixin):
  """ Output the queue statistics in a format compatible with Output_viewGraph, for the second widget by week.
  """

  def postprocess(self, data):
 
    from dream.simulation.applications.DemandPlanning.Globals import G
    
    result = data['result']['result_list'][-1]
    bottleNeckUtilizationDict = result['bottleneck_load_by_week'] = {}

    by_week = {}
    # change {bottleneck: {ma: {week:data }}} in {(bottleneck, week): {ma: data}}
    maxUtilisation = 0
    for bottleneck, bottleNeckUtilization in G.Butilisation.iteritems():
      for ma, record in bottleNeckUtilization.iteritems():
          for week, value in record.iteritems():
              by_week.setdefault((bottleneck, week), {})[ma] = value
              if value > maxUtilisation:
                maxUtilisation = value
    #maxUtilisation += 10 - maxUtilisation%10
    maList = []
    for sp in G.SPs:
        for ma in G.SPlist[sp]:
            maList.append(ma)
            
    for Bweek, bottleneckData in by_week.items():
      series = []
      if len(maList)<=10:
        ticks = list(enumerate(maList))
      else:
        ticks = list(enumerate(range(len(maList))))
        
      options = { 
        "xaxis": {
          "minTickSize": 1,
          "ticks": ticks,
          "axisLabel": "MAs"
        },
        "yaxis": {
          "min": 0,
          "max": round(maxUtilisation),
          "axisLabel": "Utilisation %"
        },
        "legend": {
            "backgroundOpacity": 0.1,
            "position":"se",
            },
        "series": {
          "bars": {
            "show": True,
            "barWidth": 0.70,
            "order": 1,
            "align": "center"
          },
          "stack": False
        }
      }
      
      weekLabel = "%s %s" % (str(Bweek[0]), str(Bweek[1]))
      bottleNeckUtilizationDict[weekLabel] = {
        "series": series,
        "options": options
      }
      
      # create the 3 bars
      series.append({
        "label": '',
        "data": list(enumerate([bottleneckData[x] for x in maList])),
        "color": "blue"
        })
            
    return data