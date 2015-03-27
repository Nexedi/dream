from copy import copy, deepcopy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class CapacityStationsKE(plugin.InputPreparationPlugin):
    """ Input preparation 
        creates the CapacityStationBuffer and CapacityStationExit for each CapacityStation
    """

    def preprocess(self, data):
        from dream.KnowledgeExtraction.PilotCases.CapacityStations.DataExtraction import DataExtraction
        from dream.KnowledgeExtraction.PilotCases.CapacityStations.OutputPreparation import OutputPreparation
        DBFilePath=data['general']['ServerAuth']
        extractedData=DataExtraction(DBFilePath)
        data=OutputPreparation(data,extractedData)
        return data

    