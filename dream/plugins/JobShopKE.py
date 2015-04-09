from copy import copy, deepcopy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class JobShopKE(plugin.InputPreparationPlugin):
    """ Input preparation 
    """

    def preprocess(self, data):
        from dream.KnowledgeExtraction.PilotCases.JobShop.DataExtraction import DataExtraction
        receivedData = DataExtraction(data['general']["ServerAuth"])
        outputJSONString=json.dumps(receivedData, indent=True)
        outputJSONFile=open('dataFromSQL.json', mode='w')
        outputJSONFile.write(outputJSONString)
        data['input']['BOM'] = receivedData
        return data

    