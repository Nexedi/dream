from copy import copy
import json
import time
import random
import operator
from datetime import datetime
import copy
from datetime import datetime

from dream.plugins import plugin

"""{"CAD": ["ENG", "CAD"],
    "CAM": ["CAM"],
    "MILL": ["MILL"],
    "TURN": ["TURN"],
    "DRILL": ["DRILL"],
    "EDM": ["EDM"],
    "WORK": ["QUAL", "ASSM", "MAN"],
    "INJM": ["INJM"]}"""
# list of the available skilss
AVAILABLE_SKILLS_LIST = ["ENG", "CAD", "CAM", "MILL", "MILL-SET", "TURN", "DRILL", "EDM", "EDM-SET", "ASSM", "MAN", "INJM", "INJM-MAN", "INJM-SET", "QUAL"]
# dict of the different operations sets (load/ setup/ processing) as defined in the GUI
SKILLS_DICT = {
  "load": [],
  "process": ["ENG", "CAD", "CAM", "MILL", "TURN", "DRILL", "EDM", "ASSM", "MAN", "INJM", "INJM-MAN", "QUAL"],
  "setup": ["MILL-SET", "EDM-SET", "INJM-SET"]
}

class ReadJSSkills(plugin.InputPreparationPlugin):
  """ Input preparation 
      reads the operators and their skills from the spreadsheet and adds them to the model
  """

  def preprocess(self, data):
    """ Read the operator and the tasks they can perform and adds them to them to the graph. 
    """
    PBData=data['input'].get('operator_skills_spreadsheet', None)
    node=data['graph']['node']
    if PBData:
      PBData.pop(0)  # pop the column names
      for PBitem in PBData:
        PBId=PBitem[0]
        if PBId:
          PBId = PBId.split("-")[0]
        # in case there is no id, do not process the element
        if not PBId:
          continue
        skills=PBitem[1].replace(" ","").split(';')
        if len(skills)==1:
          skills = PBitem[1].replace(" ","").split(',')
        skillDict = {
          "load": [],
          "process": [],
          "setup": []
        }
        for skill in skills:
          for operation, availableSkills in SKILLS_DICT.iteritems():
            if skill in availableSkills:
              skillDict[operation].append(skill)
        # if EDM-SET in in skillDict['setup'] then add EDM to skillDict['process']
        if 'EDM-SET' in skillDict['setup']:
          skillDict['process'].append('EDM')
        
        node[PBId]={
          "_class": "Dream.Operator",
          "capacity": 1,
          "name":PBitem[0],
          "skillDict":skillDict,
          "ouputSchedule" : 1
        }
    return data

