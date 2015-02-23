from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class ReadJSOrders(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the production orders from the corresponding spreadsheet
  """

  def preprocess(self, data):
    """ inserts the retrieved production orders to the BOM echelon
    """
    POdata = data["input"].get("production_orders_spreadsheet",[])
    productionOrders = []
    BOM = data["input"].get("BOM",{})
    if not BOM:
      BOM = data["input"]["BOM"] = {}
    data["input"]["BOM"]["orders"] = productionOrders
    if POdata:
      POdata.pop(0)  # pop the column names
      for order in POdata:
        orderID = order[0]
        if not orderID:
          continue
        customer = order[1]
        project = order[2]
        orderDate = order[3]
        dueDate = order[4]
        priority = order[5]
        manager = order[6]
        productionOrders.append({
          "orderID": orderID,
          "orderName": project,
          "customer": customer,
          "orderDate": orderDate,
          "dueDate": dueDate,
          "priority": priority,
          "manager": manager
        })
	
    return data