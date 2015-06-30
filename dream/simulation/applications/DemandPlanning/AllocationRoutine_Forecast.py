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
Created on 15 Dec 2014

@author: Anna
'''
from copy import deepcopy
from Globals import G
from AllocationForecast_IP import Allocation_IP
from Allocation_3 import Allocation2

def AllocationRoutine_Forecast(initialWeek, itemList, itemType, seq):
    
    
    
    # repeat allocation procedure for all items in the list
    for order in seq['seq']:
        
        item = itemList[order]
#        print 'item', item['orderID']
        
        EarlinessMA = {}
        LatenessMA = {}
        lateForecast = 0
        earlyForecast = 0
        #================================================
        # Allocation step 1...allocation at current Week
        #================================================
        
        Results = {}
        step = 1
        ind = G.WeekList.index(initialWeek)
        weekList = [initialWeek]
        weekLateness = [0]
        capacity = deepcopy(G.CurrentCapacityDict)
        incompleteBatches = deepcopy(G.incompleteBatches)
        qty = item['Qty']
        Allocation = []
        earliness = 0
        lateness = 0
        previousAss = {}
        for ma in G.SPlist[item['sp']]:
            previousAss[ma] = 0
            previousAss[ma] = incompleteBatches[ma]
#            print 'ma in', ma, incompleteBatches[ma]
            qty -= incompleteBatches[ma]
            # make use of incomplete batch units available
            incompleteBatches[ma] = 0
        
#        print 'order qty', qty   
        
        while step <= 3 and qty>0:
            
            if step == 2:                    
                weekList = [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
                weekLateness = [i-ind for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
                assert (len(weekList)==len(weekLateness))
                
            if step == 3:
                weekList = [G.WeekList[i] for i in range(ind+1, min(G.planningHorizon,ind+G.maxLateness+1))]
                weekLateness = [i-ind for i in range(ind+1, min(G.planningHorizon,ind+G.maxLateness+1))]
                
#            print 'weeklist', weekList
            if len(weekList) == 0:
                step+=1
                continue
            
            # check different MAs
            for weekIndex in range(len(weekList)):
                
                week = weekList[weekIndex]
                
                # optimise MA allocation               
                spAllocation, probStatus = Allocation_IP(item, week, previousAss, capacity,G.weightFactor)
#                print 'all', spAllocation
                # implement optimal MA solution
                for ma in spAllocation.keys():
                    if spAllocation[ma]:
                        Results = Allocation2(ma, spAllocation[ma], [week], capacity, incompleteBatches, earliness, lateness, Allocation, initialWeek)
                        assert (Results['remainingUnits'] == 0)
                        
                        # update variables
                        capacity = deepcopy(Results['remainingCap'])
                        qty -= spAllocation[ma]
                        Allocation = deepcopy(Results['Allocation'])
                        earliness = deepcopy(Results['earliness'])
                        lateness = deepcopy(Results['lateness'])
                        if ma not in EarlinessMA:
                            EarlinessMA[ma] = 0
                            LatenessMA[ma] = 0
                        
                        EarlinessMA[ma] += max([0, weekLateness[weekIndex]*(-1)])*spAllocation[ma]
                        LatenessMA[ma] += max([0, weekLateness[weekIndex]])*spAllocation[ma]     #week - initialWeek
                        
                        previousAss[ma] += spAllocation[ma]
                        
                if qty <= 0:
                    break
            
            step += 1
        
        # confirm results 
        if qty <= 0:
            
            minAss =item['Qty']*10
            maIB = None
            G.CurrentCapacityDict = Results['remainingCap']
            G.incompleteBatches = Results['remUnits']
#            print initialWeek, G.Earliness
            for maT in EarlinessMA:
#                assert(Results['remUnits'][maT]==0)
                G.Earliness[initialWeek][maT]['qty'].append(item['Qty'])
                G.Earliness[initialWeek][maT]['earliness'].append(EarlinessMA[maT]/item['Qty'])
                G.Lateness[initialWeek][maT]['qty'].append(item['Qty'])
                G.Lateness[initialWeek][maT]['lateness'].append(LatenessMA[maT]/item['Qty'])
                lateForecast += LatenessMA[maT]/item['Qty']
                earlyForecast += EarlinessMA[maT]/item['Qty']
                if previousAss[maT] <= minAss:
                    minAss = previousAss[maT]
                    maIB = maT
            
#            print 'ma ib', maIB, qty, cQty, item['Qty'], previousAss, EarlinessMA , [G.incompleteBatches[ma] for ma in G.SPlist[item['sp']]]
            if maIB != None:
                G.incompleteBatches[maIB] -= qty 
#            print [G.incompleteBatches[ma] for ma in G.SPlist[item['sp']]]
                
            G.orders[item['orderID']]['Allocation'] = Results['Allocation']
            G.orders[item['orderID']]['Excess'] = False
            chosenMA = []
            for allMA in Results['Allocation']:
                if allMA['ma'] not in chosenMA:
                    chosenMA.append(allMA['ma'])
            G.orders[item['orderID']]['chosenMA'] = chosenMA    
            
            if lateForecast:
                G.LateMeasures['noLateOrders'] += 1
                G.LateMeasures['lateness'].append(lateForecast)
                
            if earlyForecast:
                G.LateMeasures['noEarlyOrders'] += 1
                G.LateMeasures['earliness'].append(earlyForecast)            
                           
    
            for allRep in Results['Allocation']:
                G.globalMAAllocation[allRep['ma']][allRep['week']][itemType][item['priority']] += allRep['units']
                G.globalMAAllocationIW[allRep['ma']][initialWeek][itemType][item['priority']] += allRep['units']
            
        
            if itemType == 'forecast':
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, Results['lateness']/item['Qty'], Results['earliness']/item['Qty'], Results['Allocation']))
                
        
        else:
            G.Excess[item['sp']][initialWeek] += item['Qty']
            G.orders[item['orderID']]['Allocation'] = []
            G.orders[item['orderID']]['Excess'] = True
            G.orders[item['orderID']]['chosenMA'] = None
            G.globalMAAllocationIW[item['sp']][initialWeek][itemType][item['priority']] += item['Qty']
            G.LateMeasures['noExcess'] += 1
            G.LateMeasures['exUnits'] += item['Qty']
            if itemType == 'forecast':
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], None, 'NaN', 'NaN', 'None'))
