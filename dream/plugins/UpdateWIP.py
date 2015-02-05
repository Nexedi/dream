from copy import copy

from dream.plugins import plugin
import datetime
# XXX HARDCODED
MACHINE_TYPE_SET = set(["Dream.MachineJobShop", "Dream.MouldAssembly"]) 
class UpdateWIP(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the data from external data base and updates the WIP
  """
  
  def getWIPIds(self):
    """"""
    wipIDs = []
    for key in self.data["input"]["BOM"].get("WIP", {}).keys()
      wipIDs.append(key)
    return wipIDs

  def preprocess(self, data):
    """ updates the Work in Process according to what is provided by the BOM, i.e. if a design just exited the last step of it's sequence
    """
    currentTime = datetime.datetime.now().time()
    self.data = copy(data)
    orders = self.data["input"]["BOM"]["orders"]
    nodes = self.data["graph"]["node"]
    wip = self.data["input"]["BOM"].get("WIP", {})
  
    """ get the tasks that are in the WIP, and place those that are not in the WIP in the corresponding stations. Consider the parts that have concluded their routes, or the components that are not created yet.
    All the components defined by the corresponding orders should be examined
    """
    wipToBeRemoved = []
    # # check all the orders
    for order in orders:
      orderComponents = order.get("componentsList", [])
      designComplete = False          # flag to inform if the design is concluded
      completedComponents = []        # list to hold the componentIDs that are concluded
      # # find all the components
      for component in orderComponents:
        componentID = component["componentID"]
        route = component["route"] 
        # # figure out if they are defined in the WIP
        if componentID in self.getWIPIds():
          work = wip[componentID]
          # # extract WIP information
          workStation = work["station"]
          entryTime = float(work.pop("entry"),0)
          exitTime = float(work.pop("exit", 0))
          task_id = work["task_id"]
          assert len(route)>0, "the OrderComponent must have a route defined with length more than 0"
          assert task_id, "there must be a task_id defined for the OrderComponent in the WIP"
          # # get the step identified by task_id, hold the step_index to see if the entity's route is concluded
          for step_index, step in enumerate(route):
            if step["task_id"] == task_id:
              last_step = step
              break
          # # check if the entity has left the station
          # the entity is a machine if there is no exitTime
          if not exitTime:
            # # calculate remaining processing time
            remainingProcessingTime = currentTime - entryTime
            currentStation = workStation
            current_step = last_step
          # the entity is in a buffer if the step_index is no larger than the length of the route
          elif len(route)-1>=step_index:
            current_step = route[step_index+1]
            currentStation = current_step["stationIdsList"][0]
          # the entity has concluded it's route; it should be removed from the WIP
          else:
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
            wip["componentID"]["station"] = currentStation
            wip["componentID"]["sequence"] = current_step["sequence"]
            wip["componentID"]["task_id"] = current_step["task_id"]
            if not exitTime:
              wip["componentID"]["remainingProcessingTime"] = {"Fixed": {"mean": remainingProcessingTime}}
      # if the entity is not recognized within the current WIP then check if it should be created
      # first the flag designComplete and the completedComponents list must be updated 
      for component in orderComponents:
        componentID = component["componentID"]
        route = component["route"] 
        if not componentID in self.getWIPIds():
          insertWIPitem = False
          # # if the design is complete
          if designComplete:
            # # if the component is not a mould then put in the first step of its route
            if not any(station.startswith("E") for station in route[-1]["stationIdsList"]):
              insertWIPitem = True
          # # if the design is not complete 
          else:
            # # if the component is design then put it at the start of its route
            if any(station.startswith("OD") for station in route[0]["stationIdsList"]):
              insertWIPitem = True
          # # if the completed components include all the components (exclude mould and design)
          if len(completedComponents) == len(orderComponents)-2:
            # # if the component is a mould then put it in the first step of it's route
            if any(station.startswith("E") for station in route[-1]["stationIdsList"]):
              insertWIPitem = True
              
          if insertWIPitem:    
            wip["componentID"]["station"] = route[0]["stationIdsList"][0]
            wip["componentID"]["sequence"] = route[0]["sequence"]
            wip["componentID"]["task_id"] = route[0]["task_id"]
    # remove the idle entities
    for entityID in wipToBeRemoved:
      assert wip.pop(entityID, None), "while trying to remove WIP that has concluded it's route, nothing is removed"
  

      
    return data

if __name__ == '__main__':
    pass