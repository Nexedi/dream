'''
Created on 31 Aug 2015

@author: Anna
'''

import tablib

class G:
    
    Schedule={}
    MachPool = None
    PMPool = None
    Projects = None
    xlreftime = None
    OrderDates = None
    jsonInput = None
    excelInput = None
    simMode = None
    
    # reporting tabs
    reportResults = tablib.Databook()
    tabSchedule = {}
    pmSchedule = {}
    tabScheduleOrig = []
    pmScheduleOrig = []
    
    # re-initialised variables
    completionDate = {}
    seqPrjDone = None
    resAvailability = None
    seqPrjDoneOrig = None
    resAvailabilityOrig = None
