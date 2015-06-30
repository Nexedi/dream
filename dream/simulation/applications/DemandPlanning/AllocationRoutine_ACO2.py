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
Created on 28 Jan 2015

@author: Anna
'''

from Globals import G
from Allocation_3 import Allocation2
from UtilisationCalculation import utilisationCalc2, utilisationCalc1, utilisationCalc3
from copy import deepcopy

# allocates orders of a give week/priority level implementing the ant choice for MAs
def AllocationRoutine_ACO(initialWeek, itemList, itemType, ant):
           
    ACOcapacityDict = deepcopy(G.CurrentCapacityDict)
    ACOincompleteBatches = deepcopy(G.incompleteBatches)
    ACOearliness = 0
    ACOlateness = 0
    ACOtargetUtil = 0
    ACOminUtil = 0
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
        capacity = deepcopy(ACOcapacityDict)
        qty = item['Qty']
        Allocation = []
        earliness = 0
        lateness = 0
        # FIXME: ma 
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
            
            # check different MAs
            if step > 1:                    
                capacity = deepcopy(Results[ma]['remainingCap'])
                inBatches = deepcopy(Results[ma]['remUnits'])
                qty = deepcopy(Results[ma]['remainingUnits'])
                Allocation = deepcopy(Results[ma]['Allocation'])
                earliness = deepcopy(Results[ma]['earliness'])
                lateness = deepcopy(Results[ma]['lateness'])
            
            else:
                capacity = deepcopy(ACOcapacityDict)
                inBatches = deepcopy(ACOincompleteBatches)
                qty = item['Qty']
                Allocation = []
                earliness = 0
                lateness = 0
                
            # try allocation to ma
            Results[ma] = Allocation2(ma, qty, weekList, capacity, inBatches, earliness, lateness, Allocation, initialWeek)
            if Results[ma]['remainingUnits'] == 0:       # if the allocation is not successful delete the record of the allocation results
                chosenMA = ma
                            
            # confirm the solution
            if chosenMA != None:
                ACOcapacityDict = Results[chosenMA]['remainingCap']
                ACOincompleteBatches = Results[chosenMA]['remUnits']
                ACOearliness += float(Results[chosenMA]['earliness'])/item['Qty'] 
                ACOlateness += float(Results[chosenMA]['lateness'])/item['Qty'] 
                break

            step += 1
        
        if chosenMA == None:
            ACOexcess += item['Qty'] 
    
    if G.minDeltaUt:
        ACOtargetUtil, ACOminUtil = utilisationCalc1(ACOcapacityDict, initialWeek, ind)
    else:
        ACOtargetUtil, ACOminUtil = utilisationCalc3(ACOcapacityDict, initialWeek, ind)
        
    return {'ant':ant, 'excess':ACOexcess, 'earliness':ACOearliness, 'lateness':ACOlateness, 'targetUtil':ACOtargetUtil, 'minUtil':ACOminUtil}


