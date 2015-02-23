from copy import copy
import json
import time
import random
import operator
import StringIO
import xlrd

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
                    unitsThroughput=record['results']['unitsThroughput'][0]
                    data['result']['result_list'][0]['exit_output'].append(['Number of units produced','Units',
                                                                            unitsThroughput]) 
                    lineThroughput=batchesThroughput/float(maxSimTime)
                    data['result']['result_list'][0]['exit_output'].append(['Line throughput','Batches/'+timeUnit+'s',
                                                                            lineThroughput]) 
                    unitDepartureRate=unitsThroughput/float(maxSimTime)
                    data['result']['result_list'][0]['exit_output'].append(['Average Unit Departure Rate',
                                                                            'Units/'+timeUnit+'s',
                                                                            unitDepartureRate]) 
                    avgCycleTime=record['results']['lifespan'][0]
                    data['result']['result_list'][0]['exit_output'].append(['Average Cycle Time',
                                                                            timeUnit+'s',
                                                                            avgCycleTime])                   
        elif numberOfReplications>1:
            # create the titles of the columns
            data['result']['result_list'][0]['exit_output'] = [['Exit Id','','Throughput','' , '','Takt Time','','', 'Lifespan',''],
                                                               ['','LB','AVG','RB','LB','AVG','RB','LB','AVG','RB']]
            for record in data['result']['result_list'][0]['elementList']:
                family=record.get('family',None)
                # when found, add a row with the results of the specific exit
                if family=='Exit':
                    exitId=record['id']
                    throughput=self.getConfidenceInterval(record['results'].get('throughput','undefined'),confidenceLevel)
                    taktTime=self.getConfidenceInterval(record['results'].get('takt_time','undefined'),confidenceLevel)
                    lifespan=self.getConfidenceInterval(record['results'].get('lifespan','undefined'),confidenceLevel)                 
                    data['result']['result_list'][0]['exit_output'].append([exitId,
                                                                            throughput['lb'],throughput['avg'],throughput['ub'],
                                                                            taktTime['lb'],taktTime['avg'],taktTime['ub'],
                                                                            lifespan['lb'],lifespan['avg'],lifespan['ub']]) 
        return data
    
    def getConfidenceInterval(self, value_list, confidenceLevel):
        from dream.KnowledgeExtraction.ConfidenceIntervals import Intervals
        from dream.KnowledgeExtraction.StatisticalMeasures import BasicStatisticalMeasures
        BSM=BasicStatisticalMeasures()
        lb, ub = Intervals().ConfidIntervals(value_list, confidenceLevel)
        return {'lb': lb,
                'ub': ub,
                'avg': BSM.mean(value_list) 
            }