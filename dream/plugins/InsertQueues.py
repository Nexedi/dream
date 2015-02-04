from copy import copy
import json
import time
import random
import operator
from datetime import datetime

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
    orders = self.data["input"]["BOM"]["orders"]
	nodes = self.data["graph"]["node"]
	
	for order in orders:
		orderComponents = order.get("componentsList", [])
		for component in orderComponents:
			updatedRoute = []
			route = component.get("route", [])
			index = 0
			tempRoute = copy.deepcopy(route)
			for tempIndex, step in enumerate(tempRoute):
				stationIdsList = step.get("stationIdsList", [])
				''' add predecessors wherever needed (buffers, OrderDecomposition) '''
				predecessor_list = []
				for predecessor in self.getNotMachineNodePredecessorList(stationIdsList):
					# # if the component is a mould then before the assembly do not add AssemblyBuffer
					if predecessor.startswith("ASSM"):
						break
					# # if there is a QCAM there must an OrderDecomposition inserted before that
					if predecessor.startswith("QCAM"):
						pre_predecessor_list = []
						for pre_predecessor in self.getNotMachineNodePredecessorList([predecessor]):
							pre_predecessor_list.append(pre_predecessor)
						if pre_predecessor_list:
							route.insert(index, {"stationIdsList" : pre_predecessor_list,})
							index+=1
					predecessor_list.append(predecessor)
				if predecessor_list:
					route.insert(index, {"stationIdsList": predecessor_list,})
					index+=1
				''' add successors wherever needed (buffers, OrderDecomposition, exit, AssemblyBuffer, Assembly stations) '''
				# # design case -  add OrderDecomposition at the end of a design route
				if any(station.startswith("CAD") for station in stationIdsList) and tempIndex==len(tempRoute)-1:
					successor_list = []
					for successor in self.getNotMachineNodeSuccessorList(stationIdsList):
						successor_list.append(successor)
					if successor_list:
						route.insert(index, {"stationIdsList": successor_list,})
						index+=1
				# # mould case - add exit at the a mould route
				elif any(station.startswith("INJM") for station in stationIdsList) and tempIndex == len(tempRoute)-1:
					for successor in self.getNotMachineNodeSuccessorList(stationIdsList):
						successor_list.append(successor)
					if successor_list:
						route.insert(index, {"stationIdsList": successor_list,})
						index+=1
				# # normal components - add ASSM buffer and ASSM at the end of their route
				elif tempIndex == len(tempRoute)-1:
					exitAssigned=any(station.startswith("ASS") for station in stationIdsList)
					if not exitAssigned:
						# # add assemble buffers to the route
						assemblyBufferIDlist = []
						for nodeID, node in nodes.items():
							if node["_class"] = "Dream.MouldAssemblyBuffer":
								assemblyBufferIDlist.append(str(nodeID))
						if assemblyBufferIDlist:
							route.insert(index,{"stationIdsList": assemblyBufferIDlist, })
							index+=1
						# # add assemblers to the route
						assemblyIDlist = []
						for nodeID, node in nodes.items():
							if node["_class"] = "Dream.MouldAssembly":
								assemblyIDlist.append(str(nodeID))
						if assemblyIDlist:
							route.insert(index,{"stationIdsList": assemblyIDlist, })
							index+=1

				index+=1
			
    return data

if __name__ == '__main__':
    pass