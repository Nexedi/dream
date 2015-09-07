'''
Created on 1 Aug 2015

@author: Anna
'''
from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class AddOfferPhaseGenerator(plugin.InputPreparationPlugin):
    """ Input preparation 
        adds an EventGenerator that will call the Offer Phase model once
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        data_uri_encoded_input_data = data['input'].get(self.configuration_dict['input_id_json'], {})      
        data_uri_encoded_workplan_data = data['input'].get(self.configuration_dict['input_id_workplan'], {})      
        
        algorithmAttributes=copy(data['general'])
        
        nodes['OPG']={
            "name": "OfferPhaseGenerator", 
            "prioritizeIfCanFinish": 1, 
            "interval": 1, 
            "start": 0,
            "stop": 0.5,
            "_class": "dream.simulation.EventGenerator.EventGenerator",
            "method": "dream.simulation.applications.FrozenSimulation.exeSim.exeSim",
            "argumentDict": {'jsonInput':data_uri_encoded_input_data, 'workplanInput':data_uri_encoded_workplan_data, 'algorithmAttributes':algorithmAttributes}
        }
        return data