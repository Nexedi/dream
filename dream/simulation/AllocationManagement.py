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
from SimPy.Simulation import hold
from ObjectInterruption import ObjectInterruption
from FutureDemandCreator import FutureDemandCreator

class AllocationManagement(ObjectInterruption): 
    def __init__(self, id=id, name=None, argumentDict={}):
        ObjectInterruption.__init__(self)
        self.id=id
        self.name=name
        self.argumentDict=argumentDict  #the arguments of the method given in a dict        
        self.readData()
        self.FDC=FutureDemandCreator()
        
    def run(self):
        self.FDC.run()
        yield hold,self,0 
        for kWeek in range(int(G.maxSimTime)):
        # activate allocation procedure for future items at target week
            procedureFuture = AllocationRoutine(initialWeek=kWeek, itemType=1)
            procedureFuture.Run()
        
        # activate allocation procedure for PPOS items at target week
        procedurePPOS = AllocationRoutine(initialWeek=G.TargetPPOSweek, itemType=0)
        procedurePPOS.Run()
        G.reCapacity.append(G.currentCapacity)
        self.writeOutput()
        
    def readData(self):
        G.CapacityDict=self.argumentDict['capacity']
        G.CurrentCapacityDict=G.CapacityDict
        G.RouteDict=self.argumentDict['MAList']
        G.TargetPPOS=self.argumentDict['currentPPOS']['id']
        G.TargetPPOSqty=self.argumentDict['currentPPOS']['quantity']
        G.TargetPPOSweek=self.argumentDict['currentPPOS']['targetWeek']
        G.maxEarliness=self.argumentDict['allocationData']['maxEarliness']
        G.maxLateness=self.argumentDict['allocationData']['maxLateness']
        G.minPackingSize=self.argumentDict['allocationData']['minPackingSize']
    
    def writeOutput(self):
        
        wbin = xlwt.Workbook()
        for k in range(G.ReplicationNo):
            
            
            #export info on lateness
            sheet1=wbin.add_sheet('Lateness'+str(k+1))
            sheet1.write(0,0,'replication')
            sheet1.write(0,1,k+1)
            sheet1.write(2,0,'PPOS Lateness')
            sheet1.write(2,1,G.PPOSLateness[k])
            sheet1.write(3,0,'PPOS Earliness')
            sheet1.write(3,1,G.PPOSEarliness[k])
            sheet1.write(1,3,'Unconstrained Excess Units')
            sheet1.write(1,4,'Min Excess Units')
                   
            excessPPOS = sum([i.qty for i in G.ExcessPPOSBuffer[k]])
            minExcessPPOS = sum([i.qty for i in G.ExcessPPOSminBuffer[k]])
            sheet1.write(2,3,excessPPOS)
            sheet1.write(2,4, minExcessPPOS)
            print 'excess future', [i.orderID for i in G.ExcessFutureBuffer[k]], [i.qty for i in G.ExcessFutureBuffer[k]]
            print 'excess ppos', [i.orderID for i in G.ExcessPPOSBuffer[k]], [i.qty for i in G.ExcessPPOSBuffer[k]]
            excessFuture = sum([i.qty for i in G.ExcessFutureBuffer[k]])
            minExcessFuture = sum([i.qty for i in G.ExcessFutureMinBuffer[k]])
            sheet1.write(1,6,'% Unconstrained Excess')
            sheet1.write(1,7,'% Min Excess')
            sheet1.write(4,3,excessFuture)
            sheet1.write(4,4,minExcessFuture)
            sheet1.write(4,0,'Future Demand Lateness')
            sheet1.write(4,1,G.FutureLateness[k])
            sheet1.write(5,0,'Future Demand Earliness')
            sheet1.write(5,1,G.FutureEarliness[k])
            
            # Export PPOS/Future allocation Results       
            for z in range(2):
                if z==0:
                    shName = 'PPOSAllocation'+str(k+1)
                    itemName = 'Initial PPOS Demand Disaggregation'
                    profile = G.PPOSprofile[k]
                    alloc = G.AllocationPPOS[k]
                else:
                    shName = 'FutureAllocation'+str(k+1)
                    itemName = 'Initial Future Demand Disaggregation'
                    profile = G.FutureProfile[k]
                    alloc = G.AllocationFuture[k]
                    
                    
                sheet = wbin.add_sheet(shName)
                sheet.write_merge(0,0,0,4,itemName)
                sheet.write(1,0,'Order ID')
                sheet.write(1,1,'MA ID')
                sheet.write(1,2,'Total # Units')
                sheet.write(1,3,'Min # Units')
                sheet.write(1,4,'Planned Week')
                
                for i in range(len(profile)):
                    for j in range(len(profile[i])):
                        sheet.write(i+2,j,profile[i][j])
                        
                totQty = sum([i[2] for i in profile])
                
                if z==0:                
                    #pposQty = totQty
                    sheet1.write(2,6,excessPPOS*100.0/totQty)
                    sheet1.write(2,7,minExcessPPOS*100.0/totQty)
                else:
                    sheet1.write(4,6,excessFuture*100.0/totQty)
                    sheet1.write(4,7,minExcessFuture*100.0/totQty)
    
                print 'allocation', alloc
                counterCols = [5 for i in range(len(profile))]  
                # TODO the below crashes, got to check             
                for i in range(len(alloc)):
                    for j in range(3):
                        sheet.write(alloc[i][0]+2,counterCols[alloc[i][0]]+j,alloc[i][j+1])
                    counterCols[alloc[i][0]] += 3
                
                attempts = (max(counterCols)-5)/3
                for i in range(attempts):
                    sheet.write_merge(0,0,5+(i*3),5+(i*3)+2,'Allocation Attempt No.'+str(i+1))
                    sheet.write(1,5+(i*3),'MA ID')
                    sheet.write(1,5+(i*3)+1,'# Allocated Units')
                    sheet.write(1,5+(i*3)+2,'Week')
            
            
            # Excess units        
            for z in range(2):
                for y in range(2):
                    if z==0:
                        if y == 0:
                            shName = 'PPOSExcess'+str(k+1)
                            buf = G.ExcessPPOSBuffer[k]
                        else:
                            shName = 'PPOSminExcess'+str(k+1)
                            buf = G.ExcessPPOSminBuffer[k]
                    else:
                        if y == 0:
                            shName = 'FutureExcess'+str(k+1)
                            buf = G.ExcessFutureBuffer[k]
                        else:
                            shName = 'FutureMinExcess'+str(k+1)
                            buf = G.ExcessFutureMinBuffer[k]                      
            
                    row = 1
                    if len(buf):
                        sheet = wbin.add_sheet(shName)
                        sheet.write(0,0,'Order ID')
                        sheet.write(0,1,'MA ID')
                        sheet.write(0,2,'excess Units')
                        for i in buf:
                            sheet.write(row,0,i.orderID+1)
                            sheet.write(row,1,i.MAid)
                            sheet.write(row,2,i.qty)
                            row +=1
                            
            # remaining capacity
            sheet = wbin.add_sheet('Capacity'+str(k+1))
            sheet.write_merge(0,0,1,G.planningHorizon,'Weeks')
            for i in range(G.planningHorizon):
                sheet.write(1,i+1,i+1)
            sheet.write_merge(0,1,0,0,'Bottlenecks')
            i=2
            for record in G.CurrentCapacityDict:
                sheet.write(i,0,record)
                sheet.write(i,1,G.CurrentCapacityDict[record][0])
                sheet.write(i,2,G.CurrentCapacityDict[record][1])
                sheet.write(i,3,G.CurrentCapacityDict[record][2])
                i+=1               
                       
        wbin.save("allocationManagement.xls")    # temporary have a file for verification
