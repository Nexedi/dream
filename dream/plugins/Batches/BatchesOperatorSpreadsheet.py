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
    headingStyle=xlwt.easyxf("font: bold on; borders: bottom dashed;font: color red;") 
    PBstyle=xlwt.easyxf("font: bold on;font: color red;")    
    scheduleSheet.write(rowIndex,0,'Operator',headingStyle)
    scheduleSheet.write(rowIndex,1,'Machine',headingStyle)
    scheduleSheet.write(rowIndex,2,'Start Time',headingStyle)
    scheduleSheet.write(rowIndex,3,'End Time',headingStyle)
    rowIndex+=1
    
    solutionList=None
    # get the result the the router gives
    for element in data['result']['result_list'][-1]['elementList']:
        if element['_class']=='Dream.SkilledRouter':
            solutionList=element['results']['solutionList']
    
    if solutionList:
        # create a list with all the operator ids that were at least in one allocation
        operatorList=[]
        for record in solutionList:
            for key in record['allocation']:
                if key not in operatorList:
                    operatorList.append(key)
    
        # create for every operator a list like [time,machineId]. If the operator is not in the solution latter is to None
        normalizedSchedule={}
        for operator in operatorList:
            operatorSchedule=[]
            normalizedSchedule[operator]=[]
            for record in solutionList:
                time=record['time']
                allocation=record['allocation']
                machineId=None
                if operator in allocation.keys():
                    machineId=allocation[operator]
                operatorSchedule.append([time,machineId])
    
            # now create a normalized schedule for the operator like [MachineId, EntranceTime, ExitTime]
            k=0
            for record in operatorSchedule:
                normalizedSchedule[operator].append([record[1],record[0]])
                for nextRecord in operatorSchedule[k+1:]:
                    if nextRecord[1]==record[1]:
                        operatorSchedule.remove(nextRecord)
                    else:
                        normalizedSchedule[operator][-1].append(nextRecord[0])
                        break
                k+=1  
        
        # output the results in excel
        for operator in normalizedSchedule.keys():
            scheduleSheet.write(rowIndex,0,operator,PBstyle)
            for record in normalizedSchedule[operator]:
                # skip the records that have 'None'
                if not record[0]:
                    continue
                scheduleSheet.write(rowIndex,1,record[0])
                scheduleSheet.write(rowIndex,2,record[1])
                scheduleSheet.write(rowIndex,3,record[2])
                rowIndex+=1
    
    # return the workbook as encoded
    scheduleStringIO = StringIO.StringIO()
    scheduleFile.save(scheduleStringIO)
    encodedScheduleFile=scheduleStringIO.getvalue().encode('base64') 
    data['result']['result_list'][-1][self.configuration_dict['output_id']] = {
      'name': 'Operator_Schedule.xls',
      'mime_type': 'application/vnd.ms-excel',
      'data': encodedScheduleFile
    }
    return data
