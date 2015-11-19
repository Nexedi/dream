from dream.plugins import plugin
from pprint import pformat
from copy import copy, deepcopy
import json
import time
import random
import operator
import xmlrpclib

from dream.simulation.Queue import Queue
from dream.simulation.Operator import Operator
from dream.simulation.Globals import getClassFromName
from dream.plugins.Batches.BatchesACO import BatchesACO

import xlwt
import StringIO


class BatchesStochasticACO(BatchesACO):

  # changes all processing time distributions to stochastic
  def createStochasticData(self, data):
    nodes=data['graph']['node']
    for node_id,node in nodes.iteritems():
        processingTime=node.get('processingTime',{})
        distribution=processingTime.get("Fixed",{})
        if distribution:
            mean=distribution['mean']
            if mean:
                processingTime.pop('Fixed',None)
                processingTime['Triangular']={
                        "mean":mean,
                        "min":0.8*mean,
                        "max":1.2*mean
                }
    return data

  def calculateStochasticAntScore(self, ant):
    """Calculate the score of this ant.
    """
    result, = ant['result']['result_list']  #read the result as JSON
    #loop through the elements 
    for element in result['elementList']:
        element_family = element.get('family', None)
        #id the class is Exit get the unitsThroughput
        if element_family == 'Exit':
            unitsThroughput=element['results'].get('unitsThroughput',None)
            if not unitsThroughput:
                unitsThroughput=element['results']['throughput']
            # below checking the predecessors of exit. If a predecessor is reassembly and 
            # has WIP add this also in the throughput
            for objectId in self.getPredecessors(ant['input'], element['id']):
                for record in result['elementList']:
                    if record['id']==objectId and 'Reassembly' in record['_class']:
                        finalWIPList=record['results'].get('final_WIP',[0])
                        for i in range(len(finalWIPList)):
                            unitsThroughput[i]+=finalWIPList[i]     
            self.outputSheet.write(self.rowIndex,2,'Units Throughput Per Replication')
            col=3
            for element in unitsThroughput:
                self.outputSheet.write(self.rowIndex,col,element)          
                col+=1
            self.rowIndex+=1
            averageUnitsThroughput=sum(unitsThroughput)/float(len(unitsThroughput))
    # return the negative value since they are ranked this way. XXX discuss this
    return -averageUnitsThroughput

  def run(self, data):
    """Preprocess the data.
    """
    self.outputFile = xlwt.Workbook()
    self.outputSheet = self.outputFile.add_sheet('ACO Results', cell_overwrite_ok=True)
    self.rowIndex=0
    self.columnIndex=0

    distributor_url = data['general'].get('distributorURL')
    distributor = None
    if distributor_url:
        distributor = xmlrpclib.Server(distributor_url)
        
    # create a stochastic set of data
    stochasticData=deepcopy(data)
    stochasticData=self.createStochasticData(stochasticData)

    multiprocessorCount = data['general'].get('multiprocessorCount')

    tested_ants = set()
    start = time.time()         # start counting execution time

    collated=self.createCollatedScenarios(data)    
    assert collated 

    max_results = int(data['general'].get('numberOfSolutions',1))
    # this is for how many ants should carry their pheromones in the next generation
    numberOfAntsForNextGeneration=int(data['general'].get('numberOfAntsForNextGeneration',1))
    # this is for how many ants should be evaluated stochastically in every generation
    numberOfAntsForStochasticEvaluationInGeneration=int(data['general'].get('numberOfAntsForStochasticEvaluationInGeneration',2))
    # number of replications for stochastic ants inside the generation
    numberOfReplicationsInGeneration=data['general'].get('numberOfReplicationsInGeneration',3)  
    # this is for how many ants should be evaluated stochastically in the end
    numberOfAntsForStochasticEvaluationInTheEnd=int(data['general'].get('numberOfAntsForStochasticEvaluationInTheEnd',2))
    # number of replications for stochastic ants in the end
    numberOfReplicationsInTheEnd=data['general'].get('numberOfReplicationsInTheEnd',6)
    
    self.outputSheet.write(self.rowIndex,0,'ACO attributes')    
    self.rowIndex+=1
    
    self.outputSheet.write(self.rowIndex,1,'Number Of Generations')
    self.outputSheet.write(self.rowIndex,2,int(data["general"]["numberOfGenerations"]))
    self.rowIndex+=1

    self.outputSheet.write(self.rowIndex,1,'Number Of Ants Per Generation')
    self.outputSheet.write(self.rowIndex,2,int(data["general"]["numberOfAntsPerGenerations"]))
    self.rowIndex+=1   
    
    self.outputSheet.write(self.rowIndex,1,'Stochastic Ants in Generation')
    self.outputSheet.write(self.rowIndex,2,numberOfAntsForStochasticEvaluationInGeneration)
    self.rowIndex+=1
    
    self.outputSheet.write(self.rowIndex,1,'Number of replications inside generation')
    self.outputSheet.write(self.rowIndex,2,numberOfReplicationsInGeneration)
    self.rowIndex+=1
    
    self.outputSheet.write(self.rowIndex,1,'Stochastic Ants in the end')
    self.outputSheet.write(self.rowIndex,2,numberOfAntsForStochasticEvaluationInTheEnd)
    self.rowIndex+=1
    
    self.outputSheet.write(self.rowIndex,1,'Number of replications in the end')
    self.outputSheet.write(self.rowIndex,2,numberOfReplicationsInTheEnd)
    self.rowIndex+=1

    assert max_results >= 1
    assert numberOfAntsForNextGeneration>=1 \
                and numberOfAntsForNextGeneration<=int(data["general"]["numberOfAntsPerGenerations"])

    ants = [] #list of ants for keeping track of their performance

    # Number of times new ants are to be created, i.e. number of generations (a
    # generation can have more than 1 ant)
    seedPlus = 0
    for i in range(int(data["general"]["numberOfGenerations"])):
        self.outputSheet.write(self.rowIndex,0,'Generation '+str(i+1))
        self.rowIndex+=1
        antsInCurrentGeneration=[]
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
        

        ants.extend(scenario_list)
        antsInCurrentGeneration.extend(scenario_list)
        
        # if all the ants of the generation will be evaluated stochastically
        # do not do deterministic runs
        if numberOfAntsForStochasticEvaluationInGeneration == int(data["general"]["numberOfAntsPerGenerations"]):
            uniqueAntsInThisGeneration = dict()
            for ant in antsInCurrentGeneration:
                ant['result']=dict()
                ant['result']['result_list']=[ant['key']]
                ant['score']=0
                ant_result, = copy(ant['result']['result_list'])
                ant_result = json.dumps(ant_result, sort_keys=True)
                uniqueAntsInThisGeneration[ant_result] = ant
                
            antsForStochasticEvaluationInGeneration = sorted(uniqueAntsInThisGeneration.values(),
              key=operator.itemgetter('score'))[:numberOfAntsForStochasticEvaluationInGeneration]
        else:
            # run the deterministic ants               
            for ant in scenario_list:
                self.outputSheet.write(self.rowIndex,1,'running deterministic')
                self.outputSheet.write(self.rowIndex,2,ant['key'])
                self.rowIndex+=1
                ant['result'] = self.runOneScenario(ant['input'])['result']
                ant['score'] = self._calculateAntScore(ant)      
                ant['evaluationType']='deterministic'
                self.outputSheet.write(self.rowIndex,2,'Units Throughput')
                self.outputSheet.write(self.rowIndex,3,-ant['score'])
                self.rowIndex+=1

            # in this generation remove ants that outputs the same schedules
            # XXX we in fact remove ants that produce the same output json
            # XXX in the stochastic case maybe there is not benefit to remove ants. 
            # XXX so I kept totalExecutionTime to have them all
            uniqueAntsInThisGeneration = dict()
            for ant in antsInCurrentGeneration:
                ant_result, = copy(ant['result']['result_list'])
                ant_result = json.dumps(ant_result, sort_keys=True)
                uniqueAntsInThisGeneration[ant_result] = ant
                
            # The ants in this generation are ranked based on their scores and the
            # best (numberOfAntsForStochasticEvaluationInGeneration) are selected to 
            # be evaluated stochastically
            antsForStochasticEvaluationInGeneration = sorted(uniqueAntsInThisGeneration.values(),
              key=operator.itemgetter('score'))[:numberOfAntsForStochasticEvaluationInGeneration]

             
        for ant in antsForStochasticEvaluationInGeneration:
            ant['input']=self.createStochasticData(ant['input'])
            ant['input']['general']['numberOfReplications']=numberOfReplicationsInGeneration
            self.outputSheet.write(self.rowIndex,1,'running stochastic for '+str(numberOfReplicationsInGeneration)+' replications')
            self.outputSheet.write(self.rowIndex,2,ant['key'])
            self.rowIndex+=1
            ant['result'] = self.runOneScenario(ant['input'])['result']
            ant['evaluationType']='stochastic'
            ant['score'] = self.calculateStochasticAntScore(ant)
            self.outputSheet.write(self.rowIndex,2,'Average Units Throughput')
            self.outputSheet.write(self.rowIndex,3,-ant['score'])
            self.rowIndex+=1
        
        # if we had stochastic evaluation of ants at the end of the generation
        if numberOfAntsForStochasticEvaluationInGeneration:
            # for the ants that were not evaluated stochastically set score = 0
            for ant in antsInCurrentGeneration:
                if ant['evaluationType']=='deterministic':
                    ant['score']=0
                  
        # if we had stochastic evaluation keep only those ants in sorting
        if numberOfAntsForStochasticEvaluationInGeneration:
            uniqueAntsInThisGeneration = dict()
            for ant in antsForStochasticEvaluationInGeneration:
                ant_result, = copy(ant['result']['result_list'])
                ant_result = json.dumps(ant_result, sort_keys=True)
                uniqueAntsInThisGeneration[ant_result] = ant
        
        antsForNextGeneration = sorted(uniqueAntsInThisGeneration.values(),
          key=operator.itemgetter('score'))[:numberOfAntsForNextGeneration]
           
        for l in antsForNextGeneration:
            self.outputSheet.write(self.rowIndex,1,'Ant to carry pheromone to next generation')
            self.outputSheet.write(self.rowIndex,2,l['key'])
            self.rowIndex+=1
            # update the options list to ensure that good performing queue-rule
            # combinations have increased representation and good chance of
            # being selected in the next generation
            for m in collated.keys():
                # e.g. if using EDD gave good performance for Q1, then another
                # 'EDD' is added to Q1 so there is a higher chance that it is
                # selected by the next ants.
                collated[m].append(l[m])

    self.rowIndex+=1
    self.outputSheet.write(self.rowIndex,0,'ACO Ended, post processing to follow for '+str(numberOfAntsForStochasticEvaluationInTheEnd)+' Ants')
    self.rowIndex+=1
    
    # from all the ants in the experiment remove ants that outputs the same schedules
    # XXX we in fact remove ants that produce the same output json
    uniqueAnts = dict()
    for ant in ants:
        ant_result, = copy(ant['result']['result_list'])
        ant_result = json.dumps(ant_result, sort_keys=True)
        uniqueAnts[ant_result] = ant
        
    # The ants are ranked based on their scores and the
    # best (max_results) are selected to be returned
    if numberOfAntsForStochasticEvaluationInTheEnd > 0:
        ants = sorted(uniqueAnts.values(),
          key=operator.itemgetter('score'))[:numberOfAntsForStochasticEvaluationInTheEnd]
        for ant in ants:
            ant['input']=self.createStochasticData(ant['input'])
            ant['input']['general']['numberOfReplications']=numberOfReplicationsInTheEnd
            self.outputSheet.write(self.rowIndex,1,'running stochastic for '+str(numberOfReplicationsInTheEnd)+' replications')
            self.outputSheet.write(self.rowIndex,2,ant['key']) 
            self.rowIndex+=1
            ant['result'] = self.runOneScenario(ant['input'])['result']
            ant['score'] = self.calculateStochasticAntScore(ant)     
            self.outputSheet.write(self.rowIndex,2,'Average Units Throughput')
            self.outputSheet.write(self.rowIndex,3,-ant['score'])
            self.rowIndex+=1

    # from all the ants in the experiment remove ants that outputs the same schedules
    # XXX we in fact remove ants that produce the same output json
    uniqueAnts = dict()
    for ant in ants:
        ant_result, = copy(ant['result']['result_list'])
        ant_result = json.dumps(ant_result, sort_keys=True)
        uniqueAnts[ant_result] = ant

    # The ants are ranked based on their scores and the
    # best (max_results) are selected to be returned
    ants = sorted(uniqueAnts.values(),
      key=operator.itemgetter('score'))[:max_results]

    data['result']['result_list'] = result_list = []
    for ant in ants:
      result, = ant['result']['result_list']
      result['score'] = ant['score']
      result['key'] = ant['key']
      result_list.append(result)

    self.outputSheet.write(self.rowIndex,0,"Execution time %0.2fs" % (time.time() - start))
    self.rowIndex+=1
    
    # return the workbook as encoded
    outputStringIO = StringIO.StringIO()
    self.outputFile.save(outputStringIO)
    encodedOutputFile=outputStringIO.getvalue().encode('base64') 
    data['result']['result_list'][-1]['output_ACO_spreadsheet'] = {
          'name': 'ACO details.xls',
          'mime_type': 'application/vnd.ms-excel',
          'data': encodedOutputFile
        }

    self.logger.info("ACO finished, execution time %0.2fs" % (time.time() - start))
    return data