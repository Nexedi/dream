from copy import copy
import json
import time
import random
import operator
import StringIO
import xlrd

from dream.plugins import plugin

class BatchesTabularQueues(plugin.OutputPreparationPlugin):
    """ Output the exit stats in a tab
    """

    def postprocess(self, data):
        numberOfReplications=int(data['general']['numberOfReplications'])
        confidenceLevel=float(data['general']['confidenceLevel'])
        maxSimTime=float(data['general']['maxSimTime'])
        if numberOfReplications==1:
            # create the titles of the columns
            data['result']['result_list'][-1]['buffer_output'] = [['Buffer','Final Value','Average',
                                                                  'Std Dev','Min','Max',]]
            # loop the results and search for elements that have 'Exit' as family
            for record in data['result']['result_list'][-1]['elementList']:
                family=record.get('family',None)
                # when found, add a row with the results of the specific exit
                if family=='Buffer':
                    bufferId=record['id']
                    wip_stat_list=record['results']['wip_stat_list'][0]
                    bufferLevels=[int(x[1]) for x in wip_stat_list]
                    minLevel=min(bufferLevels)
                    maxLevel=max(bufferLevels)
                    self.createTimeListDict(wip_stat_list,maxSimTime)
        elif numberOfReplications>1:
            # create the titles of the columns
            pass
        return data

    # takes the time list that ManPy outputs and creates a dict so that it is easier to get avg etc
    def createTimeListDict(self, timeList,maxSimTime):
        timeListDict={}
        i=0
        for record in timeList:
            time=record[0]
            level=int(record[1])
            try:
                nextTime=timeList[i+1][0]
            except IndexError:
                nextTime=maxSimTime
            i+=1
            if not (level in timeListDict.keys()):
                timeListDict[level]=0
            timeListDict[level]+=nextTime-time
        print timeListDict
            
