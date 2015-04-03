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
    # return the negative value since they are ranked this way. XXX discuss this
    return -unitsThroughput

  # creates the collated scenarios, i.e. the list 
  # of options collated into a dictionary for ease of referencing in ManPy
  def createCollatedScenarios(self,data):
    collated = dict()
    weightData=data['input'].get('ACO_weights_spreadsheet', None)
    for i in range(1,7):
        minValue=weightData[1][i]
        maxValue=weightData[2][i]
        stepValue=weightData[3][i]
        staticValue=weightData[4][i]
        if staticValue:
            collated[str(i)]=[float(staticValue)]
        else:
            collated[str(i)]=[]
            value=float(minValue)
            while 1:
                collated[str(i)].append(round(float(value),2))
                value+=float(stepValue)
                if value>maxValue:
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

  def run(self, data):
    ant_data = copy(data)
    # below provisional values, to be updated (should the user set those?)
    data['general']['numberOfSolutions']=1
    data["general"]["numberOfGenerations"]=1
    data["general"]["numberOfAntsPerGenerations"]=3
    ACO.run(self, data)
    return data