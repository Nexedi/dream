from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class BatchesWIPKEtool(plugin.InputPreparationPlugin):
    """ Input preparation 
        reads the WIP from the short format
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        print 2
        return data    
        
        
    