from dream.plugins import plugin
import xlwt
import StringIO

class BatchesOperatorSpreadsheet(plugin.OutputPreparationPlugin):
  """ Output the schedule of operators in an Excel file to be downloaded
  """

  def postprocess(self, data):
    rowIndex=0
    scheduleFile = xlwt.Workbook() 
    scheduleSheet = scheduleFile.add_sheet('Operator Schedule', cell_overwrite_ok=True)
    scheduleSheet.write(rowIndex,0,'Operator')
    scheduleSheet.write(rowIndex,1,'Machine')
    scheduleSheet.write(rowIndex,2,'Start Time')
    scheduleSheet.write(rowIndex,3,'End Time')
    
    
    scheduleStringIO = StringIO.StringIO()
    scheduleFile.save(scheduleStringIO)
    encodedScheduleFile=scheduleStringIO.getvalue().encode('base64') 
    data['result']['result_list'][-1][self.configuration_dict['output_id']] = {
      'name': 'Operator_Schedule.xls',
      'mime_type': 'application/vnd.ms-excel',
      'data': encodedScheduleFile
    }
    return data
