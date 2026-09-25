from copy import copy

from dream.plugins import plugin
from dream.plugins import SplitRoute
import datetime
# XXX HARDCODED
MACHINE_TYPE_SET = set(["Dream.MachineJobShop", "Dream.MouldAssembly"]) 
class UpdateWIP(SplitRoute.SplitRoute):
  """ Input preparation
      reads the data from external data base and updates the WIP
  """
  
  def getWIPIds(self):
    """returns the ids of the parts that are in the WIP dictionary"""
    wipIDs = []
    for key in self.data["input"]["BOM"].get("WIP", {}).keys():
      wipIDs.append(key)
    return wipIDs

  def preprocess(self, data):
    """ updates the Work in Process according to what is provided by the BOM, i.e. if a design just exited the last step of it's sequence
    """
    self.data = copy(data)
    orders = self.data["input"].get("BOM",{}).get("productionOrders",{})
    nodes = self.data["graph"]["node"]
    wip = self.data["input"].get("BOM",{}).get("WIP", {})
  
    """ get the tasks that are in the WIP, and place those that are not in the WIP in the corresponding stations. Consider the parts that have concluded their routes, or the components that are not created yet.
    All the components defined by the corresponding orders should be examined
    """
    wipToBeRemoved = []
    designsToBeReplaced = []  # list used to hold the designID that are in the WIP and need to change key (id) as the current one correspond to the molds  ids
    # # check all the orders
    for order in orders:
      orderComponents = order.get("componentsList", [])
      designComplete = False          # flag to inform if the design is concluded
      completedComponents = []        # list to hold the componentIDs that are concluded
      # # find all the components
      for component in orderComponents:
        componentID = component["id"]
        route = component["route"] 
        # # figure out if they are defined in the WIP
        if componentID in self.getWIPIds():
          work = wip[componentID]
          # # extract WIP information
          workStation = work["station"]
          remainingProcessingTime = float(work.get("remainingProcessingTime",0))
          remainingSetupTime = float(work.get('remainingSetupTime', 0))
          task_id = work["task_id"]
          sequence = work.get('sequence', 0)
          assert len(route)>0, "the OrderComponent must have a route defined with length more than 0"
          assert task_id, "there must be a task_id defined for the OrderComponent in the WIP"
          # # get the step identified by task_id, hold the step_index to see if the entity's route is concluded
          last_step = {}
          for step_index, step in enumerate(route):
            if step["task_id"] == task_id and step.get("technology", None):
              last_step = step
              break
          # # check if the entity has left the station
          toBeRemoved = False
          if remainingProcessingTime:
            # if the last_step is not found (the step identified from the wip corresponds to a setup and the task_id of that task is merged to the task_id of the following normal processing task) - this can happen for INJM, MILL, and EDM technologies that correspond to SETUP and normal PROCESSING
            if not last_step:
              # find the step that follows (normal processing)
              for step in route:
                # introduced to fix the case were sequence is ''
                if not step.get('sequence', 0) == '':
                  # the sequences must differ maximum one
                  if int(sequence)+1 == int(step.get('sequence',0)):
                    # and the corresponding step must have a defined technology
                    if step.get('technology', None):
                      # the station defined by the WIP must start with the technology initials (only INJM, EDM, and MILL)
                      if workStation.startswith(step['technology']):
                        last_step = step
                        # the time defined as remaining processing time is remainingSetupTime
                        remainingSetupTime = remainingProcessingTime
                        # and the remainingProcessingTime should be extracted from the step
                        remainingProcessingTime = step.get('processingTime', 0)
                        break
            # if the workstation provided is not a valid station but instead the name of a technology (this happens only with EDM, INJM, and MILL that have setup and processing seperate)
            if not workStation in last_step.get("stationIdsList", []):
              if workStation == last_step.get("technology", None):
                # try to find a not occupied station and set it as the workstation instead of the technology name given.
                occupiedStations = [wipPart["station"] for wipPart in wip.values()]
                for nodeId in last_step['stationIdsList']:
                  if not nodeId in occupiedStations:
                    workStation = nodeId
            currentStation = workStation
            current_step = last_step
            # if the current step is part of a design route then the current WIP must be removed and replaced by a similar with the Design name
            for tech in self.DESIGN_ROUTE_STEPS_SET:
              if work.get("station", None).startswith(tech):
                toBeRemoved = True
                designsToBeReplaced.append(componentID)
          # the entity is in a buffer if the step_index is no larger than the length of the route
          elif len(route)-1 > step_index:
            '''if the step is OrderDecomposition then the design has concluded its route'''
            if any(station.startswith("OD") for station in route[step_index+1]["stationIdsList"]):
              toBeRemoved = True
            else:
              current_step = route[step_index+1]
              currentStation = current_step["stationIdsList"][0]
          # if it has concluded the last step
          else:
            toBeRemoved = True
          # the entity has concluded it's route; it should be removed from the WIP
          if toBeRemoved:
            wipToBeRemoved.append(componentID)
            # # check if this part is a design and update the flag
            if any(station.startswith("OD") for station in route[-1]["stationIdsList"]):
              designComplete = True
            # # add the part to the completedComponents list if it is not mould or design
            if not any(station.startswith("OD") for station in route[-1]["stationIdsList"]) and\
               not any(station.startswith("E") for station in route[-1]["stationIdsList"]):
              completedComponents.append(componentID)
          # if the entity is still in the system then update the WIP info
          if not componentID in wipToBeRemoved:
            wip[componentID]["station"] = currentStation
            wip[componentID]["sequence"] = current_step["sequence"]
            wip[componentID]["task_id"] = current_step["task_id"]
            if remainingProcessingTime:
              if isinstance(remainingProcessingTime, dict):
                wip[componentID]["remainingProcessingTime"] = remainingProcessingTime
              else:
                wip[componentID]["remainingProcessingTime"] = {"Fixed": {"mean": remainingProcessingTime}}
            # if there is remainingSetupTime
            if remainingSetupTime:
              if isinstance(remainingSetupTime, dict):
                wip[componentID]["remainingSetupTime"] = remainingSetupTime
              else:
                wip[componentID]["remainingSetupTime"] = {"Fixed": {"mean": remainingSetupTime}}
      # if the entity is not recognized within the current WIP then check if it should be created
      # first the flag designComplete and the completedComponents list must be updated 
      for component in orderComponents:
        componentID = component["id"]
        route = component["route"] 
        if not componentID in self.getWIPIds():
          insertWIPitem = [False, None] # first is the flag that shows if the component should be inserted to the WIP, the second one shows which step of it's route should be initiated
          # # if the design is complete
          if designComplete:
            # # if the component is not a mould then put in the second step of its route (the first is OrderDecomposition - it shouldn't be there)
            if not any(station.startswith("E") for station in route[-1]["stationIdsList"]):
              # if there is order decomposition in the route then start at the second step
              if any(station.startswith("OD") for station in route[0]["stationIdsList"]):
                insertWIPitem = [True, 1]
              else:
                insertWIPitem = [True, 0]
          # # if the design is not complete 
          else:
            # # if the component is design then put it at the start of its route (the start of it's route is QCAD - it should be placed there)
            if any(station.startswith("OD") for station in route[-1]["stationIdsList"]):
              insertWIPitem = [True, 0]
          # # if the completed components include all the components (exclude mould and design)
          if len(completedComponents) == len(orderComponents)-2:
            # # if the component is a mould then put it in the first step of it's route (the first step of it's route is Assembly, it should be there)
            if any(station.startswith("E") for station in route[-1]["stationIdsList"]):
              insertWIPitem = [True, 0]
              
          if insertWIPitem[0]:
            if not wip.get(componentID, {}):
              wip[componentID] = {}
            wip[componentID]["station"] = route[insertWIPitem[1]]["stationIdsList"][0]
            wip[componentID]["sequence"] = route[insertWIPitem[1]]["sequence"]
            wip[componentID]["task_id"] = route[insertWIPitem[1]]["task_id"]
    # remove the idle entities
    for entityID in wipToBeRemoved:
      if entityID in designsToBeReplaced:
        wip[entityID+"_D"] = wip[entityID]
      assert wip.pop(entityID, None), "while trying to remove WIP that has concluded it's route, nothing is removed"
  

    return data

if __name__ == '__main__':
    pass
