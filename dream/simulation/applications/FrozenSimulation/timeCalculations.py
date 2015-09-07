'''
Created on 6 Aug 2015

@author: Anna
'''

import datetime as dt
from copy import deepcopy


def availableTimeInterval_Manual(manualTime, tStart, availTime):
    
    # suitable for manual operations...returns available time until the end 
    
    sortedTime = sorted(availTime.keys())
    
    i = 0
    while i<len(sortedTime) and sortedTime[i] <= tStart:
        i += 1

    i -= 1
    if i < 0:
        i = 0
        
#    if i == 0 and tStart + manualTime < sortedTime[i]:
#        return None
    
    if availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i]) <= dt.timedelta(seconds=0):
        i += 1

    if i>=len(sortedTime):
        print 'WARNING-not possible'
        return None, 0
    
    return sortedTime[i], availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i])

def availableTimeInterval_MM(manualTime, autoTime, tStart, availTime):
    
    # suitable for MM operations...requires continuous availability over consecutive shifts
    
    sortedTime = sorted(availTime.keys())
    
    i = 0
    while i<len(sortedTime) and sortedTime[i] <= tStart:
        i += 1
    
    i -= 1
    if i < 0:
        i = 0
        
#    if i == 0 and tStart + autoTime + manualTime < sortedTime[i]:
#        return None
    
    tCumulative = dt.timedelta(seconds=0)
    startSorted = sortedTime[i]
    
    while i<len(sortedTime) and (tCumulative + availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i])) < manualTime+autoTime:
        
        if availTime[sortedTime[i]]['endMode'] == 'EOS':
            if i+1 < len(sortedTime) and availTime[sortedTime[i+1]]['preDay'] == sortedTime[i].date() and availTime[sortedTime[i+1]]['startMode'] == 'SOS':
                tCumulative += availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i])
        
        else:
            tCumulative = dt.timedelta(seconds=0)
            if i+1 < len(sortedTime):
                startSorted = sortedTime[i+1]
                
        i += 1
    
    if i>=len(sortedTime):
        return None, 0
    
    return startSorted, manualTime+autoTime-tCumulative + max(tStart,sortedTime[i]) - max(tStart,startSorted)
    



def availableTimeInterval_MA(manualTime, autoTime, tStart, availTime):
    
    sortedTime = sorted(availTime.keys())
    
    print sortedTime
    
    i = 0
    while i<len(sortedTime) and sortedTime[i] <= tStart:
        i += 1
    
    i -= 1
    if i < 0:
        i = 0
        
#    if i == 0 and tStart + autoTime + manualTime < sortedTime[i]:
#        return None
    
    print 'start', sortedTime[i]
    
    while True:

        tCumulative = dt.timedelta(seconds=0)
        startSorted = sortedTime[i]
        
        while i<len(sortedTime) and (tCumulative + availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i])) < manualTime:
            
            if availTime[sortedTime[i]]['endMode'] == 'EOS':
                if i+1 < len(sortedTime) and availTime[sortedTime[i+1]]['preDay'] == sortedTime[i].date() and availTime[sortedTime[i+1]]['startMode'] == 'SOS':
                    tCumulative += availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i])
            
            else:
                tCumulative = dt.timedelta(seconds=0)
                if i+1 < len(sortedTime):
                    startSorted = sortedTime[i+1]
            
            i += 1
        
        if i>=len(sortedTime):
            return None, 0

        tManualEnd = max(tStart, sortedTime[i]) + manualTime - tCumulative


#        while i<len(sortedTime) and availTime[sortedTime[i]]['end'] - max(tStart,sortedTime[i]) < manualTime:
#            i += 1
        
        if i>=len(sortedTime):
            return None
        
#        print 'end manual', sortedTime[i]
        
        if autoTime:
            if availTime[sortedTime[i]]['end']- max(tManualEnd,sortedTime[i]) <= autoTime:
                if  availTime[sortedTime[i]]['endMode'] == 'EOS': 
                    if i==len(sortedTime)-1:
                        break
                    
                    if availTime[sortedTime[i+1]]['startMode']=='SOS' and availTime[sortedTime[i+1]]['preDay'] == sortedTime[i].date() and availTime[sortedTime[i+1]]['end'] - max(tManualEnd,sortedTime[i]) >= autoTime:
                        break
                    else:
                        i += 1
                else:
                    i += 1
            else:
                break
                
        else:
            break
    
    return startSorted, tManualEnd - max(tStart,startSorted)

def updateAvailTime(keyStart, reqTime, tStart, availTime):
    
    # tStart e` tempo effettivo di inizio calcolato in precedenza come max(tStart,keyStart)

    if reqTime <= dt.timedelta(seconds=0):
        return availTime
    
    tempSave = deepcopy(availTime[keyStart])
    
    if keyStart == tStart:
        availTime.pop(keyStart,None)
        
    else:
        
        availTime[keyStart]['end'] = tStart
        availTime[keyStart]['endMode'] = 'IS'

    # case of interval ending before previous end
    if tStart+reqTime < tempSave['end']:
        availTime[tStart+reqTime] = {'end':tempSave['end'], 'startMode':'IS', 'endMode':tempSave['endMode'], 'preDay':tempSave['preDay']}

    # case of interval ending after previous end (i.e. automatic operations)...check if goes into following available interval    
    elif tStart+reqTime > tempSave['end']:
        sortedTime = sorted(availTime.keys())
        i=0
        while i<len(sortedTime) and sortedTime[i]<=keyStart:
            i+=1
        
#        if modeSim == 'avail':
#            i -= 1
        
        if i >= len(sortedTime):
            print 'WARNING: beyond planning horizon'
            return availTime
        
#        print 'find next time', sortedTime[i], i
        if tStart+reqTime > sortedTime[i]:
            # repeat procedure                
            availTime = updateAvailTime(sortedTime[i], reqTime - (sortedTime[i]-tStart), sortedTime[i], availTime)
                
    return availTime
                
    
def availableTime_Shift(tStart, tEnd, availTime):
    
    sortedTime = sorted(availTime.keys())
    
    i = 0
    while i<len(sortedTime) and availTime[sortedTime[i]]['end'] <= tStart:
        i += 1
    
    
#    print i, sortedTime[i], availTime[sortedTime[i]]['end'], tStart, tEnd

    if i>=len(sortedTime):
        print 'WARNING: time interval not found'
        return availTime
    
    if availTime[sortedTime[i]]['end'] >= tEnd:
        availTime = updateAvailTime(sortedTime[i], tEnd - max(tStart,sortedTime[i]), max(tStart,sortedTime[i]), availTime)
        
    
    else:     
        
        if  availTime[sortedTime[i]]['endMode'] == 'EOS': 
            if i==len(sortedTime)-1:
                print 'WARNING: beyond last interval'
                availTime= updateAvailTime(sortedTime[i], tEnd - max(tStart,sortedTime[i]), max(tStart,sortedTime[i]), availTime)
                    
            elif availTime[sortedTime[i+1]]['preDay'] == sortedTime[i].date() and sortedTime[i+1] >= tEnd:
                availTime = updateAvailTime(sortedTime[i], tEnd - max(tStart,sortedTime[i]), max(tStart,sortedTime[i]), availTime)
            
            elif availTime[sortedTime[i+1]]['startMode']=='SOS' and availTime[sortedTime[i+1]]['preDay'] == sortedTime[i].date() and availTime[sortedTime[i+1]]['end'] >= tEnd:
                print 'beyond eos', max(tStart,sortedTime[i]), tEnd - max(tStart,sortedTime[i])
                availTime = updateAvailTime(sortedTime[i], tEnd - max(tStart,sortedTime[i]), max(tStart,sortedTime[i]), availTime)
            else:
                return availTime
        
        else:
            return availTime
    
    return availTime

