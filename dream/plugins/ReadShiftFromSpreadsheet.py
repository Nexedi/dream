from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class ReadShiftFromSpreadsheet(plugin.InputPreparationPlugin):
  """ Input prepration 
      read wip-srpeadsheet data and update the wip property of the stations.
  """

  def preprocess(self, data):
      return data