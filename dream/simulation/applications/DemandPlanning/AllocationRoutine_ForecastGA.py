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
Created on 30 Jan 2015

@author: Anna

allocates the forecast demand following the SP sequence order provided in input...does not modify global variables
'''


from copy import deepcopy
from Globals import G
from AllocationForecast_IP import Allocation_IP
from Allocation_3 import Allocation2
from UtilisationCalculation import utilisationCalc1, utilisationCalc2
from math import ceil

def AllocationRoutine_ForecastGA(initialWeek, itemList, itemType, chromo):

    GAexcess = 0
    GAcapacityDict = deepcopy(G.CurrentCapacityDict)
    GAincompleteBatches = deepcopy(G.incompleteBatches)
    GAearliness = 0
    GAlateness = 0
    GAtargetUtil = 0
    GAminUtil = 0
    
    # repeat allocation procedure for all items in the list
    for order in chromo['seq']:
        
        item=itemList[order]
        
        print 'item', item['orderID']
        
        #================================================
        # Allocation step 1...allocation at current Week
        #================================================
        
        # variables created for one specific order
        # will be confirmed in the GA variables provided that there is enough capacity to allocate the entire order (possibly across different weeks)
        Results = {}
        step = 1
        ind = G.WeekList.index(initialWeek)
        weekList = [initialWeek]
        capacity = deepcopy(GAcapacityDict)
        inBatches = deepcopy(GAincompleteBatches)
        qty = item['Qty']
        Allocation = []
        earliness = 0
        lateness = 0
        previousAss = {}
        for ma in G.SPlist[item['sp']]:
            previousAss[ma] = 0

        
        while step <= 3 and qty>0:
            
            if step == 2:                    
                weekList = [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
                
            if step == 3:
                weekList = [G.WeekList[i] for i in range(ind+1, min(G.planningHorizon,ind+G.maxLateness+1))]
            
#            print 'weeklist', weekList
            if len(weekList) == 0:
                step+=1
                continue
            
            # allocate requested qty 
            for week in weekList:
                
                # optimise MA allocation at current week        
                spAllocation, probStatus = Allocation_IP(item, week, previousAss, capacity, G.weightFactor)
                                       
                    
                # implement optimal MA solution to update temporary variables
                for ma in spAllocation.keys():
                    
                    if probStatus == 'Optimal':
                        allocatedQty = spAllocation[ma]
                    else:
                        allocatedQty = ceil(spAllocation[ma])
                    
                    if spAllocation[ma]:
                        
                        #print 'spAllocation', ma, spAllocation[ma], inBatches[ma]
                        Results = Allocation2(ma, allocatedQty, [week], capacity, inBatches, earliness, lateness, Allocation, initialWeek)
                        #print 'rem units', Results['remainingUnits']
                        
                        if probStatus == 'Optimal':
                            assert (Results['remainingUnits'] == 0)
                        else:
                            allocatedQty -= Results['remainingUnits']
                        
                        # update order variables
                        capacity = deepcopy(Results['remainingCap'])
                        inBatches = deepcopy(Results['remUnits'])
                        qty -= allocatedQty
                        Allocation = deepcopy(Results['Allocation'])
                        earliness = deepcopy(Results['earliness'])
                        lateness = deepcopy(Results['lateness'])
                            
                        previousAss[ma] += allocatedQty
                
                # if order has been fully allocated update GA variables        
                if qty <= 0:
                    GAcapacityDict = deepcopy(capacity)
                    GAincompleteBatches = inBatches
                    GAearliness += earliness/item['Qty']
                    GAlateness += lateness/item['Qty']                    
                    break
            
            step += 1
        
        # if order can not been confirmed then update the GA excess variable
        if qty > 0:
            GAexcess += item['Qty']
    
    if G.minDeltaUt:       
        GAtargetUtil, GAminUtil = utilisationCalc1(GAcapacityDict, initialWeek, ind)
    else:
        GAtargetUtil, GAminUtil = utilisationCalc2(GAcapacityDict, initialWeek, ind)
        
    return {'chromo':chromo, 'excess':GAexcess, 'earliness':GAearliness, 'lateness':GAlateness, 'targetUtil':GAtargetUtil, 'minUtil':GAminUtil}


        