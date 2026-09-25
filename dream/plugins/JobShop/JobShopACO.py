from pprint import pformat
from copy import copy, deepcopy
import time

from dream.simulation.Queue import Queue
from dream.simulation.Operator import Operator
from dream.simulation.Globals import getClassFromName
from dream.plugins.ACO import ACO

class JobShopACO(ACO):
  def _calculateAntScore(self, ant):
    """Calculate the score of this ant.
    """
    totalDelay=0    #set the total delay to 0
    result, = ant['result']['result_list']  #read the result as JSON
    #loop through the elements
    throughput=0
    for element in result['elementList']:
        # find the throughput of the solution
        element_family = element.get('family', None)
        if element_family=='Exit':
            results=element['results']
            throughput=results.get('throughput', "0")[0]
        
        #id the class is Job
        if element_family == 'Job':
            results=element['results']
            delay = float(results.get('delay', "0"))
            # A negative delay would mean we are ahead of schedule. This
            # should not be considered better than being on time.
            totalDelay += max(delay, 0)
    production_orders_spreadsheet=ant['input']['input'].get('production_orders_spreadsheet',[])
    # find the number of orders 
    numberOfOrders=0
    for row in production_orders_spreadsheet:
        if row[0] and (not row[0]=="Order Id"):
            numberOfOrders+=1
            
    # if in this solution not all orders finished give the total delay as infinite so that it want be considered positive
    if not throughput==numberOfOrders:
        totalDelay=float('inf')
    
    return totalDelay

  # creates the collated scenarios, i.e. the list 
  # of options collated into a dictionary for ease of referencing in ManPy
  def createCollatedScenarios(self,data):
    collated = dict()
    for node_id, node in data['graph']['node'].items():
      node_class = getClassFromName(node['_class'])
      if issubclass(node_class, Queue) or issubclass(node_class, Operator):
        collated[node_id] = list(node_class.getSupportedSchedulingRules())
    return collated    

  # creates the ant scenario based on what ACO randomly selected
  def createAntData(self,data,ant): 
    # set scheduling rule on queues based on ant data
    ant_data = copy(data)
    for k, v in ant.items():
        ant_data["graph"]["node"][k]['schedulingRule'] = v
    return ant_data
