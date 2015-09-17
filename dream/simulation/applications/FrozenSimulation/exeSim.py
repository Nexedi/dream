'''
Created on 20 Aug 2015

@author: Anna
'''

from jsonReader import importInput, initGlobals
from findSequence import findSequence
from timeCalculations import availableTimeInterval_MA, updateAvailTime, availableTimeInterval_MM, availableTimeInterval_Manual
from operator import itemgetter
from copy import deepcopy
from Globals import G
import datetime as dt


def manual_allocation(currentOp):
        
    tStart = currentOp['minStartTime']  # earliest start date for current operation    
    remPT = dt.timedelta(hours=currentOp['manualTime']) 
    
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
        
        # calculate available PT
        if sorted_startTimeOp[0]['start'] <= tStart:
#            print 'first op'
            availablePT = min(sorted_startTimeMach[0]['avPT']*(-1), sorted_startTimeOp[0]['avPT']*(-1), remPT) 
        
        elif sorted_startTimeOp[0]['start'] < tStart + sorted_startTimeMach[0]['avPT']:
#            print 'sec op'
            tEnd = min(tStart+sorted_startTimeMach[0]['avPT'], sorted_startTimeOp[0]['start']+sorted_startTimeOp[0]['avPT'])
            tStart = sorted_startTimeOp[0]['start']
            availablePT = min(tEnd - tStart, remPT)
        
        else:
#            print '3 op'
            availablePT = dt.timedelta(seconds=0)
            tStart = sorted_startTimeOp[0]['start']
        
        # update remaining PT
        remPT -= availablePT

        
        if availablePT > dt.timedelta(seconds=0):
            # update machine and operator availability
            G.resAvailability[sorted_startTimeMach[0]['mach']] = updateAvailTime(sorted_startTimeMach[0]['start'], availablePT, tStart, 
                                                                                 G.resAvailability[sorted_startTimeMach[0]['mach']])
            
            G.resAvailability[sorted_startTimeOp[0]['pm']] = updateAvailTime(sorted_startTimeOp[0]['start'], availablePT, tStart, 
                                                                             G.resAvailability[sorted_startTimeOp[0]['pm']])
            # update schedule   
            if currentOp['id'] not in G.Schedule[G.simMode].keys():                        
                G.Schedule[G.simMode][currentOp['id']]={} 
                G.Schedule[G.simMode][currentOp['id']]['startDate'] = tStart
            tEnd = tStart + availablePT
            G.Schedule[G.simMode][currentOp['id']]['endDate'] = tEnd
            G.Schedule[G.simMode][currentOp['id']].setdefault('rList',{})[(tStart,tEnd)] = {'mach':sorted_startTimeMach[0]['mach'],'operator':sorted_startTimeOp[0]['pm']}
            G.tabSchedule[G.simMode].append([currentOp['project'], currentOp['part'], currentOp['id'],sorted_startTimeMach[0]['mach'],sorted_startTimeOp[0]['pm'],tStart,tEnd])
            G.pmSchedule[G.simMode].append([sorted_startTimeOp[0]['pm'],tStart,tEnd,currentOp['id']])
            if currentOp['preID'] != None:
                G.Schedule[G.simMode][currentOp['preID']] = G.Schedule[G.simMode][currentOp['id']]
            if G.completionDate[G.simMode][currentOp['project']] < tEnd:
                G.completionDate[G.simMode][currentOp['project']] = tEnd
            tStart = tEnd
            
            
def MAM_allocation(currentOp):
    
    # set earliest start date for current operation
    tStart = currentOp['minStartTime']  # earliest start date for current operation    
    
    # set processing time
    remPT = currentOp['manualTime'] + currentOp['autoTime']
    
    while remPT:
        
        startTimeMach = []  # collects earliest keyDate for machines
        startTimeOp = []  # collects earliest keyDate for operators
        
        # find machines available time intervals
        for mach in G.MachPool[currentOp['operation']]:
            
            # find available time (availableTimeInterval_MA)
            mTime = dt.timedelta(hours=currentOp['manualTime'])
            aTime = dt.timedelta(hours=currentOp['autoTime']) 
            if currentOp['mode'] == 'MM' or currentOp['mode'] == 'M':
                res = availableTimeInterval_MM(mTime, aTime, tStart, G.resAvailability[mach])
                startTimeMach.append({'mach':mach, 'start':res[0], 'eqPT':res[1]})
            else:
                res = availableTimeInterval_MA(mTime, aTime, tStart, G.resAvailability[mach])
                #startTimeMach.append({'mach':mach, 'start':res, 'eqPT':mTime+aTime})
                startTimeMach.append({'mach':mach, 'start':res[0], 'eqPT':res[1]+aTime})

        # sort available time
        sorted_startTimeMach = sorted(startTimeMach, key=itemgetter('start', 'eqPT'))
        tStart = max(sorted_startTimeMach[0]['start'],tStart)
        
        # verify whether PM are available during the same time interval
        for pm in G.PMPool[currentOp['operation']]:
            
            #find available time
            if currentOp['mode'] == 'MM' or currentOp['mode'] == 'M':
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
                
    
    # update machine availability
    G.resAvailability[sorted_startTimeMach[0]['mach']] = updateAvailTime(sorted_startTimeMach[0]['start'], sorted_startTimeMach[0]['eqPT'], tStart, 
                                G.resAvailability[sorted_startTimeMach[0]['mach']])
    
    # update operator availability
    G.resAvailability[sorted_startTimeOp[0]['pm']] = updateAvailTime(sorted_startTimeOp[0]['start'], sorted_startTimeOp[0]['eqPT'], tStart, 
                                G.resAvailability[sorted_startTimeOp[0]['pm']])
    
    # update schedule   
    G.Schedule[G.simMode].setdefault(currentOp['id'],{}) 
    G.Schedule[G.simMode][currentOp['id']]['startDate'] = tStart
    tEnd = tStart + sorted_startTimeMach[0]['eqPT']
    G.Schedule[G.simMode][currentOp['id']]['endDate'] = tEnd
    G.Schedule[G.simMode][currentOp['id']].setdefault('rList',{})[(tStart,tEnd)] = {'mach':sorted_startTimeMach[0]['mach'],'operator':sorted_startTimeOp[0]['pm']}
    if currentOp['preID'] != None:
        G.Schedule[G.simMode][currentOp['preID']] = G.Schedule[G.simMode][currentOp['id']]
    if G.completionDate[G.simMode][currentOp['project']] < tEnd:
        G.completionDate[G.simMode][currentOp['project']] = tEnd
    if currentOp['mode'] == 'MM' or currentOp['mode'] == 'MA':
        G.tabSchedule[G.simMode].append([currentOp['project'], currentOp['part'], currentOp['preID'],sorted_startTimeMach[0]['mach'],sorted_startTimeOp[0]['pm'],tStart,tEnd-aTime])
        G.tabSchedule[G.simMode].append([currentOp['project'], currentOp['part'], currentOp['id'],sorted_startTimeMach[0]['mach'],'automatic',tEnd-aTime,tEnd])
        G.pmSchedule[G.simMode].append([sorted_startTimeOp[0]['pm'],tStart,tEnd-aTime,currentOp['id']])
    else:
        G.tabSchedule[G.simMode].append([currentOp['project'], currentOp['part'], currentOp['id'],sorted_startTimeMach[0]['mach'],sorted_startTimeOp[0]['pm'],tStart,tEnd])
        G.pmSchedule[G.simMode].append([sorted_startTimeOp[0]['pm'],tStart,tEnd,currentOp['id']])


def exeSim(jsonInput, workplanInput, algorithmAttributes):
    
    mime_type, attachement_data = jsonInput[len('data:'):].split(';base64,', 1)
    attachement_data = attachement_data.decode('base64')
    jInput = attachement_data
    
    mime_type, attachement_data = workplanInput[len('data:'):].split(';base64,', 1)
    attachement_data = attachement_data.decode('base64')
    excelInput = attachement_data
    
    # read input data
    G.simMode = 'Earliest'
    importInput(jInput, excelInput, algorithmAttributes)
    
    #==========================
    # Earliest Completion Date
    #==========================
    
    initGlobals()    
    
    # find initial operation
    opDone = []
    seq = deepcopy(G.seqPrjDone)    
    proj = deepcopy(G.Projects)
    opReady = findSequence(proj, seq, opDone)
    
    while len(opReady):
        
        # set current operation
        currentOp = opReady[0]

        # check op mode and allocate operation
        if currentOp['mode'] == 'MA' or currentOp['mode'] == 'MM':     
            MAM_allocation(currentOp)
        
        else:
            manual_allocation(currentOp)
            
        # save results and update sequence number
        opDone.append(currentOp['id'])
        G.seqPrjDone[currentOp['project']][currentOp['part']] += 1
        if currentOp['preID'] != None:
            opDone.append(currentOp['preID'])
            G.seqPrjDone[currentOp['project']][currentOp['part']] += 1
        
        # find next operation
        seq = deepcopy(G.seqPrjDone)
        proj = deepcopy(G.Projects)
        opReady = findSequence(proj, seq, opDone)

    # add result sheets
    G.reportResults.add_sheet(G.tabSchedule[G.simMode])
    G.reportResults.add_sheet(G.pmSchedule[G.simMode])

    #==========================
    # Latest Completion Date
    #==========================
    
    G.simMode = 'Latest'
    initGlobals()    
    
    # find initial operation
    opDone = []
    seq = deepcopy(G.seqPrjDone)    
    proj = deepcopy(G.Projects)
    opReady = findSequence(proj, seq, opDone)
    
    while len(opReady):
        
        # set current operation
        currentOp = opReady[0]

        # allocate operation
        MAM_allocation(currentOp)
        
        # save results
        opDone.append(currentOp['id'])
        G.seqPrjDone[currentOp['project']][currentOp['part']] += 1
        if currentOp['preID'] != None:
            opDone.append(currentOp['preID'])
            G.seqPrjDone[currentOp['project']][currentOp['part']] += 1
        
        # find following operation
        seq = deepcopy(G.seqPrjDone)
        proj = deepcopy(G.Projects)
        opReady = findSequence(proj, seq, opDone)

    # report results
    G.reportResults.add_sheet(G.tabSchedule[G.simMode])
    G.reportResults.add_sheet(G.pmSchedule[G.simMode])
    
#    with open('schedule.xlsx', 'wb') as f: #time level schedule info
#        f.write(G.reportResults.xlsx)


if __name__ == '__main__':
    exeSim()                