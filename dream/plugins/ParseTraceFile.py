from dream.plugins import plugin

class ParseTraceFile(plugin.OutputPreparationPlugin):
  """ Output the result of demand planning in a format compatible with
  Output_viewDownloadFile
  """

  def postprocess(self, data):  
    outPutFile=None
    for record in data['result']['result_list'][-1]['elementList']:
        if record.get('id',None)=='TraceFile':
            outPutFile=record['results']['trace']
    data['result']['result_list'][-1][self.configuration_dict['output_id']] = {
          'name': 'Trace.xls',
          'mime_type': 'application/vnd.ms-excel',
          'data': outPutFile
        }
    return data
