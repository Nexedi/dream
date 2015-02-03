from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

# XXX HARDCODED
MACHINE_TYPE_SET = set(["Dream.MachineJobShop", "Dream.MouldAssembly"]) 
class SplitRoute(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the data from external data base and splits the routes if the parts described are design and mould
  """
  
  def getNotMachineNodePredecessorList(self, stationIDs_list):
    """
    Give the list of all predecessors that are not of type machine
    For example, for stations with ids that starts with "CAM", it may return "QCAM"
    """
    predecessor_list = []
    for edge in self.data["graph"]["edge"].values():
        if edge["destination"] in stationIDs_list:
            predecessor_step = edge["source"]
            if predecessor_step in predecessor_list:
                continue
            if not self.data["graph"]["node"][predecessor_step]["_class"] in MACHINE_TYPE_SET:
                predecessor_list = [predecessor_step] + predecessor_list
                predecessor_list = [x for x in getNotMachineNodePredecessorList([predecessor_step]) \
                                    if x not in predecessor_list] + predecessor_list
    return predecessor_list

  def getNotMachineNodeSuccessorList(self, stationIDs_list):
    """
    Give the list of all successors that are not of type machine
    For example, for stations of technology "CAM", it may return "Decomposition"
                 for stations of technology "INJM-MAN" or "INJM" it may return "Exit"
    """
    successor_list = []
    for edge in self.data["graph"]["edge"].values():
        if edge["source"] in stationIDs_list:
            successor_step = edge["destination"]
            if successor_step in successor_list:
                continue
            if not self.data["graph"]["node"][successor_step]["_class"] in MACHINE_TYPE_SET:
                successor_list = [successor_step] + successor_list
                successor_list = [x for x in getNotMachineNodeSuccessorList([successor_step]) \
                                    if x not in successor_list] + successor_list
    return successor_list
  
  ROUTE_STEPS_SET=set(["ENG", "CAD","CAM","MILL", "MILL-SET","TURN", "DRILL", "QUAL","EDM", "EDM-SET","ASSM", "MAN","INJM", "INJM-MAN", "INJM-SET"])
  DESIGN_ROUTE_STEPS_SET=set(["ENG", "CAD"])
  ASSEMBLY_ROUTE_STEPS_SET=set(["QASSM"])
  MOULD_ROUTE_STEPS_SET=set(["ASSM","INJM","INJM-MAN","INJM-SET"])
  def preprocess(self, data):
    """ splits the routes of mould parts (design + mould)
    """
	self.data = copy(data)
    orders = self.data["BOM"]["orders"]
	stations = self.data["BOM"]["stations"]
	graph_data = self.data["graph"]
	nodes = graph_data["node"]
	
	
	for order in orders:
		orderComponents = order.get("componentsList", [])
		for index, component in enumerate(orderComponents):
			route = component.get("route", [])
			design_step_list = []
            # for each step of the components route find out if it is of a design route (ENG - CAD) or of mould route (ASSM-INJM). If the route contains none of these technology-types steps then the component is normal
			routeList = deepcopy(route)
			i = 0
			for step in routeList:
				stepTechnology = step.get('technology',[])
				assert stepTechnology in ROUTE_STEPS_SET, 'the technology provided does not exist'
				if stepTechnology in DESIGN_ROUTE_STEPS_SET:
					design_step_list.append(step)
					route.pop(i)
				else:
					i+=1
			if design_step_list:
				design = {"componentName": component.get("componentName","")+"Design",
						  "componentID": component.get("componentID","")+"D",
					      "quantity": component.get("quantity", 1),
					      "route": design_step_list}
				orderComponents.append(design)
    return data

if __name__ == '__main__':
    pass