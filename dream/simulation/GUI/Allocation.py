'''
Created on 21 Aug 2013

@author: Anna
'''

import math
import numpy
import random
from dream.simulation.Globals import G

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
        requiredCapacity = [x*MA.qty for x in G.route[MA.MAid]]
        
        remainingCapacity = numpy.array(G.currentCapacity[self.week]) - numpy.array(requiredCapacity)
        remainingCapacity = remainingCapacity.tolist()
        
        # check if there is sufficient capacity to process the order
        if min(remainingCapacity) >= 0:
            
            # update remaining capacity            
            allocableQty = MA.qty
            if MA.qty >= G.minPackingSize:
                G.currentCapacity[self.week] = remainingCapacity
            
        
        # if the capacity available is not sufficient, the max allocable qty is derived
        else:
               
            # calculate max qty allocable
            excessUnits = [0 for i in range(len(requiredCapacity))]
            for i in range(len(remainingCapacity)):
                if requiredCapacity[i]>0 and remainingCapacity[i]<0:
                    excessUnits[i] = remainingCapacity[i]/G.route[MA.MAid][i]            
            excess = math.ceil(math.fabs(min(excessUnits)))
            
            # update remaining capacity
            assert(excess <= MA.qty or MA.qty < G.minPackingSize)
            allocableQty = MA.qty - excess
            
            if allocableQty >= G.minPackingSize:
                rCap = numpy.array(G.currentCapacity[self.week]) - numpy.multiply(allocableQty,G.route[MA.MAid])
                G.currentCapacity[self.week] = rCap.tolist()     
                   
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
        
        # identify MAs with the same SP as the MA investigated
        MAlist=[]   #FIXME: the PPOS attribute can be used instead for the current MA
        
        
        for i  in G.PPOSlist:
            if i != MA.MAid and G.PPOSlist[i]['SP'] == G.PPOSlist[MA.MAid]['SP']:          # and G.PPOSlist[i][2] != G.PPOSlist[MA.MAid][2]:
                MAlist.append(i)
        
        # calculate max number of units for each alternative MA
        maxUnits = []    
        for i in MAlist:
            i=int(i)
            MAunits=[]
            for j in range(len(G.route[i])):
                if G.route[i][j] != 0:
                    MAunits.append(G.currentCapacity[self.week][j]/G.route[i][j])
            maxUnits.append(math.floor(min(MAunits)))
            
        # choose MA with max number of units
        if len(maxUnits) != 0 and max(maxUnits) != 0:
            
            maxU = maxUnits[0]
            maxID = [0]
            
            if len(maxUnits) > 1:
                for i in range(1,len(maxUnits)):
                    if maxUnits[i] > maxU:
                        maxU = maxUnits[i]
                        maxID = [i]
                    if maxUnits[i] == maxU:
                        maxID.append(i)
                
            # choose MA randomly among those with max number of units
            x = random.choice(maxID)
            
            allocableQty = min([maxU, MA.qty])
            
            if allocableQty >= G.minPackingSize:
                # update remaining capacity
                remCap = numpy.array(G.currentCapacity[self.week]) - allocableQty* numpy.array(G.route[MAlist[x]])
                G.currentCapacity[self.week] = remCap.tolist()
                       
                # update attributes/variables affected by allocation
                MA.qty -= allocableQty
                MA.minQty = max([0, MA.minQty - allocableQty])
        
                # update allocation output variable
                # distinguish case of FutureDemand from PPOSdemand
                if MA.future == 1: 
                    G.AllocationFuture[G.replication].append([MA.orderID, MAlist[x], allocableQty, self.week+1])
                    G.FutureLateness[G.replication] += max([0, self.week - MA.originalWeek])*allocableQty
                    G.FutureEarliness[G.replication] += max([0, MA.originalWeek - self.week])*allocableQty
                else:
                    G.AllocationPPOS[G.replication].append([MA.orderID, MAlist[x], allocableQty, self.week+1])
                    G.PPOSLateness[G.replication] += max([0, self.week - MA.originalWeek])*allocableQty
                    G.PPOSEarliness[G.replication] += max([0, MA.originalWeek - self.week])*allocableQty
                    
 
        
        