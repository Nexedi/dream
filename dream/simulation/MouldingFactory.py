from copy import copy
import json
import time
import random
from Globals import G

from dream.simulation.Default import Simulation as DefaultSimulation

def ranking(candidates,elg): #this function is used for ranking and selection of the best ant
    pop = [] #this list is used separately to extract ant scores for ranking them
    for ch in candidates: #it loops through the list of ants and append their scores to a list
        pop.append(ch['score']) #it append the scores to the list pop
    pop.sort() #pop = list(set(pop)) #the scores are sorted in ascending order
    del pop[elg:] #from the sorted list, a certain number specified as elg are only retained - others are deleted
    fittest = [] #Now, another list is created for the best ranked ants
    for chrom in candidates: #the retained scored are matched with Ants
        if chrom['score'] in pop:#if an ants score was retained, it becomes retained too
            fittest.append(chrom)
            pop.remove(chrom['score'])#as the associated ants are appended the scores are immediately deleted to avoid confusion
    return fittest #returns the fittest Ants of the generation

def calculateAntTotalDelay(ant):
    """Calculate the score of this ant.

    XXX Maybe this can be based on other criterions, such as completion time ?
    """
    totalDelay=0    #set the total delay to 0
    jsonData=json.loads(ant['resultJSON'])  #read the result as JSON
    elementList = jsonData['elementList']   #find the route of JSON
    #loop through the elements
    for element in elementList:
        elementClass=element['_class']  #get the class
        #id the class is Job
        if elementClass=='Dream.Job':
            results=element['results']  
            delay = float(results.get('delay', "0")) 
            totalDelay+=delay
    return totalDelay

# XXX jerome: isn't repr() enough ? or json.dumps ?
# XXX use a set
#creates a light coded form of the ant and tests it
def checkIfAntTested(ant):
    #code the ant in a lighter string form
    codedAnt=''
    for key in ant:
        codedAnt+=ant[key]
    #if it already exists return true so that it will not be tested
    if codedAnt in G.CodedAnstsList:
        return True
    #else add it to the list and return false
    else:
        G.CodedAnstsList.append(codedAnt)
        return False 


class Simulation(DefaultSimulation):

  def _setWIP(self, in_data):
    """ Set the WIP in queue from spreadsheet data.
    """
    data = copy(in_data)
    if 'spreadsheet' in data:
      wip_dict = {}
      for value_list in data['spreadsheet']:
        if value_list[1] == 'ID' or not value_list[1]:
          continue
        sequence_list = value_list[6].split('-')
        processing_time_list = value_list[7].split('-')
        wip_dict.setdefault(sequence_list[0], []).append(
          {
            "_class": "Dream.Job",
            "id": value_list[1],
            "name": value_list[0],
            "order_date": value_list[2],
            "due_date": value_list[3],
            # TODO: calculate due date properly (based on simulation date ?)
            "dueDate": 1,
            "priority": value_list[4],
            "material": value_list[5],
            "route": [
              {
                "processingTime": {
                  "distributionType": "Fixed",
                  "mean": processing_time_list[i],
                  },
                "stationId": sequence_list[i],
                "stepNumber": i
              } for i in xrange(len(sequence_list))]
          }
        )
      for node_id in data['nodes'].keys():
        if node_id in wip_dict:
          data['nodes'][node_id]['wip'] = wip_dict[node_id]
      del(data['spreadsheet'])
      return data


  def run(self, data):
    data = self._setWIP(data)

    G.CodedAnstsList=[]       # a list to keep all the solutions in a coded form
    start=time.time()         # start counting execution time 

    # the list of options collated into a dictionary for ease of referencing in ManPy
    collated = {'Q1': ['EDD', 'LPT', ], 'Q2': ['EDD', 'LPT', 'FIFO']}
    # TODO: this list have to be defined in the GUI
    # TODO: options should not be limited to scheduling rules. For example we
    # want to try various machines of same technology

    ants = [] #list of ants for keeping track of their performance

    for i in range(10): #Number of times new ants are to be created, i.e. number of generations (a generation can have more than 1 ant)
        for j in range(20): #number of ants created per generation
            ant = {} # an ant dictionary to contain rule to queue assignment information 
            for k in collated.keys(): #for each of the machines, rules are randomly picked from the options list 
                ant[str(k)] = random.choice(collated[str(k)])
            #if the ant was not already tested, only then test it
            if not checkIfAntTested(ant):
                ants.append(ant) #the current ant to be simulated (evaluated) is added to the ants list            

                # set scheduling rule on queues based on ant data
                ant_data = copy(data)
                for k, v in ant.items():
                    # XXX we could change ant dict to contain the name of the
                    # property to change ( instead of hardcoding schedulingRule )
                    ant_data["nodes"][k]['schedulingRule'] = v

                ant['resultJSON'] = DefaultSimulation.run(self, ant_data)
                ant['score'] = calculateAntTotalDelay(ant)

        ants = ranking(ants, 4) #the ants in this generation are ranked based on their scores and the best 4 are selected

        for l in ants: #update the options list to ensure that good performing queue-rule combinations have increased representation and good chance of being selected in the next generation
            for m in collated.keys():#e.g. if using EDD gave good performance for  Queue 1, then another 'EDD' is added to M1Options so there is a higher chance that it is selected by the next ants.
                collated[m].append(l[m])

    result_count = min(4, len(ants))
    print '%s best results :' % result_count
    for i in range(result_count):
        ant = ants[i]
        displayed_ant = copy(ant)
        displayed_ant.pop('resultJSON')
        print '================='
        print displayed_ant

    print "execution time=", str(time.time()-start)

    # TODO: return multiple results in the GUI
    # return [ant['resultJSON'] for ant in ants]
    return DefaultSimulation.run(self, data)
