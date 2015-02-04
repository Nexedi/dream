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
Created on 9 Dec 2014

@author: Anna
'''


from Globals import G
from Allocation_3 import Allocation2
from copy import deepcopy

def AllocationRoutine_Final(initialWeek, itemList, itemType, ant):
        
    excess = []
    
    # repeat allocation procedure for all items in the list
    for item in itemList:
        
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
        ma = ant[item['orderID']]
        chosenMA = None
        
        while step <= 3:
            
            if step == 2:                    
                weekList = [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
                
            if step == 3:
                weekList = [G.WeekList[i] for i in range(ind+1, min(G.planningHorizon,ind+G.maxLateness+1))]

            if len(weekList) == 0:
                step+=1
                continue
            
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
                chosenMA = ma
                           
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
        
    
