from copy import copy
import json
import time
import random
import operator
import StringIO
import xlrd

from dream.plugins import plugin

class DefaultTabularExit(plugin.OutputPreparationPlugin):
  """ Output the exit stats in a tab
  """

  def postprocess(self, data):
    print 'DefaultTabularExit'  
    print data['result']['result_list']
#     data['result']['result_list'].append({
#         "key": "tabular results", 
#         "elementList": [], 
#         'view_tabular_results':[['a','b'],[1,2]]}
#     )
    data['result']['result_list'][0]['exit_output'] = [['a','b'],[1,2]] 
    print data['result']['result_list']
    return data