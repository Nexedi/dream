from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin
from dream.plugins.TimeSupport import TimeSupportMixin
from dream.plugins.ReadShiftFromSpreadsheet import ReadShiftFromSpreadsheet

class BatchesShift(ReadShiftFromSpreadsheet):
  """ Input prepration 
      extends standard ReadShiftFromSpreadsheet to accept 'All' to define all stations
      sets also the attributes of shifts to objects
      XXX to be extended to operators
  """

  def preprocess(self, data):
    nodes=data['graph']['node']
    machineshiftData=data['input'].get('machine_shift_spreadsheet', None)
    operatorshiftData=data['input'].get('operator_shift_spreadsheet', None)
    maxSimTime=data['general']['maxSimTime']
     
    # create a string with all station ids separated by commas
    allString=''
    for node_id, node in nodes.iteritems():
        if node['_class'].startswith('Dream.BatchScrapMachine') or node['_class']=='Dream.M3':
            allString+=node_id
            allString+=','
    # if in machine shift there is a 
    for element in machineshiftData:
        if element[1] in ['ALL','All','all']:
            element[1]=allString   
            
    # create a string with all operator ids separated by commas
    allString=''
    for node_id, node in nodes.iteritems():
        if node['_class']=='Dream.Operator':
            allString+=node_id
            allString+=','

    # if in machine shift there is a 
    for element in operatorshiftData:
        if element[1] in ['ALL','All','all']:
            element[1]=allString             
    
    # run the standard shift plugin  
    data=ReadShiftFromSpreadsheet.preprocess(self, data)

    # set attributes to shifts
    for node_id, node in nodes.iteritems():
        if "BatchScrapMachine" in node['_class'] or "M3" in node['_class'] or node['_class']=="Dream.Operator": 
            shiftExists=False
            interruptions=node.get('interruptions',None)
            if interruptions:
                shift=interruptions.get('shift',None)
                if shift:
                    interruptions['shift']['thresholdTimeIsOnShift']=0
                    interruptions['shift']['receiveBeforeEndThreshold']=7
                    interruptions['shift']['endUnfinished']=1
                    shiftExists=True
            # if element has no shift defined in the spreadsheet it needs to be off-shift. For this we declare a dummy
            # shift that is on-shift only after the completion of simulation
            if not shiftExists:
                node['interruptions']=node.get('interruptions',{})
                node['interruptions']['shift']={}
                node['interruptions']['shift']['shiftPattern']=[[maxSimTime+1,maxSimTime+2]]      
    return data
