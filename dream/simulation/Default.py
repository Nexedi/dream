import json
from dream.simulation.LineGenerationJSON import main as simulate_line_json

class Simulation:
  def __init__(self, logger=None):
    self.logger = logger

  def run(self, data):
    return simulate_line_json(input_data=json.dumps(data))
