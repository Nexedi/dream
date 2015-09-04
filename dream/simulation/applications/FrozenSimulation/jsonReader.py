'''
Created on 7 Aug 2015

@author: Anna
'''

import json
import tablib
import datetime as dt
import xlrd
from copy import deepcopy
from shiftGeneration import shiftGenerator
from timeCalculations import availableTime_Shift
from Globals import G

def dateToOrdinal(entry, formatDate):
    rec = dt.datetime.strptime(entry,formatDate)
    #rec.toordinal()
    return rec    

def colonTimeStr(entry):
    splitEntry = entry.split(':')
    floatTime = int(splitEntry[0]) + float(splitEntry[1])/60
    return floatTime

def excel_date(date1):
    temp = dt.datetime(1899, 12, 30)
    date1 = dt.datetime.combine(date1, dt.time())
    delta = date1 - temp    
    return float(delta.days) + (float(delta.seconds) / 86400)

def offShiftFormat(colEntry):
    periods = {'Start':[],'Stop':[]}
    sprtdRec = colEntry.split(';'+' ')
    for startANDend in sprtdRec:
        splitstartANDend = str(startANDend).split('-')
        for num,stAstP in enumerate(splitstartANDend):
            splitstAstP = stAstP.split(':')
            firstrec = int(splitstAstP[0]) + float(splitstAstP[1])/60
            if num == 0:
                periods['Start'].append()
            else:
                periods['Stop'].append(int(splitstAstP[0])+ float(splitstAstP[1])/60)
    return periods

def offShiftFormat_2(colEntry, dateNow):
    periods = {}
    sprtdRec = colEntry.split(';'+' ')
    print 'col entry', colEntry
    print 'date', dateNow
    for startANDend in sprtdRec:
        splitstartANDend = str(startANDend).split('-')
        print 'splitstartANDend', splitstartANDend
        
        for num,stAstP in enumerate(splitstartANDend):
            print 'st ast', stAstP
            falseTime = dt.datetime.strptime(stAstP,'%H:%M')
            if num == 0:
                startTime = dt.datetime(year=dateNow.year, month=dateNow.month, day=dateNow.day, hour=falseTime.hour, minute=falseTime.minute)
            else:
                endTime = dt.datetime(year=dateNow.year, month=dateNow.month, day=dateNow.day, hour=falseTime.hour, minute=falseTime.minute)
        periods[startTime] = {'endDate':endTime, 'taskID':'offShift'}
    return periods


def combSchedules(bothSchedList,combData):
    for sch in bothSchedList:
        for cell in sch:
            if len(cell) < 10:
                cell = list(cell)
                cell.extend(['Not Frozen'])
            combData.append(cell)
    print combData['Date']
    combData = combData.sort('Date')
    with open('Results\\Combined Schedule.xlsx', 'wb') as h: #completion time, cycle time and delay info in json format
        h.write(combData.xlsx)


def importInput(jInput, excelInput):
    #===========================================================
    # Import workstations and operators schedule from json file
    #===========================================================
    dataJSON = json.loads(jInput)
    

    print 'in import'
    wb = xlrd.open_workbook(file_contents = excelInput)
    
    frozen ={}
    takenPeriods = {}
    
    startSimDate = dateToOrdinal(dataJSON['general']['currentDate'], '%Y/%m/%d %H:%M')
    
    forzenOpsData=tablib.Dataset()
    forzenOpsData.headers = ['Date','Part','Order Name','WP-ID','Personnel','WorkStation','Time In','Time Out','Date Out','Frozen']
    
    schedule = dataJSON['result']['result_list'][0]['component_schedule']
    
    for item in schedule:
        if "Job ID" in item:
            continue
        startDate = dateToOrdinal(item[5], '%Y/%m/%d %H:%M')
        pt = dt.timedelta(hours=item[6])
        dateOut = startDate + pt
        station = item[4]
        ordinalOutDate = excel_date(dateOut.date())
        order = item[1].encode('ascii', 'ignore')
        part = item[0].encode('ascii', 'ignore')
        
        
        #print 'startDate', startDate.date()
        
        if pt.seconds > 0 or pt.days>0:
            forzenOpsData.append([startDate.date(), part, order, item[3], item[7], station, startDate.time(), dateOut.time(), ordinalOutDate, 'X'])
            frozen[item[3]] = 'X'
            
            G.tabSchedule.append([order,part, item[3],station,item[7],startDate,dateOut])
             
            if station not in takenPeriods:
                takenPeriods[station] = {}
            
            takenPeriods[station][startDate] = {'endDate': dateOut, 'taskID':item[3]}
        
    PMschedule = dataJSON['result']['result_list'][0]['operator_gantt']['task_list']
    
    
    for item in PMschedule:
        if 'parent' in item.keys():
            pm = item['parent']
            startDate = dateToOrdinal(item['start_date'], "%d-%m-%Y %H:%M")
            stopDate = dateToOrdinal(item['stop_date'], "%d-%m-%Y %H:%M")
            ordinalOutDate = excel_date(stopDate.date())
            taskID = item['text'].split()[0]
            print pm, taskID
            pt = float((stopDate-startDate).seconds)/3600
            
            if taskID == 'off-shift':
                continue
            
            if pt:
                print pm, taskID
                if pm not in takenPeriods:
                    takenPeriods[pm] = {}
                
                takenPeriods[pm][startDate] = {'endDate': stopDate, 'taskID': taskID}
        
    print 'frozen operations', forzenOpsData
    print 'taken periods', takenPeriods
    
    
    #=================================
    # Import Workplan from Excel file
    #=================================
    
    global numParts
    
    #scenario = 'SIMPLE_2.xlsx'
    WorkPlan = wb.sheet_by_index(0)
    
    Projects = {}
    OrderDates = {}
    DueDates = {}
    Shift = {}
    seqPrjDone = {}
    
    # FIXME: importare data riferimento
    td = dt.datetime(2015,07,23)
    xlreftime = excel_date(td)
    
    for i in range(WorkPlan.nrows):
        i += 1
        if i < WorkPlan.nrows: #for the first line of the project name
            if WorkPlan.cell_value(i,2) != ''  and WorkPlan.cell_value(i,6) != '':
                Projects[WorkPlan.cell_value(i,2)] = {}
                print 'order date',  xlrd.xldate_as_tuple(WorkPlan.cell_value(i,3), wb.datemode)
                oyear, omonth, oday, ohour, ominute, osecond = xlrd.xldate_as_tuple(WorkPlan.cell_value(i,3), wb.datemode)
                if ohour < 8:
                    ohour = 8                    
                OrderDates[WorkPlan.cell_value(i,2)] = dt.datetime(oyear, omonth, oday, ohour, ominute, osecond)   #FIXME: perche cosi?
                DueDates[WorkPlan.cell_value(i,2)] = (xlreftime + WorkPlan.cell_value(i,4))
                header = i
                current = WorkPlan.cell_value(header,2)
                seqPrjDone[current] = {}
            
            #for a part whose name is not in the first line
    
            if str(WorkPlan.cell_value(i,13)).split(';'+' ')[0].upper() == 'ALL':
                prerq = []
                for wpid in range(header,i):
                    prerq.append(str(WorkPlan.cell_value(wpid,14)))
            else:
                prerq = str(WorkPlan.cell_value(i,13)).split(';'+' ')
                
            if len(prerq) == 1 and prerq[0]=='':
                prerq=[]
    
            if WorkPlan.cell_value(i,6) == '':
                continue
            
            Projects[current].setdefault(WorkPlan.cell_value(i,6),[]).append({'id':str(WorkPlan.cell_value(i,14)), 'personnel':str(WorkPlan.cell_value(i,10)),
                                                                              'pt': WorkPlan.cell_value(i,12), 'qty':WorkPlan.cell_value(i,11), 'preReq': prerq, 
                                                                              'operation': str(WorkPlan.cell_value(i,8)), 'sequence':WorkPlan.cell_value(i,9), 
                                                                              'project':current, 'part':WorkPlan.cell_value(i,6)})
            seqPrjDone[current].setdefault(WorkPlan.cell_value(i,6),0)
    
    print 'workplan', Projects            
    print 'sequence', seqPrjDone
    #==================================
    # Import shift data from json file
    #==================================
    
    offShiftTimes = {}
    stRtstOp = {}
    unitTime = 'Hours'
    
    # default shift times are hard coded as there is no correspondence with json file
    # 7:00 - 18:00 are standard shift times
    
    defaultStartShift = 8.0/24
    defaultEndShift = 18.0/24
    stRtstOp['Default'] = [defaultStartShift,defaultEndShift]
    
    shiftData = dataJSON['input']["shift_spreadsheet"]
    for item in shiftData:
        
        if 'Date' in item:
            continue
    
        if item[1] == '' or item[1]== None:
            continue
            
        currDate = excel_date(dateToOrdinal(item[1], "%Y/%m/%d").date())
        cDate = dateToOrdinal(item[1], "%Y/%m/%d").date()
        
        print item[2], item[3]
        if item[2] == '' or item[2]== None:
            shiftStart = defaultStartShift
        else:
            shiftStart = dt.datetime.strptime(item[2],'%H:%M')
        if item[3] == '' or item[3]== None:
            shiftEnd = defaultEndShift
        else:
            shiftEnd = dt.datetime.strptime(item[3],'%H:%M')
        if item[4] == '' or item[4]== None:
            offshiftPeriods = {}
        else:
            offshiftPeriods = offShiftFormat_2(item[4],cDate)
        
        if item[0] != '':#the first line for an operator
            currResc = item[0]
            if currResc not in offShiftTimes:#no previous entry for the operator
                offShiftTimes[currResc] = {}
                offShiftTimes[currResc] = offshiftPeriods
                stRtstOp[currResc] = {}
                stRtstOp[currResc][cDate] = [shiftStart.time(),shiftEnd.time()]
    
            else:
                offShiftTimes[currResc] = offshiftPeriods
    
        else:
            offShiftTimes[currResc][cDate] = offshiftPeriods
            stRtstOp[currResc][cDate] = [shiftStart,shiftEnd]
            
    print 'off shift time', offShiftTimes
        
    offShifts = dict((k,{}) for k in offShiftTimes.keys() + takenPeriods.keys())
    
    for rsce in offShifts.keys():
        if rsce in takenPeriods:
            offShifts[rsce] = takenPeriods[rsce] #directly copy everything from the extracted dict
        if rsce in offShiftTimes:#if that resource is present in the directly specified
            for dte in offShiftTimes[rsce]:
                if dte not in offShifts[rsce]:#if this date was not originally specified
                    offShifts[rsce][dte] = offShiftTimes[rsce][dte]
                else:
                    starts = offShifts[rsce][dte]['Start']
                    stops = offShifts[rsce][dte]['Stop']
                    starts.extend(offShiftTimes[rsce][dte]['Start'])
                    stops.extend(offShiftTimes[rsce][dte]['Stop'])
                    u = list(set(starts))
                    v = list(set(stops))
                    offShifts[rsce][dte]['Start'] = u
                    offShifts[rsce][dte]['Stop'] = v
                    offShifts[rsce][dte]['Start'].sort()
                    offShifts[rsce][dte]['Stop'].sort()
    
    
    print 'stRtstOp', stRtstOp
    
    print 'off shift', offShifts
    
    #==================================================
    # Import machine and pm information from json file
    #==================================================
    
    MachInfo = []
    MachPool = {}
    PMInfo = []
    PMPool = {}
    
    stationTechnologies = {"CAD1": ["ENG", "CAD"],         # XXX CAD1 is considered different than CAD2, they are not equivalent
                "CAD2": ["CAD"],
                "CAM": ["CAM"],
                "MILL": ["MILL"],
                "TURN": ["TURN"],
                "DRILL": ["DRILL"],
                "EDM": ["EDM"],
                "WORK": ["QUAL", "MAN"],        # XXX currently we consider different stations for QUAL/MAN and ASSM
                "ASSM": ["ASSM"],
                "INJM": ["INJM"]}
    
    possMachines = dataJSON['graph']['node']
    
    for mach in possMachines.keys():
        
        if 'machine' in possMachines[mach]['_class'].lower() or 'assembly' in possMachines[mach]['_class'].lower(): 
            
            capacity = 1
            initials = len(mach)
            while initials>0 and mach[:initials] not in stationTechnologies:
                initials -= 1
            
            pool = stationTechnologies[mach[:initials]]
            
            MachInfo.append({'name': mach, 'cap':capacity, 'tech':pool, 'sched':'FIFO'})
            for tec in pool:
                MachPool.setdefault(tec,[]).append(mach) 
    
    print MachInfo
    print 'mach pool', MachPool
    
    PMskills = dataJSON['input']['operator_skills_spreadsheet']
    
    for item in range(1,len(PMskills)):
    
        if PMskills[item][0] == None or PMskills[item][0] == '':
            continue
        
        skills = PMskills[item][1].split(';'+' ')
        if 'INJM-MAN' in skills:
            skills.remove('INJM-MAN')
            skills.append('INJM')
        
        PMInfo.append({'name':PMskills[item][0], 'skills': skills, 'sched':'FIFO', 'status':''})
        for sk in skills:
            PMPool.setdefault(sk,[]).append(PMskills[item][0])
    print PMInfo
    print 'pm pool', PMPool
        
    
    print '======================',offShifts
    
    shiftRes = {} 
    resAvailability = {}
    for item in PMInfo:
        pm = item['name']
        shiftRes[pm] = shiftGenerator(startSimDate,7)
        resAvailability[pm] = deepcopy(shiftRes[pm])
        if pm in offShifts:
            for unavailDate in offShifts[pm].keys():
                print pm, unavailDate, offShifts[pm][unavailDate]['endDate']-unavailDate
                resAvailability[pm] = availableTime_Shift(unavailDate,offShifts[pm][unavailDate]['endDate'],resAvailability[pm])
                
        print 'shift', pm, shiftRes[pm]
        print 'shift', pm, resAvailability[pm]
        
    for item in MachInfo:
        mach = item['name']
        shiftRes[mach] = shiftGenerator(startSimDate,7)
        resAvailability[mach] = deepcopy(shiftRes[mach])
        if mach in offShifts:
            for unavailDate in offShifts[mach].keys():
                print mach, unavailDate, offShifts[mach][unavailDate]['endDate']-unavailDate
                resAvailability[mach] = availableTime_Shift(unavailDate,offShifts[mach][unavailDate]['endDate'],resAvailability[mach])
        print 'shift', mach, shiftRes[mach]
        print 'shift', mach, resAvailability[mach]
    
    # set global variables
    G.resAvailability = deepcopy(resAvailability)
    G.seqPrjDone = deepcopy(seqPrjDone) 
    G.resAvailability = deepcopy(resAvailability)
    G.MachPool = deepcopy(MachPool)
    G.PMPool = deepcopy(PMPool)
    G.Projects = deepcopy(Projects)
    G.xlreftime = td
    G.OrderDates = deepcopy(OrderDates)
    G.completionDate = deepcopy(OrderDates)
