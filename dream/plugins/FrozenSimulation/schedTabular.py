
from dream.plugins import plugin
from operator import itemgetter

class schedTabular(plugin.OutputPreparationPlugin):
    """ Output the schedule in a tab
    """

    def postprocess(self, data):
      data['result']['result_list'][0]['schedule_output'] = [['Project', 'Part', 'Task ID', 'Station', 'Operator', 'Start Time', 'End Time']]
      from dream.simulation.applications.FrozenSimulation.Globals import G
      # sort schedule items in start time ascending order
      sList = []
      for entry in G.tabSchedule:
        if 'End Time' not in entry:
          sList.append([x for x in entry])
      sList = sorted(sList, key=itemgetter(5))
      for item in sList:
        data['result']['result_list'][0]['schedule_output'].append(item)
            
      return data