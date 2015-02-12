from dream.plugins import plugin

class ParseTraceFile(plugin.OutputPreparationPlugin):
  """ Output the result of demand planning in a format compatible with
  Output_viewDownloadFile
  """

  def postprocess(self, data):  
    outPutFile=None
    for record in data['result']['result_list'][-1]['elementList']:
        if record.get('id',None)=='TraceFile':
            outPutFile=record
        
    data['result']['result_list'][-1][self.configuration_dict['output_id']] = {
          'name': 'Trace.xlsx',
          'mime_type': 'application/vnd.ms-excel',
          'data': outPutFile
        }
    print data['result']['result_list'][-1][self.configuration_dict['output_id']]['data']
    return data
