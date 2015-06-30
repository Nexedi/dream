# ===========================================================================
# Copyright 2015 Dublin City University
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
Created on 8 Dec 2014

@author: Anna
'''

''' implements ACO for the allocation of orders/forecast of a certain week/priority level '''

from AllocationRoutine_ACO2 import AllocationRoutine_ACO
from AllocationRoutine_Final2 import AllocationRoutine_Final
from Globals import G
from random import choice
from operator import itemgetter
from math import ceil
from numpy import mean
from copy import deepcopy


def ranking(candidates,elg):

    if elg >= len(candidates): #it always picks even number of chromosomes for crossover in order to have required pair of parents for crossover in LS
        elg = (elg-elg%2)
    else:
        elg = (elg+elg%2)
        
    finalCandidates = candidates        
    
    # add order sequence to candidates
    for i in range(len(finalCandidates)):
        finalCandidates[i]['orderSequence'] = i
    
    # sort candidates 
    fittestLateness = sorted(finalCandidates, key=itemgetter('excess', 'lateness', 'earliness'))
    fittestUtilisation = sorted(finalCandidates, key=itemgetter('targetUtil', 'minUtil'))
    
    # FIXME: verificare se sono tutti 0 lateness excess e earliness...in tal caso prendere direttamente da fittestUtilisation
    if fittestLateness[0]['excess']==fittestLateness[len(fittestLateness)-1]['excess'] and \
    fittestLateness[0]['lateness']==fittestLateness[len(fittestLateness)-1]['lateness'] and \
    fittestLateness[0]['earliness']==fittestLateness[len(fittestLateness)-1]['earliness']:
        
        # select the best solutions based on fittestUtilisation
        fittest = []
        fitID = []
        numFit = min([len(fittestUtilisation), elg])
        
        for i in range(numFit):
            fittest.append(fittestUtilisation[i])
            fitID.append(fittestUtilisation[i]['orderSequence'])
                
    else:
         
        # select candidates that appear in the first positions in both lists...with preference on Lateness metrics
        numTop = int(ceil(len(finalCandidates)*0.2))
        aLateness = []
        aUtilisation = []
        for i in range(numTop):
            aLateness.append(fittestLateness[i]['orderSequence'])
            aUtilisation.append(fittestUtilisation[i]['orderSequence'])
        
        aLateness = set(aLateness)
        aUtilisation = set(aUtilisation)
        selection = list(aLateness.intersection(aUtilisation))
        
        fittest = []
        fitID = []
        numFit = min([len(selection), elg])
        
        for i in range(numFit):
            x = 0
            while x < numTop:
                if fittestLateness[x]['orderSequence'] == selection[i]:
                    fittest.append(fittestLateness[x])
                    fitID.append(fittestLateness[x]['orderSequence'])
                    break
                x += 1
            
        
        # if there is not enough ants in selection then calculate the average ranking between the two sorted lists and 
        # select the ants with highest average ranking not previously included 
        # solve the ties in favour of lateness  
        if numFit < elg:
            
            ultRanking = {}
            rankingList = []
            for i in range(len(fittestLateness)):
                ultRanking[fittestLateness[i]['orderSequence']] = {'lateness':i, 'orderSequence':fittestLateness[i]['orderSequence']}
            for i in range(len(fittestUtilisation)):
                ultRanking[fittestUtilisation[i]['orderSequence']]['utilisation'] = i
                ultRanking[fittestUtilisation[i]['orderSequence']]['avg'] = mean([ultRanking[fittestUtilisation[i]['orderSequence']]['utilisation'], ultRanking[fittestUtilisation[i]['orderSequence']]['lateness']])
                rankingList.append(ultRanking[fittestUtilisation[i]['orderSequence']])
            
            rankingList = sorted(rankingList, key=itemgetter('avg', 'lateness'))   
            
            for i in range(len(rankingList)):
                if rankingList[i]['orderSequence'] not in fitID:    
                
                    x = 0
                    while x < len(fittestLateness):
                        if fittestLateness[x]['orderSequence'] == rankingList[i]['orderSequence']:
                            fittest.append(fittestLateness[x])
                            fitID.append(fittestLateness[x]['orderSequence'])
                            break
                        x += 1
                        
                    numFit += 1
                    if numFit == elg:
                        break
    
    termCriterion = 0           
#    scores = [ant['excess'] for ant in fittest]
#    if max(scores) - min(scores) <= 0.001*min(scores): #Termination Criteria to check for convergence - in this case, if the current solutions are within 10% range 
#        termCriterion += 1
#        
#    scores = [ant['targetUtil'] for ant in fittest]
#    if max(scores) - min(scores) <= 0.001*min(scores): #Termination Criteria to check for convergence - in this case, if the current solutions are within 10% range 
#        termCriterion += 1

    if termCriterion == 2:
        print 'Termination Criterion Reached'
        return fittest,'Terminate'
    else:
        return fittest,'Continue'


def finalRanking(candidates):
    
    finalCandidates = candidates        
    
    # add order sequence to candidates
    for i in range(len(finalCandidates)):
        finalCandidates[i]['orderSequence'] = i
    
    # sort candidates 
    fittestLateness = sorted(finalCandidates, key=itemgetter('excess', 'lateness', 'targetUtil', 'minUtil', 'earliness'))
    
    return fittestLateness[0]

def Allocation_ACO(initialWeek, itemList, itemType,ACOresults):

    # create an ant dictionary that contains applicable MA
    antDictionary = {}
    for item in itemList:
        antDictionary[item['orderID']] = deepcopy(item['MAlist'])
    
    ants = []   #list of ants that are being evaluated, an ant is a combination of different weighting factors for multi-obj optimisation (PB assignment)
    testedAnts = []
    
    antID = 1
    
    for gen in range(G.noGen):
        
        print 'generation', gen
        
        for rep in range(G.popSize):
            print 'ant', rep
            
            # create an ant
            ant = {}
            for item in itemList:
                ant[item['orderID']] = choice(antDictionary[item['orderID']])
            
            if ant in testedAnts:       
                continue

            # record ant
            testedAnts.append(ant)
            
            ant['antID'] = antID            
            
            # simulate ant
            resultAnt = AllocationRoutine_ACO(initialWeek, itemList, itemType, ant)
            ants.append(resultAnt)
            
            antID += 1
            
            # save ants results
            ACOresults.append((initialWeek, gen, rep, resultAnt['ant']['antID'],resultAnt['excess'], resultAnt['lateness'], resultAnt['earliness'], resultAnt['targetUtil'], resultAnt['minUtil'] ))
            
        # rank ants and select best ones
        ants, termCond = ranking(ants,2)
        for a in ants:
            ACOresults.append((initialWeek, gen, rep, a['ant']['antID'],'survived', '', '', '', ''))
            
        
        if termCond == 'Terminate':
            break
        
        # update weights
        for x in range(len(ants)):
            for orderID in ants[x]['ant'].keys():
                if orderID != 'antID':
                    antDictionary[orderID].append(ants[x]['ant'][orderID])
        
    # selection of final solution and results recording    
    print 'final allocation'    
    ant = finalRanking(ants)
    AllocationRoutine_Final(initialWeek, itemList, itemType, ant['ant'])
    ACOresults.append((initialWeek, gen, rep, ant['ant']['antID'], 'selected', '', '', '', ''))
    
    return ACOresults, ant['ant']
