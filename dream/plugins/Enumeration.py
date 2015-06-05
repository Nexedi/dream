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

# # run an ant in a subrocess. Can be parrallelized.
# def runAntInSubProcess(ant):
#   ant['result'] = plugin.ExecutionPlugin.runOneScenario(ant['input'])['result']
#   return ant

# Execution plugin that implements enumeration of different solutions
# this is an abstract class only its run() is to be used. Sub-classes should implement other methods 
# depending on the problem
class Enumeration(plugin.ExecutionPlugin):
    def calculateScenarioScore(self, scenario):
        raise NotImplementedError("Subclass must define 'calculateScenarioScore' method")

    # creates the collated scenarios, i.e. the list 
    # of options collated into a dictionary for ease of referencing in ManPy
    def createScenarioList(self,data):
        raise NotImplementedError("Subclass must define 'createScenarioList' method")
    
    # create the scenario
    def createScenarioData(self,data,scenario): 
        raise NotImplementedError("Subclass must define 'createScenarioData' method")
    
    # checks if the algorithm should terminate. Default is set to False so that the algorithm 
    # terminates only when all scenarios are considered
    def checkIfShouldTerminate(self,data,scenarioList): 
        return False

    def run(self, data):
    #     distributor_url = data['general'].get('distributorURL',None)
    #     distributor = None
    #     if distributor_url:
    #         distributor = xmlrpclib.Server(distributor_url)
    #     multiprocessorCount = data['general'].get('multiprocessorCount',None)
    
      start = time.time()         # start counting execution time
    
      numberOfSolutions = int(data['general'].get('numberOfSolutions',15))
      assert numberOfSolutions >= 1
      scenarioList=self.createScenarioList(data)
      
      # run the scenario. Only synchronous for now
      i=0
      for scenario in scenarioList: 
          scenario['input']=self.createScenarioData(data, scenario)
          scenario['result'] = self.runOneScenario(scenario['input'])['result']
          scenario['score'] = self.calculateScenarioScore(scenario)
          # it we should terminate remove the scenarios that are not scored yet
          if self.checkIfShouldTerminate(data, scenarioList):
              scenarioList = scenarioList[:i+1]
              break
          i+=1
   
        
      # remove ants that outputs the same schedules
      # XXX we in fact remove ants that produce the same output json      
      scenarioListWithoutDuplicates = []
      resultList=[]
      for scenario in scenarioList:
        scenarioResult = copy(scenario['result']['result_list'][0]['elementList'])
        #scenarioResult['general'].pop('totalExecutionTime', None)
        if scenarioResult not in resultList:
            resultList.append(scenarioResult)
            scenarioListWithoutDuplicates.append(scenario)
     
      # rank the scenarios based on their score and take only the numberOfSolutions best
      scenariosToReturn = sorted(scenarioListWithoutDuplicates,key=operator.itemgetter('score'))[:numberOfSolutions]
    
      # return the number of scenarios that need to be returned
      data['result']['result_list'] = result_list = []
      for scenario in scenariosToReturn:
        result, = scenario['result']['result_list']
        result['score'] = scenario['score']
        result['key'] = scenario['key']
        result_list.append(result)
    
      self.logger.info("Enumeration finished, execution time %0.2fs" % (time.time() - start))
      return data
