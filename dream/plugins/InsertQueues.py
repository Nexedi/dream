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
class InsertQueues(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the data from external data base and inserts buffers before the corresponding stations
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
  

  def preprocess(self, data):
    """ inserts buffers before the corresponding stations
    """
	self.data = copy(data)
    orders = self.data["BOM"]["orders"]
	stations = self.data["BOM"]["stations"]
	graph_data = self.data["graph"]
	nodes = graph_data["node"]
	
	
	for order in orders:
		orderComponents = order.get("componentsList", [])
		for component in orderComponents:
			updatedRoute = []
			route = component.get("route", [])
# XXX separate mould from design
			for step in route:
				stationIdsList = step.get("stationIdsList", [])
				
				

			for index, step in enumerate(route):
				stationIdsList = step.get("stationIdsList", [])
				
				
				for predecessor in self.getNotMachineNodePredecessorList(stationIdsList):
# XXX if the component is a mould then before the assembly do not add AssemblyBuffer
					if predecessor.startswith("ASSM"):
						break
# XXX if there is a QCAM there must an OrderDecomposition come
					if predecessor.startswith("QCAM"):
						for pre_predecessor in self.getNotMachineNodePredecessorList([predecessor]):
							"""insert this step (pre_predecessor) to the route
								{"stationIdsList": [pre_predecessor],}
							"""
					"""insert this step (predecessor) to the route
						{"stationIdsList": [predecessor],}
					"""
# XXX design case -  add OrderDecomposition
				if any(station.startswith("CAD") for station in stationIdsList) and index==len(route)-1:
					for successor in self.getNotMachineNodeSuccessorList(stationIdsList):
						"""insert this step (successor) to the route
							{"stationIdsList": [succecssor],}
						"""
# XXX mould case - add exit
				elif any(station.startswith("INJ") for station in stationIdsList) and index == len(route)-1:
					for successor in self.getNotMachineNodeSuccessorList(stationIdsList):
						"""insert this step (successor) to the route
							{"stationIdsList": [succecssor],}
						"""
# XXX normal components - add ASSM buffer and ASSM after manual operations?
				elif index == len(route)-1:
					exitAssigned=(station.startswith("ASS") for station in stationIdsList)
					if not exitAssigned:
						"""insert ASSM buffer to the route
							{"stationIdsList": [AssemblyBufferIdsList],}
						"""
						"""insert ASSM to the route
							{"stationIdsList": [AssemblyIdsList],}
						"""

				
				# XXX route.insert(indexToInsert, additionalStep)
			
    return data

if __name__ == '__main__':
    pass