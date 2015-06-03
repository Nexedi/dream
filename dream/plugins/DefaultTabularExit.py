from copy import copy
import json
import time
import random
import operator
import StringIO
import xlrd

from dream.plugins import plugin

class DefaultTabularExit(plugin.OutputPreparationPlugin):
    """ Output the exit stats in a tab
    """

    def postprocess(self, data):
        numberOfReplications=int(data['general']['numberOfReplications'])
        confidenceLevel=float(data['general']['confidenceLevel'])
        if numberOfReplications==1:
            # create the titles of the columns
            data['result']['result_list'][0]['exit_output'] = [['Exit Id','Throughput', 'Takt Time', 'Lifespan']]
            # loop the results and search for elements that have 'Exit' as family
            for record in data['result']['result_list'][0]['elementList']:
                family=record.get('family',None)
                # when found, add a row with the results of the specific exit
                if family=='Exit':
                    exitId=record['id']
                    throughput=int((record['results'].get('throughput','undefined'))[0])
                    taktTime=float((record['results'].get('takt_time','undefined'))[0])
                    lifespan=float((record['results'].get('lifespan','undefined'))[0])
                    data['result']['result_list'][0]['exit_output'].append([exitId,throughput,round(taktTime,2),round(lifespan,2)]) 
        elif numberOfReplications>1:
            # create the titles of the columns
            data['result']['result_list'][0]['exit_output'] = [['Exit Id','','Throughput','' , '','Takt Time','','', 'Lifespan',''],
                                                               ['','LB','AVG','UB','LB','AVG','UB','LB','AVG','UB']]
            for record in data['result']['result_list'][0]['elementList']:
                family=record.get('family',None)
                # when found, add a row with the results of the specific exit
                if family=='Exit':
                    exitId=record['id']
                    throughput=self.getConfidenceInterval(record['results'].get('throughput','undefined'),confidenceLevel)
                    taktTime=self.getConfidenceInterval(record['results'].get('takt_time','undefined'),confidenceLevel)
                    lifespan=self.getConfidenceInterval(record['results'].get('lifespan','undefined'),confidenceLevel)                 
                    data['result']['result_list'][0]['exit_output'].append([exitId,
                                                                            round(float(throughput['lb']),2),
                                                                            round(float(throughput['avg']),2),
                                                                            round(float(throughput['ub']),2),
                                                                            round(float(taktTime['lb']),2),
                                                                            round(float(taktTime['avg']),2),
                                                                            round(float(taktTime['ub']),2),      
                                                                            round(float(lifespan['lb']),2),
                                                                            round(float(lifespan['avg']),2),
                                                                            round(float(lifespan['ub']),2)                                                               
                                                                            ]) 
        return data