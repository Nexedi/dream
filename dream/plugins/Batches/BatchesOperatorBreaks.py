from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
import datetime
from copy import copy

class BatchesOperatorBreaks(plugin.InputPreparationPlugin, TimeSupportMixin):
  """ Output the schedule of operators in an Excel file to be downloaded
  """

  def preprocess(self, data):
    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
        now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
        data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
        now = strptime(data['general']['currentDate'], '%Y/%m/%d')
        data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)

    breakData=data['input']['operator_shift_spreadsheet']     
    PBData=copy(data['input'].get('operator_skill_spreadsheet', None)) 

    # create a string with all operator ids ids separated by commas
    allString=''
    for row in PBData:
        if row[0]:
            allString+=row[0]
            allString+=','
            
    # if in operator shift there is ALL in a cell then give the all string 
    for element in breakData:
        if element[1] in ['ALL','All','all']:
            element[1]=allString   

    for row in breakData:
        if row[0] in ['Date', '', None]:
            continue
        date=strptime(row[0], '%Y/%m/%d')
        operators=row[1].split(',')
        
        # if element has spaces in beginning or in end remove them
        operators=self.stripStringsOfList(operators)
        # remove empty strings
        operators = filter(bool, operators) 

        i=4
        while row[i] not in ['', None]:
            breakStart=self.convertToSimulationTime(strptime("%s %s" % (row[0], row[i]), '%Y/%m/%d %H:%M'))
            i+=1
            breakEnd=self.convertToSimulationTime(strptime("%s %s" % (row[0], row[i]), '%Y/%m/%d %H:%M'))
            i+=1
            # if the end of break shift already finished we do not need to consider in simulation
            if breakStart<0 and breakEnd<=0:
                continue
            # if the start of the shift is before now, set the start to 0
            if breakStart<0:
                breakStart=0
            # sometimes the date may change (e.g. break from 23:00 to 01:00). 
            # these would be declared in the date of the start so add a date (self.timeUnitPerDay) to the end
            if breakEnd<breakEnd:
                breakEnd+=self.timeUnitPerDay  
            # add the break to the operator
            for operator in operators:
                PB=data['graph']['node'][operator]
                interruptions=PB.get('interruptions',{})
                scheduledBreaks=interruptions.get('scheduledBreak',{})
                if scheduledBreaks:
                    scheduledBreaks['breakPattern'].append([breakStart,breakEnd])
                else:
                    PB['interruptions']['scheduledBreak']={
                              "endUnfinished": 0, 
                              "breakPattern": [
                                   [
                                        breakStart, 
                                        breakEnd
                                   ]
                              ]
                        }  
    
    return data
