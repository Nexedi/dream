from dream.plugins import plugin
from pprint import pformat
from copy import copy
import json
import time
import random
import operator
import xmlrpclib

from dream.simulation.Queue import Queue
from dream.simulation.Operator import Operator
from dream.simulation.Globals import getClassFromName
from dream.plugins.ACO import ACO

class BatchesACO(ACO):

  def _calculateAntScore(self, ant):
    """Calculate the score of this ant.
    """
    result, = ant['result']['result_list']  #read the result as JSON
    #loop through the elements 
    for element in result['elementList']:
        element_family = element.get('family', None)
        #id the class is Exit get the unitsThroughput
        if element_family == 'Exit':
            unitsThroughput=element['results'].get('unitsThroughput',None)
            if unitsThroughput:
                unitsThroughput=unitsThroughput[0]
            if not unitsThroughput:
                unitsThroughput=element['results']['throughput'][0]
            # below checking the predecessors of exit. If a predecessor is reassembly and 
            # has WIP add this also in the throughput
            for objectId in self.getPredecessors(ant['input'], element['id']):
                for record in result['elementList']:
                    if record['id']==objectId and 'Reassembly' in record['_class']:
                        unitsThroughput+=record['results'].get('final_WIP',[0])[0]
    # return the negative value since they are ranked this way. XXX discuss this
    return -unitsThroughput

  # creates the collated scenarios, i.e. the list 
  # of options collated into a dictionary for ease of referencing in ManPy
  def createCollatedScenarios(self,data):
    collated = dict()
    # fill sub-line deactivated (default to zero)
    collated["4"]=[0.0]
    weightData=data['input'].get('ACO_weights_spreadsheet', None)
    for i in range(1,6):
        # to deactivate fill sub-line the index of 4 is surpassed
        if i<4:
            index=str(i)
        else:
            index=str(i+1)
        
        minValue=weightData[1][i]
        maxValue=weightData[2][i]
        stepValue=weightData[3][i]
        staticValue=weightData[4][i]
        if staticValue:
            collated[index]=[float(staticValue)]
        else:
            collated[index]=[]
            value=float(minValue)
            while 1:
                collated[index].append(round(float(value),2))
                value+=float(stepValue)
                if value>float(maxValue):
                    break
    return collated    

  # creates the ant scenario based on what ACO randomly selected
  def createAntData(self,data,ant): 
    # set scheduling rule on queues based on ant data
    ant_data = copy(data)
    weightFactors=[1,1,1,1,1,1]
    for k, v in ant.items():
        weightFactors[int(k)-1]=v
    for node_id, node in ant_data["graph"]["node"].iteritems():
        if node['_class']=="dream.simulation.SkilledOperatorRouter.SkilledRouter":
            node['weightFactors']=weightFactors
    return ant_data

  # checks if there are operators in the model. If not it is tactical model so no optimization, one scenario should be run
  def checkIfThereAreOperators(self,data):
    for node_id,node in data['graph']['node'].iteritems():
      if 'Operator' in node['_class']:
        return True
    return False

  def run(self, data):
    ant_data = copy(data)
    # if there are no operators act as default execution plugin
    if not self.checkIfThereAreOperators(data):
      data["result"]["result_list"] = self.runOneScenario(data)['result']['result_list']
      data["result"]["result_list"][-1]["score"] = ''
      data["result"]["result_list"][-1]["key"] = "Go To Results Page"
      return data
    # else run ACO
    data['general']['numberOfSolutions']=1  # default of 1 solution for this instance
    data["general"]["distributorURL"]=None  # no distributor currently, to be added in the GUI
    # use multiprocessing in the PC. This can be an option, but default for now
    import multiprocessing                  
    data["general"]["multiprocessorCount"] = None # multiprocessing.cpu_count()-1 or 1
    ACO.run(self, data)
    data["result"]["result_list"][-1]["score"] = ''
    data["result"]["result_list"][-1]["key"] = "Go To Results Page"
    return data