from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

# XXX HARDCODED
MACHINE_TYPE_SET = set(["Dream.MachineJobShop", "Dream.MouldAssembly"])
EXIT_TYPE_SET = set(["Dream.ExitJobShop"])
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
          predecessor_list = [x for x in self.getNotMachineNodePredecessorList([predecessor_step]) \
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
          successor_list = [x for x in self.getNotMachineNodeSuccessorList([successor_step]) \
                              if x not in successor_list] + successor_list
    return successor_list
  
  def getExitStations(self):
    """returns the exits of the system"""
    nodes = self.data["graph"]["node"]
    exitList = []
    for nodeID, node in nodes.iteritems():
      if node["_class"] in EXIT_TYPE_SET:
        exitList.append(nodeID)
    return exitList

  def preprocess(self, data):
    """ inserts buffers before the corresponding stations
    """
    self.data = copy(data)
    orders = self.data["input"].get("BOM",{}).get("productionOrders",{})
    nodes = self.data["graph"]["node"]
    for order in orders:
      orderComponents = order.get("componentsList", [])
      for component in orderComponents:
        route = component.get("route", [])
        componentType = None
        index = 0
        tempRoute = copy(route)
        for tempIndex, step in enumerate(tempRoute):
          stationIdsList = step.get("stationIdsList", [])
          technology = step["technology"]
          sequence = step["sequence"]
          task_id = step["task_id"]
          ''' add predecessors wherever needed (buffers, OrderDecomposition) '''
          for predecessor in self.getNotMachineNodePredecessorList(stationIdsList):
            # # if the component is a mould then before the assembly do not add AssemblyBuffer
            if predecessor.startswith("ASSM"):
              break
            # if the predecessor is OrderDecomposition then task_id and sequence are ""
            if predecessor.startswith("OD"):
              temp_sequence = temp_task_id = ""
            else:
              temp_sequence = sequence
              temp_task_id = task_id
            route.insert(index, {"stationIdsList": [predecessor],
                                 "sequence": temp_sequence,
                                 "task_id": temp_task_id})
            index+=1
          '''find out if the part's route starts with ASSM'''
          if technology.startswith("ASS") and tempIndex == 0:
            componentType = "Mold"
          
          ''' add successors wherever needed (buffers, OrderDecomposition, exit, AssemblyBuffer, Assembly stations) '''
          # # design case -  add OrderDecomposition at the end of a design route
          if any(station.startswith("CAD") for station in stationIdsList) and tempIndex==len(tempRoute)-1:
            for successor in self.getNotMachineNodeSuccessorList(stationIdsList):
              # if the successor is a CAM buffer then do not add it to the route of the design
              if successor.startswith("QCAM"):
                continue
              route.append({"stationIdsList": [successor],
                            "sequence": "",
                            "task_id": ""})
          # # mould case - add exit at the a mould route
          elif componentType=="Mold" and tempIndex == len(tempRoute)-1:
            route.append({"stationIdsList": self.getExitStations(),
                          "sequence": sequence,
                          "task_id": task_id})
              
          # # normal components - add ASSM buffer and ASSM at the end of their route
          elif tempIndex == len(tempRoute)-1 and not componentType == "Mold":
            # exitAssigned=any(station.startswith("ASS") for station in stationIdsList)
            exitAssigned=technology.startswith("ASS")
            if not exitAssigned:
              """find the sequence and task_id that has the assembly for the mould component"""
              for sibling in orderComponents:
                for siblingStep in sibling["route"]:
                  # if any(proc.startswith("ASS") for proc in siblingStep["stationIdsList"]):
                  if siblingStep.get("technology", " ").startswith("ASS"):
                    if siblingStep["task_id"]:
                      assembly_sequence = siblingStep["sequence"]
                      assembly_task_id = siblingStep["task_id"]
              # # add assemble buffers to the route
              assemblyBufferIDlist = []
              for nodeID, node in nodes.items():
                if node["_class"] == "Dream.MouldAssemblyBuffer":
                  assemblyBufferIDlist.append(str(nodeID))
              if assemblyBufferIDlist:
                route.append({"stationIdsList": assemblyBufferIDlist, 
                              "sequence": assembly_sequence,
                              "task_id": assembly_task_id})
              # # add assemblers to the route
              assemblyIDlist = []
              for nodeID, node in nodes.items():
                if node["_class"] == "Dream.MouldAssembly":
                  assemblyIDlist.append(str(nodeID))
              if assemblyIDlist:
                route.append({"stationIdsList": assemblyIDlist,
                              "sequence": assembly_sequence,
                              "task_id": assembly_task_id,
                              "technology": "ASSM"})

          index+=1
    return data

if __name__ == '__main__':
    pass