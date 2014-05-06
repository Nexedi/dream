'''
Created on 3 Oct 2013

@author: Anna

Basic implementation: runs the allocation routine for the future demand first (one week at a time for the whole planning horizon) and the 
PPOS after

Equivalent to M2 in MATLAB functions
'''


from AllocationRoutine import AllocationRoutine
from dream.simulation.Globals import G


class AllocManagement(): 
        
    def Run(self):
        
        for kWeek in range(G.planningHorizon):
        # activate allocation procedure for future items at target week
            procedureFuture = AllocationRoutine(initialWeek=kWeek, itemType=1)
            procedureFuture.Run()
        
        # activate allocation procedure for PPOS items at target week
        procedurePPOS = AllocationRoutine(initialWeek=G.TargetPPOSweek, itemType=0)
        procedurePPOS.Run()

        G.reCapacity.append(G.currentCapacity)
        


        
