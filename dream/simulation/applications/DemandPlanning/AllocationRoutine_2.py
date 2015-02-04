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
Created on 27 Nov 2014

@author: Anna
'''

from Globals import G
from Allocation_3 import Allocation2
from numpy import mean, array, absolute, std
from operator import itemgetter
from copy import deepcopy

def AllocationRoutine2(initialWeek, itemList, itemType):            
        
    excess = []
    
    # repeat allocation procedure for all items in the list
    for item in itemList:
        
#        print 'item', item['orderID']
        
        #================================================
        # Allocation step 1...allocation at current Week
        #================================================
        
        Results = {}
        step = 1
        ind = G.WeekList.index(initialWeek)
        weekList = [initialWeek]
        capacity = deepcopy(G.CurrentCapacityDict)
        qty = item['Qty']
        Allocation = []
        earliness = 0
        lateness = 0
        
        while step <= 3:
            
            possibleSolutions = []
            if step == 2:                    
                weekList = [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
                
            if step == 3:
                weekList = [G.WeekList[i] for i in range(ind+1, min(G.planningHorizon,ind+G.maxLateness+1))]
            
            if len(weekList) == 0:
                step+=1
                continue
            
            # check different MAs
            for ma in item['MAlist']:
                
                if step > 1:                    
                    capacity = deepcopy(Results[ma]['remainingCap'])
                    qty = deepcopy(Results[ma]['remainingUnits'])
                    Allocation = deepcopy(Results[ma]['Allocation'])
                    earliness = deepcopy(Results[ma]['earliness'])
                    lateness = deepcopy(Results[ma]['lateness'])
                
                else:
                    capacity = deepcopy(G.CurrentCapacityDict)
                    qty = item['Qty']
                    Allocation = []
                    earliness = 0
                    lateness = 0
                    
                # try allocation to ma
                Results[ma] = Allocation2(ma, qty, weekList, capacity, G.incompleteBatches, earliness, lateness, Allocation, initialWeek)
                if Results[ma]['remainingUnits'] == 0:       # if the allocation is not successful delete the record of the allocation results
                    possibleSolutions.append(ma)
            
            # chose best MA
            if G.minDeltaUt:
                chosenMA = choseMA2(Results, possibleSolutions, weekList)
            else:
                chosenMA = choseMA(Results, possibleSolutions, weekList)
                            
            # confirm the solution
            if chosenMA != None:
                G.CurrentCapacityDict = Results[chosenMA]['remainingCap']
                G.incompleteBatches = Results[chosenMA]['remUnits']
                G.Earliness[initialWeek][chosenMA]['qty'].append(item['Qty'])
                G.Earliness[initialWeek][chosenMA]['earliness'].append(float(Results[chosenMA]['earliness'])/item['Qty'])
                G.Lateness[initialWeek][chosenMA]['qty'].append(item['Qty'])
                G.Lateness[initialWeek][chosenMA]['lateness'].append(float(Results[chosenMA]['lateness'])/item['Qty'])
                G.orders[item['orderID']]['Allocation'] = Results[chosenMA]['Allocation']
                G.orders[item['orderID']]['Excess'] = False
                G.orders[item['orderID']]['chosenMA'] = chosenMA
                
                for allRep in Results[chosenMA]['Allocation']:
                    G.globalMAAllocation[chosenMA][allRep['week']][itemType][item['priority']] += allRep['units']
                break
            
            step += 1
        
        if chosenMA == None:
            excess.append(item)
            G.Excess[item['sp']][initialWeek] += item['Qty']
            G.orders[item['orderID']]['Allocation'] = []
            G.orders[item['orderID']]['Excess'] = True
            G.orders[item['orderID']]['chosenMA'] = None
        
        # for orders add allocation information
        if itemType == 'order':
            if chosenMA == None:                    
                G.OrderResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Customer'], item['Qty'], item['priority'], chosenMA, 'NaN', 'NaN', 'None'))
            else:
                G.OrderResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Customer'], item['Qty'], item['priority'], chosenMA, Results[chosenMA]['lateness'], Results[chosenMA]['earliness'], Results[chosenMA]['Allocation']))

        if itemType == 'forecast':
            if chosenMA == None:                    
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, 'NaN', 'NaN', 'None'))
            else:
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, Results[chosenMA]['lateness'], Results[chosenMA]['earliness']/item['Qty'], Results[chosenMA]['Allocation']))
                
    return excess
            
        
def choseMA(allResults, possibleSolutions, weeklist):

    chosenMA = None
    
    # if there is only one solution, chose the only solution available
    if len(possibleSolutions) == 1:       
        chosenMA = possibleSolutions[0]
    
    # if there are more than one successful allocations choose between them
    if len(possibleSolutions) > 1:
        
        res = []
        for ma in possibleSolutions:
            minUtil = []
            targetUtil = []
            for week in weeklist:
                for bn in allResults[ma]['utilisation']:
                    if week in allResults[ma]['utilisation'][bn]:
                        minUtil.append(max(0, (G.Capacity[bn][week]['minUtilisation']-allResults[ma]['utilisation'][bn][week])/G.Capacity[bn][week]['minUtilisation']))
                        targetUtil.append((G.Capacity[bn][week]['targetUtilisation']-allResults[ma]['utilisation'][bn][week])/G.Capacity[bn][week]['targetUtilisation'])
                
            res.append([ma, allResults[ma]['lateness'], std(array(targetUtil)), std(array(minUtil)), allResults[ma]['earliness']])
            
        # order results...1st criterion: target utilisation (stdDev), 2nd criterion: min utilisation(stdDev)
        sortedMA = sorted(res, key=itemgetter(1, 2, 3, 4))
        chosenMA = sortedMA[0][0]
        
    return chosenMA


def choseMA2(allResults, possibleSolutions, weeklist):      # more similar to ACO selection criteria

    chosenMA = None
    
    # if there is only one solution, chose the only solution available
    if len(possibleSolutions) == 1:       
        chosenMA = possibleSolutions[0]
    
    # if there are more than one successful allocations choose between them
    if len(possibleSolutions) > 1:
        
        res = []
        for ma in possibleSolutions:
            minUtil = []
            targetUtil = []
            for bottleneck in G.Bottlenecks:
                minU = []
                targetU = []
                for week in weeklist:
                    utilisation = float(G.Capacity[bottleneck][week]['OriginalCapacity'] - allResults[ma]['remainingCap'][bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity']
                    minU.append(max(0, (G.Capacity[bottleneck][week]['minUtilisation']-utilisation)/G.Capacity[bottleneck][week]['minUtilisation']))
                    targetU.append((utilisation - G.Capacity[bottleneck][week]['targetUtilisation'])/G.Capacity[bottleneck][week]['targetUtilisation'])
                    
                minUtil.append(mean(array(minU)))
                targetUtil.append(mean(absolute(targetU)))
                        
            res.append([ma, allResults[ma]['lateness'], mean(array(targetUtil)), mean(array(minUtil)), allResults[ma]['earliness']])
            
        # order results...1st criterion: target utilisation (stdDev), 2nd criterion: min utilisation(stdDev)
        sortedMA = sorted(res, key=itemgetter(1, 2, 3, 4))
        chosenMA = sortedMA[0][0]
        
    return chosenMA
