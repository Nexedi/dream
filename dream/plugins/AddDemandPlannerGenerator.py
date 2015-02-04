from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class AddDemandPlannerGenerator(plugin.InputPreparationPlugin):
    """ Input preparation 
        adds an EventGenerator that will call the Demand Planning algorithm once
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        nodes['DPG']={
            "name": "DemandPlannerGenerator", 
            "prioritizeIfCanFinish": 1, 
            "interval": 1, 
            "start": 0,
            "stop": 0.5,
            "_class": "dream.simulation.EventGenerator.EventGenerator",
            "method": "dream.simulation.applications.DemandPlanning.executor_ACO.main"
        }
        #print nodes
        return data

    