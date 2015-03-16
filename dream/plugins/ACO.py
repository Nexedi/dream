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

class ACO(plugin.ExecutionPlugin):

  def _calculateAntScore(self, ant):
    """Calculate the score of this ant.
    """
    totalDelay=0    #set the total delay to 0
    result, = ant['result']['result_list']  #read the result as JSON
    #loop through the elements
    for element in result['elementList']:
        element_family = element.get('family', None)
        #id the class is Job
        if element_family == 'Job':
            results=element['results']
            delay = float(results.get('delay', "0"))
            # A negative delay would mean we are ahead of schedule. This
            # should not be considered better than being on time.
            totalDelay += max(delay, 0)
    return totalDelay

  def run(self, data):
    """Preprocess the data.
    """
    self.logger.info("run: %s " % (pformat(data)))

    distributor_url = data['general'].get('distributorURL')
    distributor = None
    if distributor_url:
        distributor = xmlrpclib.Server(distributor_url)

    tested_ants = set()
    start = time.time()         # start counting execution time

    # the list of options collated into a dictionary for ease of referencing in
    # ManPy
    collated = dict()
    for node_id, node in data['graph']['node'].items():
      node_class = getClassFromName(node['_class'])
      if issubclass(node_class, Queue) or issubclass(node_class, Operator):
        collated[node_id] = list(node_class.getSupportedSchedulingRules())
    assert collated

    max_results = int(data['general'].get('numberOfSolutions',0))
    assert max_results >= 1

    ants = [] #list of ants for keeping track of their performance

    # Number of times new ants are to be created, i.e. number of generations (a
    # generation can have more than 1 ant)
    for i in range(int(data["general"]["numberOfGenerations"])):
        scenario_list = [] # for the distributor
        # number of ants created per generation
        for j in range(int(data["general"]["numberOfAntsPerGenerations"])):
            # an ant dictionary to contain rule to queue assignment information
            ant = {}
            # for each of the machines, rules are randomly picked from the
            # options list
            seedPlus = 0
            seed = data['general'].get('seed', 10)
            for k in collated.keys():
                random.seed(seed+seedPlus)
                ant[k] = random.choice(collated[k])
                seedPlus +=1
            # TODO: function to calculate ant id. Store ant id in ant dict
            ant_key = repr(ant)
            # if the ant was not already tested, only then test it
            if ant_key not in tested_ants:
                tested_ants.add(ant_key)

                # set scheduling rule on queues based on ant data
                ant_data = copy(data)
                for k, v in ant.items():
                    ant_data["graph"]["node"][k]['schedulingRule'] = v

                ant['key'] = ant_key
                ant['input'] = ant_data

                scenario_list.append(ant)

        if distributor is None:
            # synchronous
            for ant in scenario_list:
                ant['result'] = self.runOneScenario(ant['input'])['result']

        else: # asynchronous
            self.logger.info("Registering a job for %s scenarios" % len(scenario_list))
            start_register = time.time()
            job_id = distributor.requestSimulationRun(
                [json.dumps(x).encode('zlib').encode('base64') for x in scenario_list])
            self.logger.info("Job registered as %s (took %0.2fs)" % (job_id, time.time() - start_register ))

            while True:
                time.sleep(1.)
                result_list = distributor.getJobResult(job_id)
                # The distributor returns None when calculation is still ongoing,
                # or the list of result in the same order.
                if result_list is not None:
                    self.logger.info("Job %s terminated" % job_id)
                    break

            for ant, result in zip(scenario_list, result_list):
                ant['result'] = json.loads(result)['result']

        for ant in scenario_list:
            ant['score'] = self._calculateAntScore(ant)

        ants.extend(scenario_list)

        # remove ants that outputs the same schedules
        # XXX we in fact remove ands that produce the same output json
        ants_without_duplicates = dict()
        for ant in ants:
            ant_result, = copy(ant['result']['result_list'])
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

    data['result']['result_list'] = result_list = []
    for ant in ants:
      result, = ant['result']['result_list']
      result['score'] = ant['score']
      result['key'] = ant['key']
      result_list.append(result)

    self.logger.info("ACO finished, execution time %0.2fs" % (time.time() - start))
    return data
