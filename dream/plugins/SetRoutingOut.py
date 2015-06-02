from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class SetRoutingOut(plugin.InputPreparationPlugin):
    """ Input preparation
        takes a model and if the queue is set to priority sets the class to selectiveQueue
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        for node_id,node in nodes.iteritems():
            if node.get('_class',None)=='Dream.Queue':
                if node.get('routingOut',None)=='Priority':
                    node['_class']="dream.simulation.Examples.SelectiveQueue.SelectiveQueue"
        return data
    