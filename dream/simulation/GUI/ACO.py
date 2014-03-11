from copy import copy
import json
import time
import random
import operator

from dream.simulation.GUI.Default import Simulation as DefaultSimulation
from dream.simulation.Queue import Queue
from dream.simulation.Globals import getClassFromName

class Simulation(DefaultSimulation):

  def getConfigurationDict(self):
    conf = DefaultSimulation.getConfigurationDict(self)
    conf["Dream-Configuration"]["property_list"].append(
        { "id": "numberOfGenerations",
          "type": "number",
          "name": "Number of generations",
          "_class": "Dream.Property",
          "_default": 10} )
    conf["Dream-Configuration"]["property_list"].append(
        { "id": "numberOfAntsPerGenerations",
          "type": "number",
          "name": "Number of ants per generation",
          "_class": "Dream.Property",
          "_default": 20} )
    conf["Dream-Configuration"]["property_list"].append(
        { "id": "numberOfSolutions",
          "type": "number",
          "name": "Number of solutions",
          "_class": "Dream.Property",
          "_default": 4} )
    return conf

  def _preprocess(self, data):
    """Override in subclass to preprocess data.
    """
    return data

  def _calculateAntScore(self, ant):
    """Calculate the score of this ant.
    """
    totalDelay=0    #set the total delay to 0
    jsonData=ant['result']  #read the result as JSON
    elementList = jsonData['elementList']   #find the route of JSON
    #loop through the elements
    for element in elementList:
        elementClass=element['_class']  #get the class
        #id the class is Job
        if elementClass=='Dream.Job':
            results=element['results']
            delay = float(results.get('delay', "0"))
            # A negative delay would mean we are ahead of schedule. This
            # should not be considered better than being on time.
            totalDelay += max(delay, 0)
    return totalDelay


  def run(self, data):
    data = self._preprocess(data)

    tested_ants = set()
    start=time.time()         # start counting execution time

    # the list of options collated into a dictionary for ease of referencing in
    # ManPy
    collated = dict()
    for node_id, node in data['nodes'].items():
      node_class = getClassFromName(node['_class'])
      if issubclass(node_class, Queue):
        collated[node_id] = list(node_class.getSupportedSchedulingRules())

    max_results = data['general']['numberOfSolutions']

    ants = [] #list of ants for keeping track of their performance

    # Number of times new ants are to be created, i.e. number of generations (a
    # generation can have more than 1 ant)
    for i in range(data["general"]["numberOfGenerations"]):
        # number of ants created per generation
        for j in range(data["general"]["numberOfAntsPerGenerations"]):
            # an ant dictionary to contain rule to queue assignment information
            ant = {}
            # for each of the machines, rules are randomly picked from the
            # options list
            for k in collated.keys():
                ant[k] = random.choice(collated[k])
            # TODO: function to calculate ant id. Store ant id in ant dict
            ant_key = repr(ant)
            # if the ant was not already tested, only then test it
            if ant_key not in tested_ants:
                tested_ants.add(ant_key)

                # the current ant to be simulated (evaluated) is added to the
                # ants list
                ants.append(ant)

                # set scheduling rule on queues based on ant data
                ant_data = copy(data)
                for k, v in ant.items():
                    ant_data["nodes"][k]['schedulingRule'] = v

                ant['key'] = ant_key

                # TODO: those two steps have to be parallelized
                ant['result'] = DefaultSimulation.runOneScenario(self, ant_data)
                ant['score'] = self._calculateAntScore(ant)

        # remove ants that outputs the same schedules
        ants_without_duplicates = dict()
        for ant in ants:
          ant_result = copy(ant['result'])
          ant_result['general'].pop('totalExecutionTime', None)
          ant_result = json.dumps(ant_result, sort_keys=True)
          ants_without_duplicates[ant_result] = ant

        # The ants in this generation are ranked based on their scores and the
        # best (max_results) are selected
        ants = sorted(ants_without_duplicates.values(),
          key=operator.itemgetter('score'))[:max_results]

        for l in ants:
            # update the options list to ensure that good performing queue-rule
            # combinations have increased representation and good chance of
            # being selected in the next generation
            for m in collated.keys():
                # e.g. if using EDD gave good performance for Q1, then another
                # 'EDD' is added to Q1 so there is a higher chance that it is
                # selected by the next ants.
                collated[m].append(l[m])

    return ants
