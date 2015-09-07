'''
Created on 6 Aug 2015

@author: Anna
'''

import datetime as dt
from copy import deepcopy

def shiftGenerator(startDate, noDays, exceptions):
    
    shift = {}
    day = 0
    actualDays = 0
    preDay = deepcopy(startDate.date())
    while actualDays < noDays:
        
        st = deepcopy(startDate)        
        dateStart = st.date()
        dateStart += dt.timedelta(days=day) 
        
        if dateStart in exceptions:
            st = dt.datetime(dateStart.year,dateStart.month, dateStart.day, exceptions[dateStart][0].hour, exceptions[dateStart][0].minute)
            fin = dt.datetime(st.year, st.month, st.day, exceptions[st.date()][1].hour, exceptions[st.date()][1].minute)
        else: 
            st = dt.datetime(dateStart.year,dateStart.month, dateStart.day, 8,0)
            fin = dt.datetime(st.year, st.month, st.day, 18,0)
            
        if st.weekday() < 5 or st.date() in exceptions:
            shift[st] = {'end':fin, 'startMode':'SOS', 'endMode':'EOS', 'preDay':preDay}
            preDay = st.date()
            actualDays += 1
            
        day += 1
    return shift
