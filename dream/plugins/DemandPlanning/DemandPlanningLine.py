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
                ( 'averageUtilization', 'Average Utilization' ),
                ( 'minUtilization', 'Min Utilization' ),
                ( 'maxUtilization', 'Max Utilization' ) ]:
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
