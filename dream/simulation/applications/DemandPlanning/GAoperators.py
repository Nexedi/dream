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
'''

from numpy import random

# defines order 2 cross over
def order2x(parent1, parent2):
    
    # verify that the parents have same length
    assert(len(parent1)==len(parent2))
    numGenes = len(parent1)
    
    # generate number of key positions
    numKP = random.random_integers(numGenes-1)
    
    # generate key positions
    keyPositions = []
    key = 0
    while key < numKP:
        possibleKey = random.random_integers(numGenes-1)
        if possibleKey not in keyPositions:
            keyPositions.append(possibleKey)
            key += 1
    
    # sort key positions
    keyPositions.sort()
    # generate first offspring
    offspring1 = offGeneration(keyPositions, parent1, parent2)
    
    # generate second offspring
    offspring2 = offGeneration(keyPositions, parent2, parent1)
    
    return offspring1, offspring2


    
# generates offspring for order2 crossover   
def offGeneration(keyPositions, parent1, parent2):
    
    # create list with parent2 alleles corresponding to key positions
    fromP2 = [parent2[i] for i in keyPositions]
    
    # generate offspring
    # copy from parent 1 if the allele is not contained in fromP2 otherwise copy from fromP2
    off = []
    c2=0
    for gene in range(len(parent1)):
        if parent1[gene] not in fromP2:
            off.append(parent1[gene])
        else:
            off.append(fromP2[c2])
            c2+=1
            
    return off



# mutation operator
def displacement(parent):
    
    # generate two key positions; second position should be different than first
    p1 = random.random_integers(len(parent)-2)

    while True:
        p2 = random.random_integers(len(parent)-2)
        if p2 != p1:
            break
    
    keyPos = [p1,p2]
    keyPos.sort()
    
    # generate third key position different than the min keyPos
    while True:
        p3 = random.random_integers(len(parent))-1
        if p3 != keyPos[0]:
            break

    offspring = [None for i in range(len(parent))]    
    
    slicedP = parent[:keyPos[0]]+parent[keyPos[1]+1:]
    
    # starting from p3 report the alleles between p1 and p2
    for i in range(keyPos[1]-keyPos[0]+1): 
        offspring[(p3+i)%len(parent)] = parent[keyPos[0]+i]
        
    startPos = (p3+keyPos[1]-keyPos[0]+1)%len(parent)
    
    # complete the offspring with alleles from the slicedP
    for i in range(len(slicedP)):
        offspring[(startPos+i)%len(parent)] = slicedP[i]
    
    return offspring


if __name__ == "__main__":
    order2x([1, 2, 3, 4],[1,3,2,4])