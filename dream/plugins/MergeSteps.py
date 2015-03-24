from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class MergeSteps(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the data from external data base and merges the route steps that constitute on technology step
  """

  def preprocess(self, data):
    """ merge the steps that constitute one single technology step
    """
    orders = data["input"].get("BOM", {}).get("productionOrders", {})
    # for all the orders 
    for order in orders:
      orderComponents = order.get("componentsList", [])
      # for each component of the order
      for component in orderComponents:
        route = component.get("route", [])
        updatedRoute = []
        technologySequence = []
        for index, step in enumerate(route):
          technology = step["technology"]
          technology = technology.split("-")[0]
          # XXX loadType is always manual for this pilot
          step["operationType"] = {"Load" : 1}
          '''processingType + operator for processing'''
          # if the operator is defined as automatic or
          # XXX if the technology is EDM
          # then set the processing type as automatic and remove the operator property
          if step["operator"] == "Automatic"\
              or step["technology"] == "EDM":
            step["operationType"]["Processing"] = 0
            step.pop("operator")
          else:
            step["operationType"]["Processing"] = 1
            tempOperator = copy.deepcopy(step["operator"])
            step["operator"] = {}
            step["operator"]["processing"] = [tempOperator]
            step["operator"]["load"] = [tempOperator]
          '''find out if there is there is any previous step to merge with''' 
          idxToMerge = None
          if technologySequence:
            if technology == technologySequence[-1]:
              if len(route[index-1]["technology"].split("-")):
                if route[index-1]["technology"].split("-")[-1]=="SET":
                  idxToMerge = index-1
                else:
                  idxToMerge = None
          '''if we must merge two steps'''
          if idxToMerge != None:
            # remove the previous step from the updatedRoute and technologySequence
            updatedRoute.pop(-1)
            technologySequence.pop(-1)
            stepToMerge = route[idxToMerge]
            # parts needed
            step["requiredParts"] = stepToMerge["requiredParts"]
            # technology
            step["technology"] = technology
            # setupTime
            if stepToMerge["processingTime"]:
              step["setupTime"] = stepToMerge["processingTime"]
            # setupType + operator for setup
            if stepToMerge["operator"] == "Automatic":
              step["operationType"]["Setup"] = 0
            else:
              step["operationType"]["Setup"] = 1
              try:
                tempOperator = copy.deepcopy(step["operator"])
              except:
                tempOperator = None
              step["operator"] = {}
              step["operator"]["setup"] = route[idxToMerge]["operator"]["processing"]
              step["operator"]["load"] = route[idxToMerge]["operator"]["load"]
              if tempOperator:
                step["operator"]["processing"] = tempOperator["processing"]
            '''find out if the setup is completed, but no processing is performed yet; in that case the part should be placed in WIP (though the route is not split yet) '''
            step["completed"] = [stepToMerge["completed"][0], step["completed"]]
          else:
            '''make the completed attribute a list '''
            step["completed"] = [step["completed"]]
            
          technologySequence.append(technology)
          # append the (updated) step to the temporary route 
          updatedRoute.append(step)
        # update the route of the step
        component["route"] = updatedRoute
    return data

if __name__ == '__main__':
    pass