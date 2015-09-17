'''
Created on 7 Aug 2015

@author: Anna
'''

import json
import tablib
import datetime as dt
import xlrd
from operator import itemgetter
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


def importInput(jInput, excelInput, algorithmAttributes):
    #===========================================================
    # Import workstations and operators schedule from json file
    #===========================================================
    dataJSON = json.loads(jInput)
    wb = xlrd.open_workbook(file_contents = excelInput)
    
    frozen ={}
    takenPeriods = {}
    
    startSimDate = dateToOrdinal(dataJSON['general']['currentDate'], '%Y/%m/%d %H:%M')
    startUserDate = dateToOrdinal(algorithmAttributes.get('currentDate',startSimDate), '%Y/%m/%d %H:%M')
    
    forzenOpsData=tablib.Dataset()
    forzenOpsData.headers = ['Date','Part','Order Name','WP-ID','Personnel','WorkStation','Time In','Time Out','Date Out','Frozen']
    
    selSol = 0
    if 'reference_solution' in dataJSON['input']:
        try:
          selSol = int(dataJSON['input']['reference_solution'])
        except:
          selSol = 0
          
    schedule = dataJSON['result']['result_list'][selSol]['component_schedule']
    
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
        
        
        if pt.seconds > 0 or pt.days>0:
            forzenOpsData.append([startDate.date(), part, order, item[3], item[7], station, startDate.time(), dateOut.time(), ordinalOutDate, 'X'])
            frozen[item[3]] = 'X'
            
            G.tabScheduleOrig.append([order,part, item[3],station,item[7],startDate,dateOut])
             
            takenPeriods.setdefault(station,{})[startDate] = {'endDate': dateOut, 'taskID':item[3]}
    
    # import PM schedule
    PMschedule = dataJSON['result']['result_list'][selSol]['operator_gantt']['task_list']
    
    # extract resource availability
    for item in PMschedule:
        if 'parent' in item.keys():
            pm = item['parent']
            startDate = dateToOrdinal(item['start_date'], "%d-%m-%Y %H:%M")
            stopDate = dateToOrdinal(item['stop_date'], "%d-%m-%Y %H:%M")
            ordinalOutDate = excel_date(stopDate.date())
            taskID = item['text'].split()[0]
            pt = float((stopDate-startDate).seconds)/3600
            
            if taskID == 'off-shift':
                continue
            
            if pt:
                if pm not in takenPeriods:
                    takenPeriods[pm] = {}
                
                takenPeriods[pm][startDate] = {'endDate': stopDate, 'taskID': taskID}
                G.pmScheduleOrig.append([pm,startDate,stopDate,taskID])
        

    #=================================
    # Import Workplan from Excel file
    #=================================
    
    WorkPlan = wb.sheet_by_index(0)
    
    Projects = {}
    OrderDates = {}
    seqPrjDone = {}
    
    
    for i in range(WorkPlan.nrows):
        i += 1
        if i < WorkPlan.nrows: #for the first line of the project name
            if WorkPlan.cell_value(i,0) != ''  and WorkPlan.cell_value(i,2) != '':
                Projects[WorkPlan.cell_value(i,0)] = {}
                oyear, omonth, oday, ohour, ominute, osecond = xlrd.xldate_as_tuple(WorkPlan.cell_value(i,1), wb.datemode)
                if ohour < 8:
                    ohour = 8                    
                OrderDates[WorkPlan.cell_value(i,0)] = dt.datetime(oyear, omonth, oday, ohour, ominute, osecond)   
                header = i
                current = WorkPlan.cell_value(header,0)
                seqPrjDone[current] = {}
            
            #for a part whose name is not in the first line
    
            if str(WorkPlan.cell_value(i,6)).split(';'+' ')[0].upper() == 'ALL':
                prerq = []
                for wpid in range(header,i):
                    prerq.append(str(WorkPlan.cell_value(wpid,7)))
            else:
                prerq = str(WorkPlan.cell_value(i,6)).split(';'+' ')
                
            if len(prerq) == 1 and prerq[0]=='':
                prerq=[]
    
            if WorkPlan.cell_value(i,2) == '':
                continue
            
            Projects[current].setdefault(WorkPlan.cell_value(i,2),[]).append({'id':str(WorkPlan.cell_value(i,7)), 
                                                                              'pt': WorkPlan.cell_value(i,5), 'qty':WorkPlan.cell_value(i,4), 'preReq': prerq, 
                                                                              'operation': str(WorkPlan.cell_value(i,3)), 
                                                                              'project':current, 'part':WorkPlan.cell_value(i,2)}) #'personnel':str(WorkPlan.cell_value(i,10)), 'sequence':WorkPlan.cell_value(i,9), 
            seqPrjDone[current].setdefault(WorkPlan.cell_value(i,2),0)
    
    maxODate = min(OrderDates.iteritems(), key=itemgetter(1))[1]
    
    #==================================
    # Import shift data from json file
    #==================================
    
    offShiftTimes = {}
    stRtstOp = {}
    
    # default shift times are hard coded as there is no correspondence with json file
    # 8:00 - 18:00 are standard shift times
    
    defaultStartShift = dt.datetime(year=2014,month=1,day=1,hour=8,minute=0)
    defaultEndShift = dt.datetime(year=2014,month=1,day=1,hour=18,minute=0)
    stRtstOp['Default'] = [defaultStartShift,defaultEndShift]
    
    shiftData = dataJSON['input']["shift_spreadsheet"]
    for item in shiftData:
        
        if 'Date' in item:
            continue
    
        if item[1] == '' or item[1]== None:
            continue
            
        if item[0] != '':#the first line for an operator
            currResc = item[0]
            
        cDate = dateToOrdinal(item[1], "%Y/%m/%d").date()
        
        # set shift exceptions
        if item[2] == '' or item[2]== None:
            shiftStart = defaultStartShift
        else:
            shiftStart = dt.datetime.strptime(item[2],'%H:%M')
        if item[3] == '' or item[3]== None:
            shiftEnd = defaultEndShift
        else:
            shiftEnd = dt.datetime.strptime(item[3],'%H:%M')
        
        # read off-shift periods   
        if item[4] == '' or item[4]== None:
            offshiftPeriods = {}
        else:
            offshiftPeriods = offShiftFormat_2(item[4],cDate)
        

        offShiftTimes.setdefault(currResc,{})
        for offS in offshiftPeriods.keys():
            offShiftTimes[currResc][offS] = offshiftPeriods[offS]
        stRtstOp.setdefault(currResc,{})[cDate] = [shiftStart.time(),shiftEnd.time()]

                
    #==================================================
    # Import machine and pm information from json file
    #==================================================
    
    MachInfo = []
    MachPool = {}
    PMInfo = []
    PMPool = {}
    
    # static information on applicable technologies
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
    
    # import machines information
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
    
    # import PM information
    PMskills = dataJSON['input']['operator_skills_spreadsheet']
    
    for item in range(1,len(PMskills)):
    
        if PMskills[item][0] == None or PMskills[item][0] == '':
            continue
        
        skills = PMskills[item][1].split(';'+' ')
        if 'INJM-MAN' in skills:
            skills.remove('INJM-MAN')
            skills.append('INJM')
        if 'INJM-SET' in skills:
            skills.remove('INJM-SET')
            skills.append('INJM')
        if 'EDM-SET' in skills:
            skills.remove('EDM-SET')
            skills.append('EDM')
        if 'MILL-SET' in skills:
            skills.remove('MILL-SET')
            skills.append('MILL')
        
        PMInfo.append({'name':PMskills[item][0], 'skills': skills, 'sched':'FIFO', 'status':''})
        for sk in skills:
            PMPool.setdefault(sk,[]).append(PMskills[item][0])
    
    # set start simulation date as maximum betweeen the current date (json) and the order date 
    G.xlreftime = max(maxODate,startUserDate)    #startSimDate,
    shiftRes = {} 
    resAvailability = {}

    # define shifts for PMs 
    for item in PMInfo:
        pm = item['name']
        if pm in stRtstOp:
            exceptions = stRtstOp[pm]
        else:
            exceptions = {}            
        shiftRes[pm] = shiftGenerator(G.xlreftime,30,exceptions)
        resAvailability[pm] = deepcopy(shiftRes[pm])
        if pm in offShiftTimes:
            for unavailDate in offShiftTimes[pm].keys():
                resAvailability[pm] = availableTime_Shift(unavailDate,offShiftTimes[pm][unavailDate]['endDate'],resAvailability[pm])
        if pm in takenPeriods:
            for unavailDate in takenPeriods[pm].keys():
                resAvailability[pm] = availableTime_Shift(unavailDate,takenPeriods[pm][unavailDate]['endDate'],resAvailability[pm])
                

    # define shifts for machines
    for item in MachInfo:
        mach = item['name']
        if mach in stRtstOp:
            exceptions = stRtstOp[mach]
        else:
            exceptions = {}            
        shiftRes[mach] = shiftGenerator(G.xlreftime,30,exceptions)
        resAvailability[mach] = deepcopy(shiftRes[mach])
        if mach in offShiftTimes:
            for unavailDate in offShiftTimes[mach].keys():
                resAvailability[mach] = availableTime_Shift(unavailDate,offShiftTimes[mach][unavailDate]['endDate'],resAvailability[mach])
        if mach in takenPeriods:
            for unavailDate in takenPeriods[mach].keys():
                resAvailability[mach] = availableTime_Shift(unavailDate,takenPeriods[mach][unavailDate]['endDate'],resAvailability[mach])
    
    # set global variables
    G.seqPrjDoneOrig = deepcopy(seqPrjDone) 
    G.resAvailabilityOrig = deepcopy(resAvailability)
    G.MachPool = deepcopy(MachPool)
    print 'mach pool',G.MachPool
    G.PMPool = deepcopy(PMPool)
    G.Projects = deepcopy(Projects)
    G.OrderDates = deepcopy(OrderDates)


def initGlobals():
    G.resAvailability = deepcopy(G.resAvailabilityOrig)
    G.seqPrjDone = deepcopy(G.seqPrjDoneOrig)
    G.Schedule[G.simMode] = {}
    G.completionDate[G.simMode] = deepcopy(G.OrderDates)
 
    G.tabSchedule[G.simMode] = tablib.Dataset(title='Schedule'+str(G.simMode))
    G.tabSchedule[G.simMode].headers = (['Project', 'Part', 'Task ID', 'Station', 'Operator', 'Start Time', 'End Time'])
    for item in G.tabScheduleOrig:
        G.tabSchedule[G.simMode].append(item)
    G.pmSchedule[G.simMode] = tablib.Dataset(title='PMschedule'+str(G.simMode))
    for item in G.pmScheduleOrig:
        G.pmSchedule[G.simMode].append(item)
