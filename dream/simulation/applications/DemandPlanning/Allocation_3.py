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
from math import ceil, fabs
from copy import deepcopy

def Allocation2(currentMA, qty, weekList, capIn, inBatches, earliness, lateness, Allocation, demandWeek):
    
    # allocate item on its own route    
    step = 0
    sufficient = False
    remainingUnits = qty
    
#        Allocation = [] #reports allocation results in the form of dcitionaries ('allocatedQty':..,'week':..) 
    currentCapacity = deepcopy(capIn)
    remUnits = deepcopy(inBatches)
    utilisation = {}
    for bottleneck in G.RouteDict[currentMA]:
        utilisation[bottleneck] = {}
        
    while sufficient == False:
        
        sufficient = True     #flag that shows if we have sufficient capacity
        
        # define the currentWeek
        currentWeek = weekList[step]
        
        # verify whether the qty is an exact multiple of the batch size
        surplus = qty%G.BatchSize[currentMA][currentWeek]
        roundDown = 0
        if surplus == 0:
                            
            #confirm the qty to be assigned
            correctedQty = remainingUnits
            
        else:                
            
            # if there is enough incomplete Batch units...use them and round down the qty to produce
            if remUnits[currentMA] >= surplus:                    
                correctedQty = remainingUnits - surplus 
                roundDown = 1               
               
            else:   # round up the qty to produce
                correctedQty = remainingUnits + G.BatchSize[currentMA][currentWeek] - surplus                     
        
#            # round the qty to exact multiples of the batch size
#            correctedQty = qty - (qty%G.BatchSize[currentMA][currentWeek])
#            if correctedQty == 0:
#                # FIXME: maybe excess units should be defined here
#                break

        # read the capacity that the MA requires
        requiredCapacity={}
        for x in G.RouteDict[currentMA]:
            requiredCapacity[x]=G.RouteDict[currentMA][x][currentWeek]*correctedQty

        # read the remaining capacity for the given week and subtract the required from it
        remainingCapacity={}
        for bottleneck in G.RouteDict[currentMA]:
            remainingCapacity[bottleneck]=currentCapacity[bottleneck][currentWeek]-requiredCapacity[bottleneck]
            # if we dropped below zero then the capacity is not sufficient
            if remainingCapacity[bottleneck]<0:
                sufficient=False           
        
        # check if there is sufficient capacity to process the order
        if sufficient:       
            
            remainingUnits = 0  
            #remainingUnits = max(remainingUnits, 0)
            for bottleneck in G.RouteDict[currentMA]:
                currentCapacity[bottleneck][currentWeek]=remainingCapacity[bottleneck]
                utilisation[bottleneck][currentWeek] = float(G.Capacity[bottleneck][currentWeek]['OriginalCapacity'] - currentCapacity[bottleneck][currentWeek])/G.Capacity[bottleneck][currentWeek]['OriginalCapacity']
            Allocation.append({'ma':currentMA, 'units':correctedQty, 'week':currentWeek})   
            if currentWeek > demandWeek:
                lateness += (step+1)*correctedQty
            elif currentWeek<demandWeek:
                earliness += (step+1)*correctedQty
            
            # if there is a surplus...update remUnits
            if surplus:
                
                if roundDown:
                    remUnits[currentMA] -= surplus
                else:
                    remUnits[currentMA] += G.BatchSize[currentMA][currentWeek] - surplus
                
                surplus = 0
                
        # if the capacity available is not sufficient, the max allocable qty is derived
        else:             

            # calculate max qty allocable
            excessUnits=0
            excess=0
            for bottleneck in remainingCapacity:
                if requiredCapacity[bottleneck]>0 and remainingCapacity[bottleneck]<0:
                    excessUnits = remainingCapacity[bottleneck]/G.RouteDict[currentMA][bottleneck][currentWeek]
                    if ceil(fabs(excessUnits))>excess:
                        excess = ceil(fabs(excessUnits))
                        
            # update remaining capacity
            assert(excess <= correctedQty)
            
            # round allocable qty to multiple of batch size...in this case is necessarily round down and remUnits are not affected
            allocableQty = correctedQty - excess
            allocableQty -= allocableQty%G.BatchSize[currentMA][currentWeek]
            remainingUnits -= allocableQty 
            assert(remainingUnits>0)               
            
            for bottleneck in G.RouteDict[currentMA]:
                currentCapacity[bottleneck][currentWeek]-=allocableQty*G.RouteDict[currentMA][bottleneck][currentWeek]
            
            Allocation.append({'ma':currentMA,'units':allocableQty, 'week':currentWeek})
            if currentWeek > demandWeek:
                lateness += (step+1)*allocableQty
            elif currentWeek < demandWeek:
                earliness += (step+1)*allocableQty
            
        if remainingUnits == 0:
            sufficient = True
        else:
            sufficient = False
            step += 1
            if step >= len(weekList):
                break            
            
    # if the entire qty has been assigned the allocation can be confirmed
#        if remainingUnits > 0:                
#            self.allocation = []
#            remainingUnits = qty
        
    return {'remainingUnits': remainingUnits, 'Allocation':Allocation, 'earliness':earliness, 'lateness':lateness, 'utilisation':utilisation, 'remUnits':remUnits, 'remainingCap':currentCapacity}
            
