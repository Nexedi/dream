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
  # XXX hard-coded allowed station classes
  STATION_CLASS_SET = set(["Dream.MouldAssembly","Dream.MachineJobShop"])
  # XXX hardcoded values for CAD1 and CAD2 stations
  @staticmethod
  def getStationTechnologies():
    '''returns the technologies that can be processed on the stations'''
    return {"CAD1": ["ENG", "CAD"],         # XXX CAD1 is considered different than CAD2, they are not equivalent
            "CAD2": ["CAD"],
            "CAM": ["CAM"],
            "MILL": ["MILL"],
            "TURN": ["TURN"],
            "DRILL": ["DRILL"],
            "EDM": ["EDM"],
            "WORK": ["QUAL", "MAN"],        # XXX currently we consider different stations for QUAL/MAN and ASSM
            "ASSM": ["ASSM"],
            "INJM": ["INJM"]}

  def getStationInitials(self,technology):
    '''get the stations that correspond to that technology'''
    initialsList = []
    for initials, corresponding_tech_list in self.getStationTechnologies().iteritems():
      for tech in corresponding_tech_list:
        if tech == technology and not initials in initialsList:
          initialsList.append(initials)
    return initialsList
    
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
    orders = data["input"].get("BOM",{}).get("productionOrders",{})
    try:
      stations = data["input"]["BOM"]['stations1']
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
          assert len(self.getStationInitials(technology)), 'there is no corresponding station initial for that technology'
          step["technology"] = technology
          technologyStations = []
          for station in stations:
            station = station.replace(" ", "").split("-")[0]
            for initials in self.getStationInitials(technology):
              if station.startswith(initials)\
                 and data["graph"]["node"][station]["_class"] in self.STATION_CLASS_SET:
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