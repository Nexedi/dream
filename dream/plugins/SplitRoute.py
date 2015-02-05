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
    """ splits the routes of mould parts (design + mould)
    """
    orders = data["input"]["BOM"]["orders"]
    stations = data["input"]["BOM"]["stations"]
    for order in orders:
      orderComponents = order.get("componentsList", [])
      componentsToAdd = []
      for index, component in enumerate(orderComponents):
        route = component.get("route", [])
        design_step_list = []
        # for each step of the components route find out if it is of a design route (ENG - CAD) or of mould route (ASSM-INJM). If the route contains none of these technology-types steps then the component is normal
        routeList = copy.deepcopy(route)
        i = 0
        for step in routeList:
          stepTechnology = step.get('technology',[])
          assert stepTechnology in ROUTE_STEPS_SET, 'the technology provided does not exist'
          if stepTechnology in DESIGN_ROUTE_STEPS_SET:
            design_step_list.append(step)
            route.pop(i)
          else:
            i+=1
        if design_step_list:
          design = {"componentName": component.get("componentName","")+"_Design",
                    "componentID": component.get("componentID","")+"_D",
                    "quantity": component.get("quantity", 1),
                    "route": design_step_list}
          componentsToAdd.append(design)
      for design in componentsToAdd:
        orderComponents.append(design)
    return data

if __name__ == '__main__':
    pass