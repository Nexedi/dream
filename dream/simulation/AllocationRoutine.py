'''
Created on 5 Sep 2013

@author: Anna
'''

from Globals import G
from Allocation import Allocation
from JobMA import JobMA

class AllocationRoutine():
    def __init__(self, initialWeek, itemType):
        self.initialWeek = initialWeek
        self.itemType = itemType
        self.week = self.initialWeek
        self.internalBuffer = []
        self.minBuffer = []

        
    def Run(self):        
        
        #verify if there is any item to be allocated at self.weeek (originally)
        noItems = self.checkNumberOfItems()
        
        # if there are items of that week, start the allocation routine
        if noItems:            
            
            #====================================
            # step 1: same route, same week
            #====================================           
            # get all the items of self.week and activate the allocation process
            
            #G.filterItem = self.itemType
            #G.filterWeek = self.week
            #itemsToBeAssigned = filterWeek(G.Buffer[G.replication])
            
            #itemsToBeAssigned = [x for x in G.Buffer[G.replication] if (x.originalWeek == self.week and x.future == self.itemType)]
            itemsToBeAssigned = self.filterWeek(G.Buffer[G.replication])
            assert len(itemsToBeAssigned) == noItems
            sameRouteSameWeek = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=0, excBuffer=self.internalBuffer)
            sameRouteSameWeek.Run()
            
            #==========================================
            # step 2: same route, previous weeks
            #==========================================
            # proceed only if there are excess items
            self.week -= 1
            while self.week >= 0 and (self.initialWeek - self.week) <= G.maxEarliness and len(self.internalBuffer):   

                itemsToBeAssigned = self.internalBuffer
                self.internalBuffer = []
                sameRoutePreviousWeeks = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=0, excBuffer=self.internalBuffer)
                sameRoutePreviousWeeks.Run()
                self.week -= 1
                
            #===============================================================
            # step 3: separate min quantity of excess demand from unconstrained qty
            #===============================================================
            # proceed only if there are excess items
            if len(self.internalBuffer):   

                for item in self.internalBuffer:
                    # if the item presents min qty then create a new item and store it into minBuffer
                    if item.minQty:
                        newJob = JobMA(item.orderID, item.MAid, item.SPid, item.PPOSid, item.minQty, item.minQty, item.originalWeek, item.future)
                        self.minBuffer.append(newJob)
                        item.qty = item.qty - item.minQty
                        item.minQty = 0
                        if item.qty == 0:
                            self.internalBuffer.remove(item)           
                
            #============================================         
            # step 4: allocate min qty to later weeks
            #============================================
            self.week = self.initialWeek + 1
            while self.week < G.planningHorizon and (self.week - self.initialWeek) <= G.maxLateness and len(self.minBuffer):  
                
                itemsToBeAssigned = self.minBuffer
                self.minBuffer = []
                sameRouteLaterWeeks = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=0, excBuffer=self.minBuffer)
                sameRouteLaterWeeks.Run()
                self.week += 1
            
            # any excess items left in the minBuffer should be transferred into the global minBuffer
            if len(self.minBuffer): 
                if self.itemType == 1:
                    G.ExcessFutureMinBuffer[G.replication] = self.minBuffer
                else:
                    G.ExcessPPOSminBuffer[G.replication] = self.minBuffer
                    
                self.minBuffer = []
                    
            #========================================
            # step 5: alternative route, same week
            #========================================
            self.week = self.initialWeek
            if len(self.internalBuffer):  

                itemsToBeAssigned = self.internalBuffer
                self.internalBuffer = []
                altRouteSameWeek = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=1, excBuffer=self.internalBuffer)
                altRouteSameWeek.Run()
                
            #==============================================
            # step 6: alternative route, previous weeks
            #==============================================
            self.week = self.initialWeek - 1
            while self.week >= 0 and (self.initialWeek - self.week) <= G.maxEarliness and len(self.internalBuffer):   

                itemsToBeAssigned = self.internalBuffer
                self.internalBuffer = []
                altRoutePreviousWeeks = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=1, excBuffer=self.internalBuffer)
                altRoutePreviousWeeks.Run()
                self.week -= 1
                
            #===================================================
            # step 7: later weeks, same and alternative routes
            #===================================================
            self.week = self.initialWeek + 1
            while self.week < G.planningHorizon and (self.week - self.initialWeek) <= G.maxLateness and len(self.internalBuffer):     

                # same route
                itemsToBeAssigned = self.internalBuffer
                self.internalBuffer = []
                sameRouteLaterWeeks = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=0, excBuffer=self.internalBuffer)
                sameRouteLaterWeeks.Run()
                
                if len(self.internalBuffer):

                    itemsToBeAssigned = self.internalBuffer
                    self.internalBuffer = []
                    sameRouteLaterWeeks = Allocation(itemList=itemsToBeAssigned, week=self.week, altRoutes=1, excBuffer=self.internalBuffer)
                    sameRouteLaterWeeks.Run()
                    
                self.week += 1
           
            #================================================
            # transfer excess items into global buffers
            #================================================
            if len(self.internalBuffer): 
                if self.itemType == 1:
                    G.ExcessFutureBuffer[G.replication] = self.internalBuffer
                else:
                    G.ExcessPPOSBuffer[G.replication] = self.internalBuffer
                
                self.internalBuffer = []
            
    # go through the initial buffer and counts the number of items to be assigned at self.week    
    def checkNumberOfItems(self):
        counter = 0
        for item in G.Buffer[G.replication]:
            if item.originalWeek == self.week and item.future == self.itemType:
                counter += 1
        return counter
    
    def filterWeek(self,buf):
        result = [x for x in buf if (x.originalWeek == self.week and self.itemType == x.future)]
        return result

    
# filter function to get items of a specific week (self.week) from the initial buffer           
#def filterWeek(buf):
#        
#    result = [x for x in buf if (x.originalWeek == G.filterWeek and G.filterItem == x.future)]
#    return result
    