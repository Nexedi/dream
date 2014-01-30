from copy import copy
import json
import time
import random
import operator

from dream.simulation.GUI.Default import Simulation as DefaultSimulation


class Simulation(DefaultSimulation):
  def getConfigurationDict(self):
    conf = DefaultSimulation.getConfigurationDict(self)
    conf["Dream-Configuration"]["gui"]["shift_spreadsheet"] = 1
    return conf

  def _preprocess(self, data):
    """Preprocess data, reading shift spreadsheet"""
    # TODO
    return data

