from copy import copy
import json
import time
import random
import operator

from dream.simulation.GUI.Default import Simulation as DefaultSimulation


class Simulation(DefaultSimulation):
  def _preprocess(self, data):
    """Preprocess data, reading shift spreadsheet"""
    # TODO
    return data

  def run(self, data):
    return DefaultSimulation.run(self._preprocess(data))
