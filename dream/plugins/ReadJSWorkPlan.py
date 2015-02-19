from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy
import routeQuery

from dream.plugins import plugin

class ReadJSWorkPlan(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the work-plan from the corresponding spreadsheet
  """
    
  def findEntityByID(self, ID):
    """search within the BOM and find the entity (order or component)"""
    orders = self.data["input"]["BOM"].get("orders", {})
    for order in orders:
      # check if the id corresponds to an order
      if ID == order["orderID"]:
        return order
      components = order.get("componentsList", [])
      for component in components:
        if ID == component["componentID"]:
          return component
    return {}

  def preprocess(self, data):
    """ inserts the retrieved order components and the related information (routing) to the BOM echelon
    """
    self.data=data
	  WPdata = data["input"]["workplan_spreadsheet"]
    orders = data["input"]["BOM"].get("orders",{})
    if WPdata:
      WPdata.pop(0)  # pop the column names
      for line in WPdata:
        orderID = WPdata[1]
        order = self.findEntityByID(orderID)
        # if the order is not defined then skip this part
        if not order:
          continue
        partID = WPdata[0]
        part = self.findEntityByID(partID)
        # if there is no such part in the BOM then create it
        if not part:
          partName = WPdata[2]
          components = order.get("componentsList",[])
          components.append({
            "componentID": partID,
            "componentName": partName
          })
          order["componentsList"] = components
        # update  the route of the component
        route = part.get("route", [])
        task_id = WPdata[-1]
        sequence = WPdata[4]
        processingTime = WPdata[-4]
        operator = WPdata[5]
        partsneeded = WPdata[-2].replace(" ","").split(',')
        technology = WPdata[3]
        quantity = WPdata[6]
        route.append({
          "task_id": task_id,
          "sequence": sequence,
          "processingTime": {"fixed":{"mean":processingTime}},
          "operator": operator,
          "partsneeded": partsneeded,
          "technology": technology,
          "quantity": quantity
        })
        part["route"] = route

	
    return data