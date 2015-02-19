from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy
import routeQuery
from datetime import datetime

from dream.plugins import plugin

class ReadJSSkills(plugin.InputPreparationPlugin):
  """ Input preparation 
      reads the operators and their skills from the spreadsheet and adds them to the model
  """

  def preprocess(self, data):
    """ Read the operator and the tasks they can perform and adds them to them to the graph. 
    """
    PBData=data['input'].get('operator_skill_spreadsheet', None)
    node=data['graph']['node']
    if PBData:
        PBData.pop(0)  # pop the column names
        for PBitem in PBData:
            PBId=PBitem[0]
            PBId = PBId.split("-")[0]
            # in case there is no id, do not process the element
            if not PBId:
                continue
            skills=PBitem[1].replace(" ","").split(';')
            node[PBId]={
              "_class": "Dream.Operator",
              "capacity": 1,
              "name":PBId,
              "skills":skills,
              "ouputSchedule" : 1
            }
        
    return data

