from copy import copy
import json
import time
import random
import operator
import StringIO
import xlrd

from dream.plugins import plugin

class ReadDemandPlannerExcelInput(plugin.OutputPreparationPlugin):
  """ Example on how to read an excel spreadsheet 
  """

  def preprocess(self, data):
    """ Example showing how to read an attached file
    """
    # Attachement is encoded in data uri, ie data:application/excel;base64,***
    data_uri_encoded_input_data = data['input'].get(self.configuration_dict['input_id'], {})
    if data_uri_encoded_input_data:
        mime_type, attachement_data = data_uri_encoded_input_data[len('data:'):].split(';base64,', 1)
        attachement_data = attachement_data.decode('base64')
        
        workbook = xlrd.open_workbook(file_contents=attachement_data)
    
        print "This spreadsheet contains sheets:", workbook.sheet_names()

    #raise ValueError(workbook.sheet_names())
    
    return data