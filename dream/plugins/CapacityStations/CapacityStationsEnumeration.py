from dream.plugins.Enumeration import Enumeration
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

# enumeration in order to search for the optimal threshold
class CapacityStationsEnumeration(Enumeration):
    def calculateScenarioScore(self, scenario):
        """Calculate the score of this scenario.
        """
        totalDelay=0    #set the total delay to 0
        result, = scenario['result']['result_list']  #read the result as JSON
        #loop through the elements
        for element in result['elementList']:
            #id the class is Job
            if element.get('_class', None) == "Dream.CapacityProject":
                id=element['id']
                exitDay=element['results']['schedule'][-1]['exitTime']
                for project in scenario['input']['input']['BOM']['productionOrders']:
                    if project['id']==id:
                        dueDate=project['dueDate']
                delay = exitDay-dueDate
                # A negative delay would mean we are ahead of schedule. This
                # should not be considered better than being on time.
                totalDelay += max(delay, 0)
        return totalDelay
        
    # creates the collated scenarios, i.e. the list 
    # of options collated into a list for ease of referencing in ManPy
    def createScenarioList(self,data):
        scenarioList=[]
        step=data['general'].get('thresholdStep',7)
        dueDates=[]
        for project in data['input']['BOM']['productionOrders']:
            dueDates.append(project['dueDate'])
        minimum=min(dueDates)
        maximum=max(dueDates)
        thresholds=[]
        for i in range(0,int(maximum-minimum),step):
            thresholds.append(i)
        thresholds.append(int(maximum-minimum)+1)
        for threshold in thresholds:
            scenarioList.append({'key':str(threshold),'threshold':threshold})
        return scenarioList
    
    # creates the scenario. Here just set the dueDateThreshold
    def createScenarioData(self,data,scenario): 
        scenarioData=deepcopy(data)
        scenarioData['graph']['node']['CSC']['dueDateThreshold']=scenario['threshold']     
        return scenarioData   
    
    # checks if the algorithm should terminate.
    # in this case terminate if the total delay is increased
    def checkIfShouldTerminate(self,data,scenarioList): 
        # in the first scenario no need to terminate
        if len(scenarioList)<2:
            return False
        # find the last scenario that is scored
        index=0
        for i in range(len(scenarioList)):
            if scenarioList[i].get('score',None)==None:
                index=i-1
                break
        # if the delay of the last scenario is bigger than the previous return true
        if index:
            if scenarioList[index]['score']>scenarioList[index-1]['score']:
                return True
        return False
