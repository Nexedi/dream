from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class ReadSkilledOperators(plugin.InputPreparationPlugin):
  """ Input prepration 
      reads the operators and their skills from the spreadsheet and adds them to the model
  """

  def preprocess(self, data):
    """ Set the WIP in queue from spreadsheet data.
    """
    PBData=data['input'].get('operator_skill_spreadsheet', None)
    node=data['graph']['node']
    operatorPresent = False
    if PBData:
        PBData.pop(0)  # pop the column names
        for PBitem in PBData:
            PBId=PBitem[0]
            # in case there is no id, do not process the element
            if not PBId:
                continue
            skills=PBitem[1].split(',')
            skills = filter(bool, skills) 
            # if element has spaces in beginning or in end remove them
            skills=self.stripStringsOfList(skills)
            
            newSkills=[]
            for n_id,n in node.iteritems():
                technology=n.get('technology',None)
                if technology in skills and n_id not in newSkills:    
                    newSkills.append(n_id)      
            # this so that models without technology also work          
            if not newSkills:
                newSkills=skills                                               
            node[PBId]={
              "_class": "Dream.Operator",
              "capacity": 1,
              "name":PBId,
              "skills":newSkills,
              "ouputSchedule" : 1
            }
            operatorPresent = True
                  
        # if there is at least one operator
        if operatorPresent:
            nodes=data['graph']['node']
            for station_id,station in nodes.iteritems():
                # set the operation type of all machines to MT-Load-Processing
                if station['_class'] in ['Dream.BatchScrapMachine','Dream.BatchScrapMachineBeforeReassembly',
                                      'Dream.BatchScrapMachineAfterDecompose','Dream.M3']:
                    station["operationType"]="MT-Load-Processing"
            # add EventGenerator for the allocation every 10 minutes
            node['EV123454321']={   #(random id)
                      "name": "Allocator", 
                      "argumentDict": "{}", 
                      "interval": data['general'].get('allocationInterval',40), 
                      "stop": -1, 
                      "id": "EV123454321", 
                      "start": 0, 
                      "interruptions": {}, 
                      "_class": "Dream.EventGenerator", 
                      "method": "Dream.ManPyObject.requestAllocation"
              }
            # add EventGenerator for the allocation every 10 minutes
            node['SkilledRouter01']={   #(random id)
                    "_class": "dream.simulation.SkilledOperatorRouter.SkilledRouter", 
                    "name": "SkilledRouter01",
                    "outputSolutions":1,
                    "twoPhaseSearch": int(data['general'].get('twoPhaseSearch',0)), 
                    "checkCondition":1    
              }
    return data

