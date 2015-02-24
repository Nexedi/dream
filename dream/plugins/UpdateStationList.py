from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class UpdateStationList(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the data from external data base and substitutes the technology information with stationIDs lists
  """
  @staticmethod
  def getStationTechnologies():
    '''returns the technologies that can be processed on the stations'''
    return {"CAD": ["ENG", "CAD"],
            "CAM": ["CAM"],
            "MILL": ["MILL"],
            "TURN": ["TURN"],
            "DRILL": ["DRILL"],
            "EDM": ["EDM"],
            "WORK": ["QUAL", "ASSM", "MAN"],
            "INJM": ["INJM"]}

  def getStationInitials(self,technology):
    '''get the stations that correspond to that technology'''
    for initials, corresponding_tech_list in self.getStationTechnologies().iteritems():
      for tech in corresponding_tech_list:
        if tech == technology:
          return initials
    return None
    
  def getStationNames(self):
    node = self.data["graph"]["node"]
    stations = []
    for nodeID in node.keys():
      stations.append(nodeID)
    return stations
  
  def preprocess(self, data):
    """ substitutes the technology information with stationIDs lists
    """
    self.data = data
    orders = data["input"]["BOM"]['orders']
    try:
      stations = data["input"]["BOM"]['stations']
    except:
      stations = self.getStationNames()
    nodes = data["graph"]["node"]
    
    for order in orders:
      orderComponents = order.get("componentsList", [])
      for component in orderComponents:
        route = component.get("route", [])
        for index, step in enumerate(route):
          technology = step.get("technology", None)
          technology = technology.split("-")[0]
          assert self.getStationInitials(technology), 'there is no corresponding station initial for that technology'
          step["technology"] = technology
          technologyStations = []
          for station in stations:
            if station.startswith(self.getStationInitials(technology)):
              found = False # check that the id of the station provided by the db BOM exist in the nodes of the graph
              for node in nodes.keys():
                if node == station:
                  found = True
                  break
              assert found == True, "the station ids in the DB must be the same with the stations ids provided by the model"
              technologyStations.append(station)
          assert len(technologyStations)>0, "the stations corresponding to the defined technology must be more than 0"
          step["stationIdsList"] = technologyStations
    return data

if __name__ == '__main__':
    pass