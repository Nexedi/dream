'''
Created on 22 Apr 2015

@author: Anna
'''
from Globals import G
from Allocation_3 import Allocation2
from copy import deepcopy
from numpy import mean, array, absolute, std
from operator import itemgetter
from UtilisationCalculation import utilisationCalc2, utilisationCalc1, utilisationCalc3

def AllocationRoutine_Final(initialWeek, itemList, itemType, ant):
        
    excess = []
    builtAnt = {}
    ACOearliness = 0
    ACOlateness = 0
    ACOexcess = 0

    
    # repeat allocation procedure for all items in the list
    for item in itemList:
        
        #================================================
        # Allocation step 1...allocation at current Week
        #================================================
        
        Results = {}
        step = 1
        ind = G.WeekList.index(initialWeek)
        weekList = [initialWeek]
        weekListUtCalc = [initialWeek]
        capacity = deepcopy(G.CurrentCapacityDict)
        qty = item['Qty']
        Allocation = []
        earliness = 0
        lateness = 0
        #ma = ant[item['orderID']]
        chosenMA = None
        possibleSolutions = []
        lateForecast = 0
        earlyForecast = 0
        
         
        while step <= 3:
            
            if step == 2:                    
                weekList = [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
                weekListUtCalc += weekList
                
            if step == 3:
                weekList = [G.WeekList[i] for i in range(ind+1, min(G.planningHorizon,ind+G.maxLateness+1))]

            if len(weekList) == 0:
                step+=1
                continue
            
            # check different MAs
            for ma in item['MAlist']:
                
                if ma not in possibleSolutions:
                
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
                               
            if len(possibleSolutions) == len(item['MAlist']):
                break                
            step += 1
            
        # choose best MA
        if G.minDeltaUt:
            chosenMA2, orderedMAlist = choseMA2(Results, possibleSolutions, item['MAlist'], weekListUtCalc)
        else:
            chosenMA2, orderedMAlist = choseMA(Results, possibleSolutions, item['MAlist'], weekListUtCalc)
        
        oMAlist2 = [ix[0] for ix in orderedMAlist]
        
        if ant == 0:
            chosenMA = chosenMA2
            
        else:
            if ant[item['orderID']] in possibleSolutions:
                chosenMA = ant[item['orderID']]
                # riordinare la orderedMAlist per portare in chosenMA (da ACO) al primo posto
                if oMAlist2[0] != chosenMA:
                    tempMAlist = [chosenMA]
                    for oMA in oMAlist2:
                        if oMA != chosenMA:
                            tempMAlist.append(oMA)
                    oMAlist2 = tempMAlist
        
        builtAnt[item['orderID']]=chosenMA       
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
            G.orders[item['orderID']]['orderedList'] = oMAlist2
            ACOearliness += float(Results[chosenMA]['earliness'])/item['Qty'] 
            ACOlateness += float(Results[chosenMA]['lateness'])/item['Qty'] 


            if Results[chosenMA]['lateness']:
                G.LateMeasures['noLateOrders'] += 1
                G.LateMeasures['lateness'].append(float(Results[chosenMA]['lateness'])/item['Qty'])
                
            if Results[chosenMA]['earliness']:
                G.LateMeasures['noEarlyOrders'] += 1
                G.LateMeasures['earliness'].append(float(Results[chosenMA]['earliness'])/item['Qty'])            
            
            for allRep in Results[chosenMA]['Allocation']:
                G.globalMAAllocation[chosenMA][allRep['week']][itemType][item['priority']] += allRep['units']
                G.globalMAAllocationIW[chosenMA][initialWeek][itemType][item['priority']] += allRep['units']
        
        else:
            excess.append(item)
            G.Excess[item['sp']][initialWeek] += item['Qty']
            G.orders[item['orderID']]['Allocation'] = []
            G.orders[item['orderID']]['Excess'] = True
            G.orders[item['orderID']]['chosenMA'] = None
            G.orders[item['orderID']]['orderedList'] = oMAlist2
            G.LateMeasures['noExcess'] += 1
            G.LateMeasures['exUnits'] += item['Qty']
            G.globalMAAllocationIW[item['sp']][initialWeek][itemType][item['priority']] += item['Qty']
            ACOexcess += item['Qty']
        
        # for orders add allocation information
        if itemType == 'order':
            if chosenMA == None:                    
                G.OrderResults.append((item['orderID'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, oMAlist2, 'NaN', 'NaN', 'None'))
                mList = ''
                for i in range(len(oMAlist2)):
                    if i>0:
                        mList += ', '
                    mList += oMAlist2[i]                
                G.OrderResultsShort.append((item['orderID'], mList))
            else:
                G.OrderResults.append((item['orderID'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, oMAlist2, Results[chosenMA]['lateness'], Results[chosenMA]['earliness'], Results[chosenMA]['Allocation']))
                mList = ''
                for i in range(len(oMAlist2)):
                    if i>0:
                        mList += ', '
                    mList += oMAlist2[i]                
                G.OrderResultsShort.append((item['orderID'], mList))
                
        if itemType == 'forecast':
            if chosenMA == None:                    
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, orderedMAlist, 'NaN', 'NaN', 'None'))
            else:
                G.forecastResults.append((item['ppos'], item['sp'], item['MAlist'], item['Week'], item['Qty'], item['priority'], chosenMA, orderedMAlist, Results[chosenMA]['lateness'], Results[chosenMA]['earliness']/item['Qty'], Results[chosenMA]['Allocation']))

    if G.minDeltaUt:
        ACOtargetUtil, ACOminUtil = utilisationCalc1(G.CurrentCapacityDict, initialWeek, ind)
    else:
        ACOtargetUtil, ACOminUtil = utilisationCalc2(G.CurrentCapacityDict, initialWeek, ind)
    
    return {'ant':builtAnt, 'excess':ACOexcess, 'earliness':ACOearliness, 'lateness':ACOlateness, 'targetUtil':ACOtargetUtil, 'minUtil':ACOminUtil}

def choseMA(allResults, possibleSolutions, MAlist, weeklist):

    chosenMA = None

    if len(MAlist) > 1:
            
        res = []
        for ma in MAlist:
            minUtil = []
            targetUtil = []
            for week in weeklist:
                for bn in allResults[ma]['utilisation']:
                    if week in allResults[ma]['utilisation'][bn]:
                        if G.Capacity[bn][week]['minUtilisation']:
                            minUtil.append(max(0, (G.Capacity[bn][week]['minUtilisation']-allResults[ma]['utilisation'][bn][week])/G.Capacity[bn][week]['minUtilisation']))
                        else:
                            minUtil.append(max(0, (G.Capacity[bn][week]['minUtilisation']-allResults[ma]['utilisation'][bn][week])))
                        
                        if G.Capacity[bn][week]['targetUtilisation']:
                            targetUtil.append((G.Capacity[bn][week]['targetUtilisation']-allResults[ma]['utilisation'][bn][week])/G.Capacity[bn][week]['targetUtilisation'])
                        else:
                            targetUtil.append(G.Capacity[bn][week]['targetUtilisation']-allResults[ma]['utilisation'][bn][week])
                
            res.append([ma, allResults[ma]['remainingUnits'], allResults[ma]['lateness'], std(array(targetUtil)), std(array(minUtil)), allResults[ma]['earliness']])
    
        # order results...1st criterion: target utilisation (stdDev), 2nd criterion: min utilisation(stdDev)
        sortedMA = sorted(res, key=itemgetter(1, 2, 3, 4, 5))
    
    else: 
        sortedMA = [MAlist]
            
    # if there is only one solution, chose the only solution available
    if len(possibleSolutions) == 1:       
        chosenMA = possibleSolutions[0]
    
    # if there are more than one successful allocations choose between them
    if len(possibleSolutions) > 1:            
        chosenMA = sortedMA[0][0]
        assert(chosenMA in possibleSolutions)
        
    return chosenMA, sortedMA


def choseMA2(allResults, possibleSolutions, MAlist, weeklist):      # more similar to ACO selection criteria

    chosenMA = None
    
    if len(MAlist) > 1:
            
        res = []
        for ma in MAlist:
            minUtil = []
            targetUtil = []
            for bottleneck in G.Bottlenecks:
                minU = []
                targetU = []
                for week in weeklist:
                    utilisation = float(G.Capacity[bottleneck][week]['OriginalCapacity'] - allResults[ma]['remainingCap'][bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity']
                    if G.Capacity[bottleneck][week]['minUtilisation']:
                        minU.append(max(0, (G.Capacity[bottleneck][week]['minUtilisation']-utilisation)/G.Capacity[bottleneck][week]['minUtilisation']))
                    else:
                        minU.append(max(0, (G.Capacity[bottleneck][week]['minUtilisation']-utilisation)))
                    if G.Capacity[bottleneck][week]['targetUtilisation']:
                        targetU.append((utilisation - G.Capacity[bottleneck][week]['targetUtilisation'])/G.Capacity[bottleneck][week]['targetUtilisation'])
                    else:
                        targetU.append((utilisation - G.Capacity[bottleneck][week]['targetUtilisation']))
                        
                    
                minUtil.append(mean(array(minU)))
                targetUtil.append(mean(absolute(targetU)))
                        
            res.append([ma, allResults[ma]['remainingUnits'], allResults[ma]['lateness'], mean(array(targetUtil)), mean(array(minUtil)), allResults[ma]['earliness']])

        # order results...1st criterion: target utilisation (stdDev), 2nd criterion: min utilisation(stdDev)
        sortedMA = sorted(res, key=itemgetter(1, 2, 3, 4, 5))

    else:
        sortedMA = [MAlist]
        
    # if there is only one solution, chose the only solution available
    if len(possibleSolutions) == 1:       
        chosenMA = possibleSolutions[0]
    
    # if there are more than one successful allocations choose between them
    if len(possibleSolutions) > 1:            
        chosenMA = sortedMA[0][0]
        assert(chosenMA in possibleSolutions)
        
    return chosenMA, sortedMA
    