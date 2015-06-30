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
Created on 29 Jan 2015

@author: Anna

Implements GA for identifying best SP sequence order in forecast disaggregation...best MA combination for each SP is chosen by LP method
Equivalent of Allocation_ACO for orders disaggregation
'''

from AllocationRoutine_ForecastGA import AllocationRoutine_ForecastGA
from AllocationRoutine_Forecast import AllocationRoutine_Forecast
from Globals import G
from RankingAlgorithms import rankingElitist, compareChromosomes, finalRanking
from GAoperators import order2x, displacement
from numpy import random
from copy import deepcopy


def Allocation_GA(initialWeek, itemList, itemType,GAresults):

    chromosomes = []   #list of ants that are being evaluated, an ant is a combination of different weighting factors for multi-obj optimisation (PB assignment)
    testedChrom = []
    bestChromosome = []     # record best chromosome for current generation
    
    chromoID = 0
    
    # get the list of orders ID
    orderList = {}
    orderIDlist = []
    for item in itemList:
        orderList[item['orderID']]=item        
        orderIDlist.append(item['orderID']) 
    
    #===========================
    # generate first population
    #===========================
    print 'generation 0'
    while chromoID < G.popSizeGA:        
        
        # generate new order sequence
        if chromoID == 0:
            chromo = {'cID': chromoID, 'seq':orderIDlist}
        else:
            chromo = {'cID':chromoID, 'seq':list(random.permutation(orderIDlist))}
        
        # verify whether the sequence has already being tested
        if chromo['seq'] in testedChrom:
            continue
        
        # record chromosome
        testedChrom.append(chromo['seq'])
        
        # simulate chromosome
        resultGA = AllocationRoutine_ForecastGA(initialWeek, orderList, itemType,chromo)
        chromosomes.append(resultGA)
        chromoID += 1
        
        # save chromosomes results
        GAresults.append((initialWeek, 0, chromoID, resultGA['chromo']['cID'], resultGA['excess'], resultGA['lateness'], \
                          resultGA['earliness'], resultGA['targetUtil'], resultGA['minUtil'],chromo['seq'] ))
            
        
    # start optimisation cycle    
    for gen in range(1,G.noGenGA):
        
        print 'generation', gen
        
        # selection: elitist selection with linear ranking procedure for completing the population
        chromosomes, bc = rankingElitist(chromosomes,G.elitistSelection)
        
        # save best chromosome for previous generation
        bestChromosome.append(deepcopy(bc))
        
        # check if the solution is different or the termination criterion is reached...done here to avoid ranking the results multiple times
        if compareChromosomes(bestChromosome,G.terminationGA):
            break
        
        # keep track of chromosomes with changes...for these chromosomes allocation would be required
        changeC = [0]*G.popSizeGA
        
        # cross-over: order2 cross-over is applied
        for item in range(G.popSizeGA):
            
            #print 'item', item
            # apply X-over based on X-over probability
            xOver = random.random()
            #print 'xOver', xOver
            
            if  item < G.popSizeGA-1 and xOver <= G.probXover:
                
                #print 'in for crossOver'
                chromosomes[item]['chromo']['seq'], chromosomes[item+1]['chromo']['seq'] = order2x(chromosomes[item]['chromo']['seq'], chromosomes[item+1]['chromo']['seq'])
                changeC[item] = 1   # both chromosomes have changes and they should be reassessed
                changeC[item+1] = 1
                
            mutation = random.random()
            #print 'mut', mutation
            # apply mutation based on mutation probability
            if mutation <= G.probMutation:
                
                #print 'in for mutation'
                chromosomes[item]['chromo']['seq'] = displacement(chromosomes[item]['chromo']['seq'])
                changeC[item] = 1
                
            # reassess the chromosome if it has been changed and has never been investigated (does not belong to testedChromosomes)
            #if changeC[item] and chromosomes[item]['chromo']['seq'] not in testedChrom:   #FIXME: se e`in tested non si hanno i risultati...si possono lasciare in bianco perche`counque non e`il milgiore cromosoma : 
                
            testedChrom.append(chromosomes[item]['chromo']['seq'])
            chromosomes[item]['chromo']['cID'] = chromoID
            chromoID += 1
            
            # simulate chromosome
            resultGA = AllocationRoutine_ForecastGA(initialWeek, orderList, itemType,chromosomes[item]['chromo'])
            chromosomes[item] = deepcopy(resultGA)
                
            # save chromosomes results
            GAresults.append((initialWeek, gen, item, chromosomes[item]['chromo']['cID'], chromosomes[item]['excess'], chromosomes[item]['lateness'], \
                              chromosomes[item]['earliness'], chromosomes[item]['targetUtil'], chromosomes[item]['minUtil'], chromosomes[item]['chromo']['seq']))
        
    # final ranking
    bestC = finalRanking(chromosomes+bestChromosome)

    AllocationRoutine_Forecast(initialWeek, orderList, itemType, bestC['chromo'])
    GAresults.append((initialWeek, bestC['chromo']['cID'], 'selected', bestC['chromo']['seq'], '', '', '','','',''))
    
    return GAresults
    
