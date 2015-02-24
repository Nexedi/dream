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
          completed = step.get("completed", "No")
          if completed == "No" or completed == "":
            routeConcluded = False
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
            "task_id": step["task_id"],
             "station": step["technology"],
             "remainingProcessingTime": 0,
             "sequence": step["sequence"]
          }
    return data