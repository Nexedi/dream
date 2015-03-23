from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class CapacityStationsSetAssemblySpace(plugin.InputPreparationPlugin):
    """ Input preparation 
        creates the CapacityStationBuffer and CapacityStationExit for each CapacityStation
    """

    def preprocess(self, data):
        assemblySpace=int(copy(data['general']).get('assemblySpace',100))
        data['general']['extraPropertyDict']={}
        data['general']['extraPropertyDict']['assemblySpace']=assemblySpace
        return data
    
