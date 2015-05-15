from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class SetTriangular(plugin.InputPreparationPlugin):
    """ Input preparation
        takes a model with deterministic processing time and sets it to triangular
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        for node_id,node in nodes.iteritems():
            if node.get('_class',None)==self.configuration_dict['input_id']:
                processingTime=node.get('processingTime',{})
                distribution=processingTime.get("Fixed",{})
                if distribution:
                    mean=distribution['mean']
                processingTime.pop('Fixed',None)
                processingTime['Triangular']={
                        "mean":mean,
                        "min":0.8*mean,
                        "max":1.2*mean
                    }
        return data
    