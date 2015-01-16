from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class ReadEntryData(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the entries if any, and updates the keys of the entityData dict
  """

  def preprocess(self, data):
    """ read the entries data and change the class key of the entityData dict to _class
    """
    node=data['graph']['node']
    for stationKey, stationData in node.iteritems():
      entityData = stationData.pop("entityData", None)
      if entityData:
        entityClass = entityData.pop("class", None)
        if entityClass:
          entityData["_class"] = entityClass
        else:
          entityData["_class"] = "Dream.Part"
        stationData["entityData"] = entityData

    return data

