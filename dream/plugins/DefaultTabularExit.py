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
        node=data['graph']['node']
        data['result']['result_list'][0]['exit_output'] = [['Exit Id','Throughput', 'Takt Time', 'Lifespan']]
        for record in data['result']['result_list'][0]['elementList']:
            family=record.get('family',None)
            if family=='Exit':
                exitId=record['id']
                throughput=record['results'].get('throughput','undefined')
                taktTime=record['results'].get('takt_time','undefined')
                lifespan=record['results'].get('lifespan','undefined')
                data['result']['result_list'][0]['exit_output'].append([exitId,throughput,taktTime,lifespan]) 
        return data