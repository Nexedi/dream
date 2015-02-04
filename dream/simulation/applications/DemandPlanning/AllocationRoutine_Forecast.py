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
    
    
    EarlinessMA = {}
    LatenessMA = {}
    
    # repeat allocation procedure for all items in the list
    for order in seq['seq']:
        
        item = itemList[order]
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
            
            # check different MAs
            for week in weekList:
                
                # optimise MA allocation               
                spAllocation = Allocation_IP(item, week, previousAss, capacity,G.weightFactor)
#                print 'all', spAllocation
                # implement optimal MA solution
                for ma in spAllocation.keys():
                    if spAllocation[ma]:
                        Results = Allocation2(ma, spAllocation[ma], [week], capacity, G.incompleteBatches, earliness, lateness, Allocation, initialWeek)
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
                        EarlinessMA[ma] += max([0, initialWeek - week])*spAllocation[ma]
                        LatenessMA[ma] += max([0, week - initialWeek])*spAllocation[ma]
                            
                        previousAss[ma] += spAllocation[ma]
                        
                if qty <= 0:
                    break
            
            step += 1
        
        # confirm results 
        if qty <= 0:
            G.CurrentCapacityDict = Results['remainingCap']
            G.incompleteBatches = Results['remUnits']
#            print initialWeek, G.Earliness
            for maT in EarlinessMA:
                G.Earliness[initialWeek][maT]['qty'].append(item['Qty'])
                G.Earliness[initialWeek][maT]['earliness'].append(EarlinessMA[maT]/item['Qty'])
                G.Lateness[initialWeek][maT]['qty'].append(item['Qty'])
                G.Lateness[initialWeek][maT]['lateness'].append(LatenessMA[maT]/item['Qty'])
            G.orders[item['orderID']]['Allocation'] = Results['Allocation']
            G.orders[item['orderID']]['Excess'] = False
            chosenMA = []
            for allMA in Results['Allocation']:
                if allMA['ma'] not in chosenMA:
                    chosenMA.append(allMA['ma'])
            G.orders[item['orderID']]['chosenMA'] = chosenMA    
            
                           
    
            for allRep in Results['Allocation']:
                G.globalMAAllocation[allRep['ma']][allRep['week']][itemType][item['priority']] += allRep['units']
            
        
            if itemType == 'forecast':
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, Results['lateness'], Results['earliness']/item['Qty'], Results['Allocation']))
                
        
        else:
            G.Excess[item['sp']][initialWeek] += item['Qty']
            G.orders[item['orderID']]['Allocation'] = []
            G.orders[item['orderID']]['Excess'] = True
            G.orders[item['orderID']]['chosenMA'] = None
            if itemType == 'forecast':
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], None, 'NaN', 'NaN', 'None'))
