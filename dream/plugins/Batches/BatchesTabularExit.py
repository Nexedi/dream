from copy import copy
import json
import time
import random
import operator
import StringIO
import xlrd
import numpy

from dream.plugins import plugin

class BatchesTabularExit(plugin.OutputPreparationPlugin):
    """ Output the exit stats in a tab
    """

    def postprocess(self, data):
        numberOfReplications=int(data['general']['numberOfReplications'])
        confidenceLevel=float(data['general']['confidenceLevel'])
        maxSimTime=data['general']['maxSimTime']
        timeUnit=data['general']['timeUnit']
        if numberOfReplications==1:
            # create the titles of the columns
            data['result']['result_list'][0]['exit_output'] = [['KPI','Unit','Value']]
            # loop the results and search for elements that have 'Exit' as family
            for record in data['result']['result_list'][-1]['elementList']:
                family=record.get('family',None)
                # when found, add a row with the results of the specific exit
                if family=='Exit':
                    batchesThroughput=record['results']['throughput'][0]
                    data['result']['result_list'][0]['exit_output'].append(['Number of batches produced','Batches',
                                                                            batchesThroughput])                     
                    unitsThroughput=record['results'].get('unitsThroughput',None)
                    if unitsThroughput:
                        unitsThroughput=unitsThroughput[0]
                    if not unitsThroughput:
                        unitsThroughput=batchesThroughput
                    data['result']['result_list'][0]['exit_output'].append(['Number of units produced','Units',
                                                                            unitsThroughput]) 
                    lineThroughput=batchesThroughput/float(maxSimTime)
                    data['result']['result_list'][0]['exit_output'].append(['Line throughput','Batches/'+timeUnit,
                                                                            "%.2f" % lineThroughput]) 
                    unitDepartureRate=unitsThroughput/float(maxSimTime)
                    data['result']['result_list'][0]['exit_output'].append(['Average Unit Departure Rate',
                                                                            'Units/'+timeUnit,
                                                                            "%.2f" % unitDepartureRate]) 
                    avgCycleTime=record['results']['lifespan'][0]
                    data['result']['result_list'][0]['exit_output'].append(['Average Cycle Time',
                                                                            timeUnit,
                                                                            "%.2f" % avgCycleTime])
                    
                    # output the productivity metric
                    # ToDo, this currently works only for one replication
                    totalOperatorHours=self.getTotalOperatorOnShiftHours(data['result']['result_list'][0]['elementList'],maxSimTime)
                    if totalOperatorHours:
                        productivity=unitsThroughput/totalOperatorHours
                        data['result']['result_list'][0]['exit_output'].append(['Productivity',
                                                                                "Produced Units/Operator Hours",
                                                                                "%.2f" % productivity])                                   
        elif numberOfReplications>1:
            # create the titles of the columns
            data['result']['result_list'][0]['exit_output'] = [['KPI','Unit','Average','Std Dev','Min','Max',
                                                                str(float(confidenceLevel)*100)+'% CI LB ',
                                                                str(float(confidenceLevel)*100)+'% CI UB']]
            for record in data['result']['result_list'][0]['elementList']:
                family=record.get('family',None)
                # when found, add a row with the results of the specific exit
                if family=='Exit':
                    batchesThroughputList=record['results']['throughput']
                    batchesThroughputCI=self.getConfidenceInterval(batchesThroughputList,confidenceLevel)
                    data['result']['result_list'][0]['exit_output'].append(['Number of batches produced','Batches',
                                                                            "%.2f" % self.getAverage(batchesThroughputList),
                                                                            "%.2f" % self.getStDev(batchesThroughputList),
                                                                            min(batchesThroughputList),
                                                                            max(batchesThroughputList),
                                                                            "%.2f" % batchesThroughputCI['lb'],
                                                                            "%.2f" % batchesThroughputCI['ub']]
                                                                           )    
                    unitsThroughputList=record['results'].get('unitsThroughput',None)
                    if not unitsThroughputList:
                        unitsThroughputList=batchesThroughputList
                    unitsThroughputList=record['results']['unitsThroughput']
                    unitsThroughputCI=self.getConfidenceInterval(unitsThroughputList,confidenceLevel)
                    data['result']['result_list'][0]['exit_output'].append(['Number of units produced','Units',
                                                                            "%.2f" % self.getAverage(unitsThroughputList),
                                                                            "%.2f" % self.getStDev(unitsThroughputList),
                                                                            min(unitsThroughputList),
                                                                            max(unitsThroughputList),
                                                                            "%.2f" % unitsThroughputCI['lb'],
                                                                            "%.2f" % unitsThroughputCI['ub']]
                                                                           )    
                    lineThroughputList=[x/float(maxSimTime) for x in batchesThroughputList]
                    lineThroughputCI=self.getConfidenceInterval(lineThroughputList,confidenceLevel)
                    data['result']['result_list'][0]['exit_output'].append(['Line throughput','Batches/'+timeUnit,
                                                                            "%.2f" % self.getAverage(lineThroughputList),
                                                                            "%.2f" % self.getStDev(lineThroughputList),
                                                                            "%.2f" % min(lineThroughputList),
                                                                            "%.2f" % max(lineThroughputList),
                                                                            "%.2f" % lineThroughputCI['lb'],
                                                                            "%.2f" % lineThroughputCI['ub']]
                                                                           ) 
                    unitDepartureRateList=[x/float(maxSimTime) for x in unitsThroughputList]
                    unitDepartureRateCI=self.getConfidenceInterval(unitDepartureRateList,confidenceLevel)
                    data['result']['result_list'][0]['exit_output'].append(['Unit Departure Rate',
                                                                            'Units/'+timeUnit,
                                                                            "%.2f" % self.getAverage(unitDepartureRateList),
                                                                            "%.2f" % self.getStDev(unitDepartureRateList),
                                                                            "%.2f" % min(unitDepartureRateList),
                                                                            "%.2f" % max(unitDepartureRateList),
                                                                            "%.2f" % unitDepartureRateCI['lb'],
                                                                            "%.2f" % unitDepartureRateCI['ub']]
                                                                           )      
                    avgCycleTime=record['results']['lifespan']         
                    avgCycleTimeList=record['results']['lifespan']
                    avgCycleTimeCI=self.getConfidenceInterval(avgCycleTimeList,confidenceLevel)
                    data['result']['result_list'][0]['exit_output'].append(['Cycle Time',timeUnit,
                                                                            "%.2f" % self.getAverage(avgCycleTimeList),
                                                                            "%.2f" % self.getStDev(avgCycleTimeList),
                                                                            "%.2f" % min(avgCycleTimeList),
                                                                            "%.2f" % max(avgCycleTimeList),
                                                                            "%.2f" % avgCycleTimeCI['lb'],
                                                                            "%.2f" % avgCycleTimeCI['ub']]
                                                                           ) 
        return data
    
    
    def getTotalOperatorOnShiftHours(self,results,maxSimTime):
        totalOperatorOnShiftHours=0.0
        for element in results:
            if element.get('family',None)=='Operator':
                totalOperatorOnShiftHours+=maxSimTime*(1-element['results']['off_shift_ratio'][0]/100.0)
        return totalOperatorOnShiftHours