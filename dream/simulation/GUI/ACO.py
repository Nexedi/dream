from copy import copy
import json
import time
import random
import operator
import xmlrpclib

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
    conf["Dream-Configuration"]["property_list"].append(
        { "id": "distributorURL",
          "type": "string",
          "name": "Distributor URL",
          "description": "URL of an ERP5 Distributor, see "
            "https://github.com/erp5/erp5/tree/dream_distributor",
          "_class": "Dream.Property",
          "_default": ''} )
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

    distributor_url = data['general']['distributorURL']
    distributor = None
    if distributor_url:
        distributor = xmlrpclib.Server(distributor_url)

    tested_ants = set()
    start = time.time()         # start counting execution time

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
        scenario_list = [] # for the distributor
        # number of ants created per generation
        for j in range(data["general"]["numberOfAntsPerGenerations"]):
            # an ant dictionary to contain rule to queue assignment information
            ant = {}
            # for each of the machines, rules are randomly picked from the
            # options list
            l=1 # used to create different random from every key
            for k in collated.keys():
                from random import Random
                rnd=Random(1+i*j*l)
                l+=1
                ant[k] = rnd.choice(collated[k])
            # TODO: function to calculate ant id. Store ant id in ant dict
            ant_key = repr(ant)
            # if the ant was not already tested, only then test it
            if ant_key not in tested_ants:
                tested_ants.add(ant_key)

                # set scheduling rule on queues based on ant data
                ant_data = copy(data)
                for k, v in ant.items():
                    ant_data["nodes"][k]['schedulingRule'] = v

                ant['key'] = ant_key
                ant['input'] = ant_data

                scenario_list.append(ant)

        if distributor is None:
            successful_scenario_list = []
            # synchronous
            for ant in scenario_list:
                try:
                    ant['result'] = DefaultSimulation.runOneScenario(self, ant['input'])
                    successful_scenario_list.append(ant)
                except Exception, e:
                    print "Error executing scenario, skipping ant. Scenaro was:\n%s" %  ant['input']
            scenario_list = successful_scenario_list

        else: # asynchronous
            job_id = distributor.requestSimulationRun(
                [json.dumps(x) for x in scenario_list])

            print "Job registered", job_id
            while True:
                time.sleep(1.)
                result_list = distributor.getJobResult(job_id)
                # The distributor returns None when calculation is still ongoing,
                # or the list of result in the same order.
                if result_list is not None:
                    print "Job terminated"
                    break

            for ant, result in zip(scenario_list, result_list):
                ant['result'] = json.loads(result)

        for ant in scenario_list:
            ant['score'] = self._calculateAntScore(ant)

        ants.extend(scenario_list)

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

    print "ACO finished, execution time %0.2fs" % (time.time() - start)
    return ants
