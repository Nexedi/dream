from copy import copy
import json
import time
import random
import operator
import xmlrpclib

from dream.simulation.Queue import Queue
from dream.simulation.Globals import getClassFromName

from . import Plugin

class ACOExecution(Plugin.DefaultExecutionPlugin):

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
    distributor_url = data['general'].get('distributorURL')
    distributor = None
    if distributor_url:
        distributor = xmlrpclib.Server(distributor_url)
        self.logger.info("Distributed ACO using distributor from %s" % distributor)

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
            for k in collated.keys():
                ant[k] = random.choice(collated[k])
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
            # synchronous
            for ant in scenario_list:
                # TODO: adapt this.
                ant['result'] = Plugin.DefaultExecutionPlugin.run(self, ant['input'])

        else: # asynchronous
            job_id = distributor.requestSimulationRun(
                [json.dumps(x) for x in scenario_list])

            self.logger.info("Job registered " + job_id)
            while True:
                time.sleep(1.)
                result_list = distributor.getJobResult(job_id)
                # The distributor returns None when calculation is still ongoing,
                # or the list of result in the same order.
                if result_list is not None:
                    self.logger.info("Job terminated")
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

    self.logger.info("ACO finished, execution time %0.2fs" % (time.time() - start))
    return ants
