'''
Created on 20 Aug 2015

@author: Anna
'''

from jsonReader import importInput
from findSequence import findSequence
from timeCalculations import availableTimeInterval_MA, updateAvailTime, availableTimeInterval_MM, availableTimeInterval_Manual
from operator import itemgetter
from copy import deepcopy
from Globals import G
import datetime as dt


def manual_allocation(currentOp):
        
    tStart = currentOp['minStartTime']  # earliest start date for current operation    
    remPT = dt.timedelta(hours=currentOp['manualTime']) 
    
    print 'in manual allocation', currentOp['id']
    print 'tStart manual', tStart, remPT
    while remPT > dt.timedelta(seconds=0):
        
        startTimeMach = []  # collects earliest keyDate for machines
        startTimeOp = []  # collects earliest keyDate for operators
        
        # find machines available time intervals
        for mach in G.MachPool[currentOp['operation']]:
            res = availableTimeInterval_Manual(remPT, tStart, G.resAvailability[mach])
            startTimeMach.append({'mach':mach, 'start':res[0], 'avPT':res[1]*(-1)})

        # sort available time
        sorted_startTimeMach = sorted(startTimeMach, key=itemgetter('start', 'avPT'))
        tStart = max(sorted_startTimeMach[0]['start'],tStart)

        # verify whether PM are available in the same time
        for pm in G.PMPool[currentOp['operation']]:
            res = availableTimeInterval_Manual(remPT, tStart, G.resAvailability[pm])
            startTimeOp.append({'pm':pm, 'start':res[0], 'avPT':res[1]*(-1)}) 

        # sort available time
        sorted_startTimeOp = sorted(startTimeOp, key=itemgetter('start', 'avPT'))
        
        print tStart
        print 'sort mach', sorted_startTimeMach
        print 'sort pm', sorted_startTimeOp
        
        # calculate available PT
        if sorted_startTimeOp[0]['start'] <= tStart:
            print 'first op'
            availablePT = min(sorted_startTimeMach[0]['avPT']*(-1), sorted_startTimeOp[0]['avPT']*(-1), remPT) 
        
        elif sorted_startTimeOp[0]['start'] < tStart + sorted_startTimeMach[0]['avPT']:
            print 'sec op'
            tEnd = min(tStart+sorted_startTimeMach[0]['avPT'], sorted_startTimeOp[0]['start']+sorted_startTimeOp[0]['avPT'])
            tStart = sorted_startTimeOp[0]['start']
            availablePT = min(tEnd - tStart, remPT)
        
        else:
            print '3 op'
            availablePT = dt.timedelta(seconds=0)
            tStart = sorted_startTimeOp[0]['start']
        
        # update remaining PT
        remPT -= availablePT
        print 'fine all', tStart, availablePT, remPT
        
        
        if availablePT > dt.timedelta(seconds=0):
            # update machine and operator availability
            G.resAvailability[sorted_startTimeMach[0]['mach']] = updateAvailTime(sorted_startTimeMach[0]['start'], availablePT, tStart, 
                                                                                 G.resAvailability[sorted_startTimeMach[0]['mach']])
            
            G.resAvailability[sorted_startTimeOp[0]['pm']] = updateAvailTime(sorted_startTimeOp[0]['start'], availablePT, tStart, 
                                                                             G.resAvailability[sorted_startTimeOp[0]['pm']])
            # aggiorna schedule   
            if currentOp['id'] not in G.Schedule.keys():                        
                G.Schedule[currentOp['id']]={} 
                G.Schedule[currentOp['id']]['startDate'] = tStart
            tEnd = tStart + availablePT
            G.Schedule[currentOp['id']]['endDate'] = tEnd
            G.Schedule[currentOp['id']].setdefault('rList',{})[(tStart,tEnd)] = {'mach':sorted_startTimeMach[0]['mach'],'operator':sorted_startTimeOp[0]['pm']}
            G.tabSchedule.append([currentOp['project'], currentOp['part'], currentOp['id'],sorted_startTimeMach[0]['mach'],sorted_startTimeOp[0]['pm'],tStart,tEnd])
            if currentOp['preID'] != None:
                G.Schedule[currentOp['preID']] = G.Schedule[currentOp['id']]
            if G.completionDate[currentOp['project']] < tEnd:
                G.completionDate[currentOp['project']] = tEnd
            tStart = tEnd
    
    print currentOp['id'], G.Schedule[currentOp['id']]
            
            
def MAM_allocation(currentOp):
    
    tStart = currentOp['minStartTime']  # earliest start date for current operation    
    
    print 'tStart', tStart   
    remPT = currentOp['manualTime'] + currentOp['autoTime']
    
    while remPT:
        
        startTimeMach = []  # collects earliest keyDate for machines
        startTimeOp = []  # collects earliest keyDate for operators
        
        # find machines available time intervals
        for mach in G.MachPool[currentOp['operation']]:
            
            # find available time (availableTimeInterval_MA)
            print 'man', currentOp['manualTime']
            mTime = dt.timedelta(hours=currentOp['manualTime'])
            aTime = dt.timedelta(hours=currentOp['autoTime']) 
            print 'mach av', mach, G.resAvailability[mach]
            if currentOp['mode'] == 'MM':
                res = availableTimeInterval_MM(mTime, aTime, tStart, G.resAvailability[mach])
                startTimeMach.append({'mach':mach, 'start':res[0], 'eqPT':res[1]})
            else:
                res = availableTimeInterval_MA(mTime, aTime, tStart, G.resAvailability[mach])
                #startTimeMach.append({'mach':mach, 'start':res, 'eqPT':mTime+aTime})
                startTimeMach.append({'mach':mach, 'start':res[0], 'eqPT':res[1]+aTime})
            print 'start time mach', startTimeMach
            
        # sort available time
        sorted_startTimeMach = sorted(startTimeMach, key=itemgetter('start', 'eqPT'))
        tStart = max(sorted_startTimeMach[0]['start'],tStart)
        
        print 'mach tent', sorted_startTimeMach[0]['mach'], tStart
        
        # verify whether PM are available in the same time
        for pm in G.PMPool[currentOp['operation']]:
            
            print 'operator', pm
            #find available time
            if currentOp['mode'] == 'MM':
                res = availableTimeInterval_MM(mTime, aTime, tStart, G.resAvailability[pm])
                startTimeOp.append({'pm':pm, 'start':res[0], 'eqPT':res[1]}) 
            else:
                res = availableTimeInterval_MA(mTime, dt.timedelta(hours=0), tStart, G.resAvailability[pm])
#                startTimeOp.append({'pm':pm, 'start':res[0], 'eqPT':mTime}) 
                startTimeOp.append({'pm':pm, 'start':res[0], 'eqPT':res[1]}) 
                
        # sort available time
        sorted_startTimeOp = sorted(startTimeOp, key=itemgetter('start', 'eqPT'))
        
        if sorted_startTimeOp[0]['start'] <= tStart:
            remPT = 0
        else:
            tStart = sorted_startTimeOp[0]['start']
                
    
    print 'machine chosen', sorted_startTimeMach[0]['mach']
    print 'operator chosen', sorted_startTimeOp[0]['pm'], sorted_startTimeOp
    print G.resAvailability[sorted_startTimeMach[0]['mach']]
    print G.resAvailability[sorted_startTimeOp[0]['pm']]
    
    # update machine availability
    G.resAvailability[sorted_startTimeMach[0]['mach']] = updateAvailTime(sorted_startTimeMach[0]['start'], sorted_startTimeMach[0]['eqPT'], tStart, 
                                G.resAvailability[sorted_startTimeMach[0]['mach']])
    
    # update operator availability
    G.resAvailability[sorted_startTimeOp[0]['pm']] = updateAvailTime(sorted_startTimeOp[0]['start'], sorted_startTimeOp[0]['eqPT'], tStart, 
                                G.resAvailability[sorted_startTimeOp[0]['pm']])
    
    # aggiorna schedule   
    G.Schedule.setdefault(currentOp['id'],{}) 
    G.Schedule[currentOp['id']]['startDate'] = tStart
    tEnd = tStart + sorted_startTimeMach[0]['eqPT']
    G.Schedule[currentOp['id']]['endDate'] = tEnd
    G.Schedule[currentOp['id']].setdefault('rList',{})[(tStart,tEnd)] = {'mach':sorted_startTimeMach[0]['mach'],'operator':sorted_startTimeOp[0]['pm']}
    if currentOp['preID'] != None:
        G.Schedule[currentOp['preID']] = G.Schedule[currentOp['id']]
    if G.completionDate[currentOp['project']] < tEnd:
        G.completionDate[currentOp['project']] = tEnd
    G.tabSchedule.append([currentOp['project'], currentOp['part'], currentOp['preID'],sorted_startTimeMach[0]['mach'],sorted_startTimeOp[0]['pm'],tStart,tEnd-aTime])
    G.tabSchedule.append([currentOp['project'], currentOp['part'], currentOp['id'],sorted_startTimeMach[0]['mach'],'automatic',tEnd-aTime,tEnd])
        
    print 'schedule', G.Schedule
    
    print G.resAvailability[sorted_startTimeOp[0]['pm']]


def exeSim(jsonInput, workplanInput, algorithmAttributes):
    
    mime_type, attachement_data = jsonInput[len('data:'):].split(';base64,', 1)
    attachement_data = attachement_data.decode('base64')
    jInput = attachement_data
    
    mime_type, attachement_data = workplanInput[len('data:'):].split(';base64,', 1)
    attachement_data = attachement_data.decode('base64')
    excelInput = attachement_data
    
    # read input data
    importInput(jInput, excelInput, algorithmAttributes)
    
    # find initial operation
    opDone = []
    seq = deepcopy(G.seqPrjDone)    
    proj = deepcopy(G.Projects)
    opReady = findSequence(proj, seq, opDone)
    
    print 'opready', opReady, G.seqPrjDone
    
    while len(opReady):
        
        # set current operation
        currentOp = opReady[0]
        print 'chosen operation', currentOp['id']
        
        # check op mode
        if currentOp['mode'] == 'MA' or currentOp['mode'] == 'MM':     
            MAM_allocation(currentOp)
        
        else:
            manual_allocation(currentOp)
#        elif currentOp['mode'] == 'MM':
#            print 'MM'
#            MM_allocation(currentOp)
            
        # save results
        opDone.append(currentOp['id'])
        G.seqPrjDone[currentOp['project']][currentOp['part']] += 1
        print 'op', currentOp
        if currentOp['preID'] != None:
            opDone.append(currentOp['preID'])
            G.seqPrjDone[currentOp['project']][currentOp['part']] += 1
        
        # aggiorna seqPrjDone
        
        
        seq = deepcopy(G.seqPrjDone)
        proj = deepcopy(G.Projects)
        opReady = findSequence(proj, seq, opDone)
        print opDone
    
    print 'completion date', G.completionDate
    
    G.reportResults.add_sheet(G.tabSchedule)
    with open('schedule.xlsx', 'wb') as f: #time level schedule info
        f.write(G.reportResults.xlsx)


if __name__ == '__main__':
    exeSim()                