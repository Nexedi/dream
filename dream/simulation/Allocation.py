'''
Created on 21 Aug 2013

@author: Anna
'''

import math
import numpy
import random
from Globals import G

class Allocation():
    def __init__(self, itemList, week, altRoutes, excBuffer):
        self.week = week
        self.altRoutes = altRoutes
        self.itemList = itemList
        self.excBuffer = excBuffer        
        
    def Run(self):
        
        for CurrentMA in self.itemList:    
            
            # call the allocation methods based on the step (e.g. allocation on same route or allocation on alternative routes)
            if self.altRoutes == 1:
                self.alternativeRoutes(CurrentMA)
                
            else:
                self.allocationStd(CurrentMA)                                
            
            # put items in output buffer (temporary buffer for excess units to be allocated)
            if CurrentMA.qty > 0:
                self.excBuffer.append(CurrentMA)                            
                  

    # allocate item on its own route    
    def allocationStd(self, MA):
        sufficient=True     #flag that shows if we have sufficient capacity
        # read the capacity that the MA requires
        requiredCapacity={}
        for x in G.RouteDict[MA.MAid]['route']:
            requiredCapacity[x]=G.RouteDict[MA.MAid]['route'][x]*MA.qty
        
        # read the remaining capacity for thegiven week and subtract the required from it
        remainingCapacity={}
        for bottleneck in G.CurrentCapacityDict:
            remainingCapacity[bottleneck]=G.CurrentCapacityDict[bottleneck][self.week]-requiredCapacity[bottleneck]
            # if we dropped below zero then the capacity is not sufficient
            if remainingCapacity[bottleneck]<0:
                sufficient=False
        
        # check if there is sufficient capacity to process the order
        if sufficient:            
            # update remaining capacity            
            allocableQty = MA.qty
            if MA.qty >= G.minPackingSize:
                for bottleneck in G.CurrentCapacityDict:
                     G.CurrentCapacityDict[bottleneck][self.week]=remainingCapacity[bottleneck]
        
        # if the capacity available is not sufficient, the max allocable qty is derived
        else:             
            # calculate max qty allocable
            #excessUnits = [0 for i in range(len(requiredCapacity))]
            excessUnits={}
            excess=0
            for bottleneck in remainingCapacity:
                if requiredCapacity[bottleneck]>0 and remainingCapacity[bottleneck]<0:
                    excessUnits= remainingCapacity[bottleneck]/G.RouteDict[MA.MAid]['route'][bottleneck]
                    if math.ceil(math.fabs(excessUnits))>excess:
                        excess = math.ceil(math.fabs(excessUnits))
           
            
            # update remaining capacity
            assert(excess <= MA.qty or MA.qty < G.minPackingSize)
            allocableQty = MA.qty - excess
            
            if allocableQty >= G.minPackingSize:
                #rCap = numpy.array(G.currentCapacity[self.week]) - numpy.multiply(allocableQty,G.route[MA.MAid])
                for bottleneck in G.CurrentCapacityDict:
                     G.CurrentCapacityDict[bottleneck][self.week]-=allocableQty*G.RouteDict[MA.MAid]['route'][bottleneck]
                   
        # update attributes/variables affected by allocation
        if allocableQty >= G.minPackingSize:
            MA.qty -= allocableQty
            MA.minQty = max([0, MA.minQty - allocableQty])
            
            # update allocation output variable
            # distinguish case of FutureDemand from PPOSdemand
            if MA.future == 1:  
                G.AllocationFuture[G.replication].append([MA.orderID, MA.MAid, allocableQty, self.week+1])
                G.FutureLateness[G.replication] += max([0, self.week - MA.originalWeek])*allocableQty
                G.FutureEarliness[G.replication] += max([0, MA.originalWeek - self.week])*allocableQty                
            else:
                G.AllocationPPOS[G.replication].append([MA.orderID, MA.MAid, allocableQty, self.week+1])
                G.PPOSLateness[G.replication] += max([0, self.week - MA.originalWeek])*allocableQty
                G.PPOSEarliness[G.replication] += max([0, MA.originalWeek - self.week])*allocableQty
        
    def alternativeRoutes(self, MA):
        sufficient=False     #flag that shows if we have sufficient capacity
        # identify MAs with the same SP as the MA investigated
        alternativeMADict={}   #FIXME: the PPOS attribute can be used instead for the current MA
        # loop through the MAinfo
        for alernativeMA in G.RouteDict:
            # if it is the same MA do not consider it
            if alernativeMA==MA.MAid:
                continue
            # if the alternative MA is of the same SP add it to the list
            PPOS=G.RouteDict[alernativeMA]['PPOS'] 
            SP=G.RouteDict[alernativeMA]['SP']
            if PPOS==MA.PPOSid and SP==MA.SPid:                
                alternativeMADict[alernativeMA]=G.RouteDict[alernativeMA]
        
        # calculate max number of units for each alternative MA
        maxUnits = {}    
        for alternativeMA in alternativeMADict:
            MAunits=[]
            for routeElement in alternativeMADict[alternativeMA]['route']:
                units=alternativeMADict[alternativeMA]['route'][routeElement]
                if units!= 0:
                    MAunits.append(G.CurrentCapacityDict[routeElement][self.week]/units)
                    sufficient=True
            maxUnits[alternativeMA]=math.floor(min(MAunits))
        
        # choose MA with max number of units
        if maxUnits and sufficient:
            maxU=0
            maxID=[]
            for MAid in maxUnits:
                if maxUnits[MAid]>maxU:
                    maxU=maxUnits[MAid]
                    maxID = [MAid]
                if maxUnits[MAid]==maxU:
                    maxID.append(MAid)
                
            # choose MA randomly among those with max number of units
            chosenMAId = random.choice(maxID)

            allocableQty = min([maxU, MA.qty])
            
            if allocableQty >= G.minPackingSize:               
                for bottleneck in G.CurrentCapacityDict:
                    G.CurrentCapacityDict[bottleneck][self.week]-=allocableQty*G.RouteDict[chosenMAId]['route'][bottleneck]
                # update attributes/variables affected by allocation
                MA.qty -= allocableQty
                MA.minQty = max([0, MA.minQty - allocableQty])
        
                # update allocation output variable
                # distinguish case of FutureDemand from PPOSdemand
                if MA.future == 1: 
                    G.AllocationFuture[G.replication].append([MA.orderID, chosenMAId, allocableQty, self.week+1])
                    G.FutureLateness[G.replication] += max([0, self.week - MA.originalWeek])*allocableQty
                    G.FutureEarliness[G.replication] += max([0, MA.originalWeek - self.week])*allocableQty
                else:
                    G.AllocationPPOS[G.replication].append([MA.orderID, chosenMAId, allocableQty, self.week+1])
                    G.PPOSLateness[G.replication] += max([0, self.week - MA.originalWeek])*allocableQty
                    G.PPOSEarliness[G.replication] += max([0, MA.originalWeek - self.week])*allocableQty
        
        