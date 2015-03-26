from dream.plugins import plugin

class PostProcessDemandPlanning(plugin.OutputPreparationPlugin):
  """ Output the result of demand planning in a format compatible with
  Output_viewDownloadFile
  """

  def postprocess(self, data):
    # XXX the event generator should store its result in data and not in global
    # variable.
    from dream.simulation.applications.DemandPlanning.Globals import G
    data['result']['result_list'][-1][self.configuration_dict['output_id']] = {
      'name': 'Result.xlsx',
      'mime_type': 'application/vnd.ms-excel',
      'data': G.reportResults.xlsx.encode('base64')
    }
    return data
