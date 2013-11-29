# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================
'''
Created on 22 Nov 2013

@author: Dipo, George
'''
'''
Optimization based on scenario analysis 
For now it is only mixing different scheduling rules of the Queues
'''

import random
import json
import LineGenerationJSONACO
import time

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

#method that takes an ant and creates a json with the scheduling rules in order to send it to ManPy main script
def createAntJSON(ant):
    antJSON={}
    antJSON["_class"] = "Dream.Simulation" 
    antJSON["nodes"] = {}
    for record in ant:
        stationId=str(record)
        schedulingRule=ant.get(stationId, "FIFO")
        antJSON["nodes"][stationId] = {}
        antJSON["nodes"][stationId]["_class"]="Dream.QueueJobShop"
        antJSON["nodes"][stationId]["schedulingRule"]=schedulingRule
    return json.dumps(antJSON, indent=True)

def calculateAntTotalDelay(ant):
    totalDelay=0    #set the total delay to 0
    jsonData=json.loads(ant['resultJSON'])  #read the result as JSON
    elementList = jsonData['elementList']   #find the route of JSON
    #loop through the elements
    for element in elementList:
        elementClass=element['_class']  #get the class
        #id the class is Job
        if elementClass=='Dream.Job':
            results=element['results']  
            delay=float(results.get('delay', "0")) 
            totalDelay+=delay
    return totalDelay

'''
Below are initial lists of scheduling rules to be considered for each of the queues/machine, these could be entered at GUI level

I believe the ability to attribute each of these lists to a queue object is the only requirements at GUI level. Everything henceforth is a ManPy and Optimization business.
'''
#M1Options = ['EDD','WINQ','LPT','SPT','SRR','ERD','PCO','MS'] #initial list of scheduling rules that are to be randomly used for each of the machines
#M2Options = ['EDD','WINQ','LPT','SPT','SRR','ERD','PCO','MS']
#M3Options = ['EDD','WINQ','LPT','SPT','SRR','ERD','PCO','MS']
#M4Options = ['EDD','WINQ','LPT','SPT','SRR','ERD','PCO','MS']
#M5Options = ['EDD','WINQ','LPT','SPT','SRR','ERD','PCO','MS']

M1Options = ['EDD','NextStage','EOD','Priority','RPC','MinSlack','NumStages'] #initial list of scheduling rules that are to be randomly used for each of the machines
M2Options = ['EDD','NextStage','EOD','Priority','RPC','MinSlack','NumStages'] 
M3Options = ['EDD','NextStage','EOD','Priority','RPC','MinSlack','NumStages'] 
M4Options = ['EDD','NextStage','EOD','Priority','RPC','MinSlack','NumStages'] 
M5Options = ['EDD','NextStage','EOD','Priority','RPC','MinSlack','NumStages'] 

#Optimization takes over from here and it calls ManPy simulation at intervals using the sim function 
def main():
    start=time.time()                               # start counting execution time 
    modelJSONFile=open("C:\Users\George\dream\dream\simulation\JSONInputs\Topology20.JSON", "r")     #the JSON of the model. To be sent from GUI
    modelJSONData=modelJSONFile.read()   
    modelJSON=json.loads(modelJSONData)
    modelJSON=json.dumps(modelJSON, indent=True)
    collated = {'Q1':M2Options,'Q2':M3Options,'Q3':M4Options,'Q4':M4Options,'Q5':M5Options} #the list of options collated into a dictionary for ease of referencing in ManPy
    ants = [] #list of ants for keeping track of their performance
    
    for i in range(6): #Number of times new ants are to be created, i.e. number of generations (a generation can have more than 1 ant)
        for j in range(8): #number of ants created per generation
            ant = {} #an ant dictionary to contain rule to queue assignment information 
            for k in collated.keys(): #for each of the machines, rules are randomly picked from the options list 
                    ant[str(k)] = random.choice(collated[str(k)])
            ants.append(ant) #the current ant to be simulated (evaluated) is added to the ants list
            antJSON=createAntJSON(ant)
            ant['resultJSON'] = LineGenerationJSONACO.main(modelJSON,antJSON)         
            ant['score'] = calculateAntTotalDelay(ant) 
        ants = ranking(ants,4) #the ants in this generation are ranked based on their scores and the best 4 are selected

        for l in ants: #update the options list to ensure that good performing queue-rule combinations have increased representation and good chance of being selected in the next generation
            for m in collated.keys():#e.g. if using EDD gave good performance for  Queue 1, then another 'EDD' is added to M1Options so there is a higher chance that it is selected by the next ants.
                collated[m].append(l[m])
        #print collated#to verify that the list of options was updated accordingly
    print 'Best 3 results'
    print '================='
    print ants[0]['score']
    print '================='
    print ants[1]['score']
    print '================='
    print ants[2]['score']
    print "execution time=", str(time.time()-start)

if __name__ == '__main__':
    main()

