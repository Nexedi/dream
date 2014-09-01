'''
Created on 3 Oct 2013

@author: Anna

Basic implementation: runs the allocation routine for the future demand first
(one week at a time for the whole planning horizon) and the PPOS after

Equivalent to M2 in MATLAB functions
'''

import xlwt
import xlrd
from AllocationRoutine import AllocationRoutine
from CoreObject import CoreObject
from Globals import G
from ObjectInterruption import ObjectInterruption
from FutureDemandCreator import FutureDemandCreator

class AllocationManagement(ObjectInterruption): 
    def __init__(self, id=id, name=None, argumentDict={}):
        ObjectInterruption.__init__(self)
        self.id=id
        self.name=name
        self.argumentDict=argumentDict  #the arguments of the method given in a dict        
        self.initialize()
        
    def initialize(self):
        ObjectInterruption.initialize(self)
        self.readData()
        self.FDC=FutureDemandCreator()
        from Globals import G
        G.AllocationManagementList.append(self)
        
    def run(self):
        self.FDC.run()
        yield G.env.timeout(0)
        for kWeek in range(int(G.maxSimTime)):
        # activate allocation procedure for future items at target week
            procedureFuture = AllocationRoutine(initialWeek=kWeek, itemType=1)
            procedureFuture.Run()
        
        # activate allocation procedure for PPOS items at target week
        procedurePPOS = AllocationRoutine(initialWeek=G.TargetPPOSweek, itemType=0)
        procedurePPOS.Run()
        G.reCapacity.append(G.currentCapacity)
        G.replication+=1
        
    def readData(self):
        G.CapacityDict=self.argumentDict['capacity']
        import copy
        G.CurrentCapacityDict=copy.deepcopy(G.CapacityDict) 
        G.RouteDict=self.argumentDict['MAList']
        G.TargetPPOS=self.argumentDict['currentPPOS']['id']
        G.TargetPPOSqty=self.argumentDict['currentPPOS']['quantity']
        G.TargetPPOSweek=self.argumentDict['currentPPOS']['targetWeek']
        G.maxEarliness=self.argumentDict['allocationData']['maxEarliness']
        G.maxLateness=self.argumentDict['allocationData']['maxLateness']
        G.minPackingSize=self.argumentDict['allocationData']['minPackingSize']

