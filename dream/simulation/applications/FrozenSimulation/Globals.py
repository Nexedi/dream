'''
Created on 31 Aug 2015

@author: Anna
'''

import tablib

class G:
    
    Schedule={}
    seqPrjDone = None
    resAvailability = None
    MachPool = None
    PMPool = None
    Projects = None
    xlreftime = None
    reportResults = tablib.Databook()
    tabSchedule = tablib.Dataset(title='Schedule')
    tabSchedule.headers = (['Project', 'Part', 'Task ID', 'Station', 'Operator', 'Start Time', 'End Time'])
    OrderDates = None
    completionDate = None
