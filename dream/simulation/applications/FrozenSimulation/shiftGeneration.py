'''
Created on 6 Aug 2015

@author: Anna
'''

import datetime as dt
from copy import deepcopy

def shiftGenerator(startDate, noDays):
    
    shift = {}
    day = 0
    actualDays = 0
    preDay = deepcopy(startDate.date())
    while actualDays < noDays:
        st = deepcopy(startDate)
        
        if day: 
            dateStart = st.date()
            dateStart += dt.timedelta(days=day) 
            st = dt.datetime(dateStart.year,dateStart.month, dateStart.day, 8,0)
            
        if st.weekday() < 5:
            fin = dt.datetime(st.year, st.month, st.day, 18,0)
            shift[st] = {'end':fin, 'startMode':'SOS', 'endMode':'EOS', 'preDay':preDay}
            preDay = st.date()
            actualDays += 1
        day += 1
    return shift
        
if __name__ == '__main__':
    shift = shiftGenerator(dt.datetime(2015,8,4,12,00),10)
        
