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
    orders = data["BOM"]['orders']
	
	for order in orders:
		orderComponents = order.get("componentsList", [])
		for component in orderComponents:
			route = component.get("route", [])
			updatedRoute = []
			technologySequence = []
			idxToMerge = None
			for index, step in enumerate(route):
				technology = step["technology"]
				technology = technology.split("-")[0]
				# loadType is always manual for this pilot
				step["operationType"] = {"load" : "Manual"}
				step["operator"] = {}
				# processingType + operator for processing
				if step["operator"] == "Automatic"
					step["operationType"]["processing"] = "Automatic"
				else:
					step["operationType"]["processing"] = "Manual"
					tempOperator = copy.deepcopy(step["operator"])
					step["operator"]["processing"] = [tempOperator],
					step["operator"]["load"] = [tempOperator]}
				# find out if there is there is any previous step to merge with
				if technology == technologySequence[-1]:
					if len(route[index-1]["technology"].split("-")):
						if route[index-1]["technology"].split("-")[-1]=="SET":
							idxToMerge = index-1
						else:
							idxToMerge = None
				# if we must merge two steps
				if idxToMerge != None:
					# remove the previous step from the updatedRoute and technologySequence
					updatedRoute.pop(-1)
					technologySequence.pop(-1)
					stepToMerge = route[idxToMerge]
					# parts needed
					step["parts_needed"] = route[idxToMerge]["parts_needed"]
					# technology
					step["technology"] = technology
					# setupTime
					if route[idxToMerge]["processingTime"]:
						step["setupTime"] = route[idxToMerge]["processingTime"]
					# setupType + operator for setup
					if route[idxToMerge]["operator"] == "Automatic"
						step["operationType"]["setup"] = "Automatic"
					else:
						step["operationType"]["setup"] = "Manual"
						step["operator"]["setup"] = route[idxToMerge]["operator"]
						step["operator"]["load"] = route[idxToMerge]["operator"]
				technologySequence.append(techonology)
				# append the (updated) step to the temporary route 
				updatedRoute.append(step)
			# update the route of the step
			component["route"] = updatedRoute
    return data

if __name__ == '__main__':
    pass