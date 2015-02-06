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
        # create the titles of the columns
        data['result']['result_list'][0]['exit_output'] = [['Exit Id','Throughput', 'Takt Time', 'Lifespan']]
        # loop the results and search for elements that have 'Exit' as family
        for record in data['result']['result_list'][0]['elementList']:
            family=record.get('family',None)
            # when found, add a row with the results of the specific exit
            if family=='Exit':
                exitId=record['id']
                throughput=record['results'].get('throughput','undefined')
                taktTime=record['results'].get('takt_time','undefined')
                lifespan=record['results'].get('lifespan','undefined')
                data['result']['result_list'][0]['exit_output'].append([exitId,throughput,taktTime,lifespan]) 
        return data