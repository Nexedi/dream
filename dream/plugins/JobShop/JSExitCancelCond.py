from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy
from datetime import datetime

from dream.plugins import plugin


class JSExitCancelCond(plugin.InputPreparationPlugin):
  """ Input preparation 
      Read the exits end update them to cancelCondition-empty exits
  """

  def preprocess(self, data):
    """ Read the exits end update them to cancelCondition-empty exits. The simulation run should stop by the time all components have been cleared from the model 
    """
    nodes=data["graph"]["node"]
    for node, node_data in nodes.iteritems():
      if node_data.get("_class", None) == "Dream.ExitJobShop":
        node_data["cancelCondition"] = {"reason": "empty"}
    return data

