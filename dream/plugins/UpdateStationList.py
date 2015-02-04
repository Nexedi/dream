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

  def preprocess(self, data):
    """ substitutes the technology information with stationIDs lists
    """
    orders = data["input"]["BOM"]['orders']
	stations = data["input"]["BOM"]['stations']
	nodes = data["graph"]["node"]
	
	for order in orders:
		orderComponents = order.get("componentsList", [])
		for component in orderComponents:
			route = component.get("route", [])
			for index, step in enumerate(route):
				technology = step.pop("technology", None)
				technology = technology.split("-")[0]
				technologyStations = []
				for station in stations:
					if station.startswith(technology):
						found = False # check that the id of the station provided by the db BOM exist in the nodes of the graph
						for node in nodes:
							if node["id"] == station:
								found = True
								break
						assert found == True, "the station ids in the DB must be the same with the stations ids provided by the model"
						technologyStations.append(station)
				assert len(technologyStations)>0, "the stations corresponding to the defined technology must be more than 0"
				step["stationIdsList"] = technologyStations
    return data

if __name__ == '__main__':
    pass