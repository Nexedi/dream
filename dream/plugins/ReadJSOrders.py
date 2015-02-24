from copy import copy
import json
import time
import random
import operator
import datetime
import copy

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin

class ReadJSOrders(plugin.InputPreparationPlugin, TimeSupportMixin):
  """ Input preparation
      reads the production orders from the corresponding spreadsheet
  """

  def preprocess(self, data):
    """ inserts the retrieved production orders to the BOM echelon
    """
    strptime = datetime.datetime.strptime
    # read the current date and define dateFormat from it
    try:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d %H:%M')
      data['general']['dateFormat']='%Y/%m/%d %H:%M'
    except ValueError:
      now = strptime(data['general']['currentDate'], '%Y/%m/%d')
      data['general']['dateFormat']='%Y/%m/%d'
    self.initializeTimeSupport(data)
    
    POdata = data["input"].get("production_orders_spreadsheet",[])
    productionOrders = []
    BOM = data["input"].get("BOM",{})
    if not BOM:
      BOM = data["input"]["BOM"] = {}
    data["input"]["BOM"]["productionOrders"] = productionOrders
    if POdata:
      POdata.pop(0)  # pop the column names
      for order in POdata:
        orderID = order[0]
        if not orderID:
          continue
        customer = order[1]
        project = order[2]
        # orderDate = order[3]
        # XXX hardcoded time
        orderDate = self.convertToSimulationTime(strptime("%s %s" % (order[3], "00:00"), '%Y/%m/%d %H:%M'))
        # dueDate = order[4]
        # XXX hardcoded time
        dueDate = self.convertToSimulationTime(strptime("%s %s" % (order[4], "00:00"), '%Y/%m/%d %H:%M'))
        priority = order[5]
        manager = order[6]
        productionOrders.append({
          "_class": "Dream.Order",      # hard coded value for the class
          "id": orderID,
          "name": project,
          "customer": customer,
          "orderDate": orderDate,
          "dueDate": dueDate,
          "priority": priority,
          "manager": manager
        })
    return data