from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class ReadJSWorkPlan(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the work-plan from the corresponding spreadsheet
  """
    
  def findEntityByID(self, ID):
    """search within the BOM and find the entity (order or component)"""
    orders = self.data["input"]["BOM"].get("productionOrders", {})
    for order in orders:
      # check if the id corresponds to an order
      if ID == order["id"]:
        return order
      components = order.get("componentsList", [])
      for component in components:
        if ID == component["id"]:
          return component
    return {}

  def preprocess(self, data):
    """ inserts the retrieved order components and the related information (routing) to the BOM echelon
    """
    self.data=data
    WPdata = data["input"].get("workplan_spreadsheet",[])
    if WPdata:
      WPdata.pop(0)  # pop the column names
      for line in WPdata:
        orderID = line[1]
        order = self.findEntityByID(orderID)
        # if the order is not defined then skip this part
        if not order:
          continue
        partID = line[0]
        part = self.findEntityByID(partID)
        # if there is no such part in the BOM then create it
        if not part:
          partName = line[2]
          components = order.get("componentsList",[])
          # the part is brand new
          part = {
            "id": partID,
            "name": partID,
            "componentType": partName
          }
          components.append(part)
          order["componentsList"] = components
        # update  the route of the component
        route = part.get("route", [])
        task_id = line[-2]
        sequence = line[4]
        processingTime = float(line[-5])
        operator = line[5].replace(" ","").split("-")[0]
        requiredParts = line[-4]
        # if there are requested parts then split them
        if requiredParts:
          requiredParts = requiredParts.replace(" ","").split(';')
        else:
          requiredParts = []
        technology = line[3]
        quantity = int(line[6])
        completed = line[-1]
        # append the current step to the route of the part
        route.append({
          "task_id": task_id,
          "sequence": sequence,
          "processingTime": {"Fixed":{"mean":processingTime*quantity}},
          "operator": operator,
          "requiredParts": requiredParts,
          "technology": technology,
          "quantity": quantity,
          "completed": completed
        })
        part["route"] = route
    return data