from dream.plugins import plugin
from pprint import pformat
from copy import copy, deepcopy
import json
import time
import random
import operator
import xmlrpclib
import signal
from multiprocessing import Pool

from dream.simulation.Queue import Queue
from dream.simulation.Operator import Operator
from dream.simulation.Globals import getClassFromName

# run an ant in a subrocess. Can be parrallelized.
def runAntInSubProcess(ant):
  ant['result'] = plugin.ExecutionPlugin.runOneScenario(ant['input'])['result']
  return ant

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


  def run(self, data):
    """Preprocess the data.
    """
    distributor_url = data['general'].get('distributorURL')
    distributor = None
    if distributor_url:
        distributor = xmlrpclib.Server(distributor_url)

    multiprocessorCount = data['general'].get('multiprocessorCount')

    tested_ants = set()
    start = time.time()         # start counting execution time

    collated=self.createCollatedScenarios(data)    
    assert collated 

    max_results = int(data['general'].get('numberOfSolutions',0))
    assert max_results >= 1

    numberOfAntsForNextGeneration = int(data['general'].get('numberOfAntsForNextGeneration', max_results))

    ants = [] #list of ants for keeping track of their performance

    # Number of times new ants are to be created, i.e. number of generations (a
    # generation can have more than 1 ant)
    seedPlus = 0
    for i in range(int(data["general"]["numberOfGenerations"])):
        scenario_list = [] # for the distributor
        # number of ants created per generation
        for j in range(int(data["general"]["numberOfAntsPerGenerations"])):
            # an ant dictionary to contain rule to queue assignment information
            ant = {}
            # for each of the machines, rules are randomly picked from the
            # options list
            seed = data['general'].get('seed', 10)
            if seed == '' or seed == ' ' or seed == None:
                seed = 10
            for k in collated.keys():
                random.seed(seed+seedPlus)
                ant[k] = random.choice(collated[k])
                seedPlus +=1
            # TODO: function to calculate ant id. Store ant id in ant dict
            ant_key = repr(ant)
            # if the ant was not already tested, only then test it
            if ant_key not in tested_ants:
                tested_ants.add(ant_key)
                ant_data=deepcopy(self.createAntData(data, ant))
                ant['key'] = ant_key
                ant['input'] = ant_data
                scenario_list.append(ant)
                       
        if distributor is None:
            if multiprocessorCount:
                self.logger.info("running multiprocessing ACO with %s processes" % multiprocessorCount)
                # We unset our signal handler to print traceback at the end
                # otherwise logs are confusing. 
                sigterm_handler = signal.getsignal(signal.SIGTERM)
                pool = Pool(processes=multiprocessorCount)
                try:
                    signal.signal(signal.SIGTERM, signal.SIG_DFL)
                    scenario_list = pool.map(runAntInSubProcess, scenario_list)
                    pool.close()
                    pool.join()
                finally:
                    signal.signal(signal.SIGTERM, sigterm_handler)
            else:
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
                result = json.loads(result)
                if 'result' in result: # XXX is this still needed ???
                  result = result['result']
                  assert "result_list" in result
                else:
                  result = {'result_list': [result]}
                ant['result'] = result

        for ant in scenario_list:
            ant['score'] = self._calculateAntScore(ant)

        ants.extend(scenario_list)

        # remove ants that outputs the same schedules
        # XXX we in fact remove ants that produce the same output json
        ants_without_duplicates = dict()
        for ant in ants:
            ant_result, = copy(ant['result']['result_list'])
            ant_result['general'].pop('totalExecutionTime', None)
            ant_result = json.dumps(ant_result, sort_keys=True)
            ants_without_duplicates[ant_result] = ant

        # The ants in this generation are ranked based on their scores and the
        # best (numberOfAntsForNextGeneration) are added again to the list to increase
        # the probability of their characteristics since they are more likely to
        # be selected again
        ants = sorted(ants_without_duplicates.values(),
          key=operator.itemgetter('score'))[:numberOfAntsForNextGeneration]

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
    for ant in ants[:max_results]:
      result, = ant['result']['result_list']
      result['score'] = ant['score']
      result['key'] = ant['key']
      result_list.append(result)

    self.logger.info("ACO finished, execution time %0.2fs" % (time.time() - start))
    return data
