from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class ReadJSCompleted(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the work-plan from the corresponding spreadsheet
  """
    

  def preprocess(self, data):
    """ inserts the retrieved order components and the related information (routing) to the BOM echelon
    """
    self.data=data
    orders = data["input"]["BOM"].get("productionOrders",{})
    wip = data["input"]["BOM"].get("WIP", {})
    for order in orders:
      components = order.get("componentsList", [])
      for component in components:
        routeConcluded = True
        route = component.get("route", [])
        for index, step in enumerate(route):
          completed = step.get("completed", [])
          '''if the step consists of two sub_steps (Setup - Process) then check if only one of them is concluded'''
          for ind in range(len(completed)):
            if completed[ind] == "No" or completed[ind] == "" or completed[ind] == None:
              routeConcluded = False
              ''''if the index is bigger than 0 (1,2,..) it means that there is not only processing but also setup or other types of operations to be performed. Check if the components is already in the WIP. if not add it to it and keep the operation processing time for the remainingProcessingTime'''
              if ind>=1:
                if not component["id"] in wip.keys():
                  processingTime = step.get("processingTime", {"Fixed":{"meam":0}})
                  # the distribution of the processing time is supposed to be fixed (see ReadJSWorkPlan))
                  processingTime = float(processingTime["Fixed"].get("mean",0))
                  wip[component["id"]] = {
                    "task_id": step["task_id"], 
                    "station": step["technology"],
                    "remainingProcessingTime": processingTime,
                    "sequence": step["sequence"]
                  }
              break
              '''XXX keep in mind that task_id of setup will not correspond to valid task_ids after pre_processing'''
          if not routeConcluded:
            # check the WIP and see if the current part already resides there
            if not component["id"] in wip.keys():
              # if there is a previous task
              if index:
                previousStep = route[index-1]
                wip[component["id"]] = {
                  "task_id": previousStep["task_id"],
                  "station": previousStep["technology"],
                  "remainingProcessingTime": 0,
                  "sequence": previousStep["sequence"]
                }
            break
        if routeConcluded:
          wip[component["id"]] = {
            "task_id": route[-1]["task_id"],
             "station": route[-1]["technology"],
             "remainingProcessingTime": 0,
             "sequence": route[-1]["sequence"]
          }
    return data