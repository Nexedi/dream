from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy
import routeQuery

from dream.plugins import plugin

class ReadJSOrders(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the production orders from the corresponding spreadsheet
  """

  def preprocess(self, data):
    """ inserts the retrieved production orders to the BOM echelon
    """
	  POdata = data["input"]["production_orders_spreadsheet"]
    productionOrders = []
    data["input"]["BOM"]["orders"] = productionOrders
    if POdata:
      POdata.pop(0)  # pop the column names
      for order in POdata:
        orderID = POdata[0]
        if not orderID:
          continue
        customer = POdata[1]
        project = POdata[2]
        orderDate = POdata[3]
        dueDate = POdata[4]
        manager = POdata[5]
        productionOrders.append({
          "orderID": orderID,
          "orderName": project,
          "customer": customer,
          "orderDate": orderDate,
          "dueDate": dueDate,
          "manager": manager
        })
	
    return data