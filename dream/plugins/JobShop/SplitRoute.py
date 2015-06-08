from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy

from dream.plugins import plugin

class SplitRoute(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the data from external data base and splits the routes if the parts described are design and mould
  """
  
  ROUTE_STEPS_SET=set(["ENG", "CAD","CAM","MILL", "MILL-SET","TURN", "DRILL", "QUAL","EDM", "EDM-SET","ASSM", "MAN","INJM", "INJM-MAN", "INJM-SET"])
  DESIGN_ROUTE_STEPS_SET=set(["ENG", "CAD"])
  def preprocess(self, data):
    """ splits the routes of mould parts (design + mould) and update the _class attribute of the entities
    """
    orders = data["input"].get("BOM",{}).get("productionOrders",{})
    for order in orders:
      orderComponents = order.get("componentsList", [])
      componentsToAdd = []
      for index, component in enumerate(orderComponents):
        route = component.get("route", [])
        design_step_list = []
        # for each step of the components route find out if it is of a design route (ENG - CAD) or of mould route (ASSM-INJM). If the route contains none of these technology-types steps then the component is normal
        routeList = copy.deepcopy(route)
        i = 0
        # figure out which steps are design steps
        for step in routeList:
          stepTechnology = step.get('technology',[])
          assert stepTechnology in self.ROUTE_STEPS_SET, 'the technology provided does not exist'
          if stepTechnology in self.DESIGN_ROUTE_STEPS_SET:
            design_step_list.append(step)
            route.pop(i)
          else:
            i+=1
        # if the current entity is a mold-design then create the design and update the _class attribute of the mold
        if design_step_list:
          design = {"name": component.get("name","")+"_Design",
                    "id": component.get("id","")+"_D",
                    "quantity": component.get("quantity", 1),
                    "route": design_step_list,
                    "_class": "Dream.OrderDesign"}
          componentsToAdd.append(design)
          """the current component is a mold"""
          component["_class"] = "Dream.Mould" # XXX hard-coded value
        # otherwise we have a normal component, update the _class attribute accordingly
        else:
          component["_class"] = "Dream.OrderComponent" # XXX hard-coded value
      for design in componentsToAdd:
        orderComponents.append(design)
    return data

if __name__ == '__main__':
    pass