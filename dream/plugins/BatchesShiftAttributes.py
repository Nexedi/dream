from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class BatchesShiftAttributes(plugin.InputPreparationPlugin):
  """ Input preparation 
      set the shift attributes in the Batch instance
  """

  def preprocess(self, data):
    """ set the shift attributes in the Batch instance
    """
    nodes=data['graph']['node']
    for node_id, node in nodes.iteritems():
        interruptions=node.get('interruptions',None)
        if interruptions:
            shift=interruptions.get('shift',None)
            if shift:
                interruptions['shift']['thresholdTimeIsOnShift']=0
                interruptions['shift']['receiveBeforeEndThreshold']=7
                interruptions['shift']['endUnfinished']=1
    return data