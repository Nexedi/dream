from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class ChangeDecimalOperators(plugin.InputPreparationPlugin):
  """ Input preparation
      if times are given with ',' as decimal operator this plugin replaces them to '.'
  """

  def preprocess(self, data):
    """ replace ',' to '.' in the processing times of workplan spreadsheet
    """
    self.data = copy(data)
    orders = self.data["input"].get("BOM",{}).get("productionOrders",{})
    WPdata = data["input"].get("workplan_spreadsheet",[])
    # processing time is in column 7. But read it if this changes
    i=0
    procTimeColumn=7
    for record in WPdata[0]:
        if "Processing" in record:
            procTimeColumn=i
            break
        i+=1
    
    # replace ',' to '.' for every entry
    for row in WPdata:
        if row[procTimeColumn]:
            row[procTimeColumn]=str(row[procTimeColumn])
            row[procTimeColumn]=row[procTimeColumn].replace(',','.')
    return data

if __name__ == '__main__':
    pass