from dream.simulation.Default import Simulation as DefaultSimulation
import json

class Simulation(DefaultSimulation):
  def run(self, data):
    if 'spreadsheet' in data:
      wip_dict = {}
      for value_list in data['spreadsheet']:
        if value_list[1] == 'ID' or not value_list[1]:
          continue
        sequence_list = value_list[6].split('-')
        processing_time_list = value_list[7].split('-')
        wip_dict[sequence_list[0]] = [
          {
            "_class": "Dream.Job",
            "id": value_list[1],
            "name": value_list[0],
            "order_date": value_list[2],
            "due_date": value_list[3],
            "priority": value_list[4],
            "material": value_list[5],
            "route": [
              {
                "processingTime": {
                  "distributionType": "Fixed",
                  "mean": processing_time_list[i],
                  },
                "stationId": sequence_list[i],
                "stepNumber": i
              } for i in xrange(len(sequence_list))]
          }
        ]
      for node_id in data['nodes'].keys():
        if node_id in wip_dict:
          data['nodes'][node_id]['wip'] = wip_dict[node_id]
      del(data['spreadsheet'])
      self.logger.debug('preprocessed data:\n%s' % json.dumps(
        data, sort_keys=True, indent=2))
    return DefaultSimulation.run(self, data)
