# ===========================================================================
# Copyright 2013 University of Limerick
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
Created on 17 Apr 2014

@author: Anna, George
'''
'''
test script to convert the static excels to JSON. It does not communicate with GUI yet
'''

import xlwt
import xlrd
import json
from AllocManagement import AllocManagement
from dream.simulation.Globals import G
from dream.simulation.FutureDemandCreator import FutureDemandCreator


def createGlobals():
    G.TargetPPOS = 0
    G.TargetPPOSqty = 0
    G.TargetPPOSweek = 0
    G.ReplicationNo = 0
    G.replication = 0
    G.PPOSlist = {}
    G.Capacity = []
    G.route = {}
    G.maxEarliness = 0        # max number of weeks for earliness
    G.maxLateness = 0         # max number of weeks for lateness
    G.planningHorizon =0      # for future demand purposes
    G.demandFile = None
    G.currentCapacity = None
    G.reCapacity = []
    G.PPOSprofile = []        # initial disaggregation for PPOS
    G.FutureProfile = []      # initial disaggregation for future demand
    G.AllocationFuture = []
    G.FutureLateness = []
    G.FutureEarliness = []    
    G.AllocationPPOS = []
    G.PPOSLateness = []
    G.PPOSEarliness = []
    G.minPackingSize = 0
    G.Buffer = []
    G.ExcessPPOSBuffer = []
    G.ExcessPPOSminBuffer = []
    G.ExcessFutureBuffer = []
    G.ExcessFutureMinBuffer = []    
    G.DistributionType=None
    G.CapacityDict={}
    G.RouteDict={}

#    filterItem = 0
#    filterWeek = 0

#===================================
# import simulation input data
#===================================
def readGeneralInput():
    # general simulation input
    wbin = xlrd.open_workbook('GUI/inputs.xlsx')
    sh = wbin.sheet_by_name('Scalar_Var')
    G.TargetPPOS = int(sh.cell(2,1).value) -1 
    G.TargetPPOSqty = int(sh.cell(3,1).value)
    G.TargetPPOSweek = int(sh.cell(6,1).value) -1    
    G.planningHorizon = int(sh.cell(7,1).value) 
    G.ReplicationNo = int(sh.cell(15,1).value) 
    G.maxEarliness = int(sh.cell(18,1).value) 
    G.maxLateness = int(sh.cell(19,1).value) 
    G.minPackingSize = int(sh.cell(22,1).value)

    # capacity information
    sh = wbin.sheet_by_name('Capacity')
    nCols = sh.ncols
    nRows=sh.nrows
    assert(nCols == G.planningHorizon+1)
    capacity=[]
#     for i in range(1,nCols):
#         capacity.append(sh.col_values(i,2))

    for i in range(2, nRows):
        capacity.append(sh.row_values(i,1,4))
    G.Capacity = capacity      

    # PPOS-MA disaggregation and corresponding routes
    sh = wbin.sheet_by_name('Route')
    nRows = sh.nrows
    nCols = sh.ncols
    # prepare a dict that holds the capacity of every bottleneck  per week
    for i in range(3,nCols):
        G.CapacityDict[sh.cell(2,i).value]=G.Capacity[i-3]
    
    
    for i in range(4,nRows):
        tempPPOSlist = sh.row_values(i,0,3)
        id=tempPPOSlist[2]
        ppos=tempPPOSlist[0]
        sp=tempPPOSlist[1]
        routeValues=sh.row_values(i,3,nCols)
        G.RouteDict[id]={'PPOS':ppos, 'SP':sp, 'route':{}}
        for j in range(len(routeValues)):
            G.RouteDict[id]['route'][sh.cell(2,j+3).value]=routeValues[j]

def writeOutput():
    
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
                   
    wbin.save("demandPlannerOutput.xls")    # temporary have a file for verification


def main():    
    # set up global variables
    createGlobals()
    # read from inputs spreadsheet
    readGeneralInput()
    # open json file
    argumentDictFile=open('argumentDict.json', mode='w')
    argumentDict={}
    argumentDict['argumentDict']={}
    
    # set general attributes
    argumentDict['general']={}
    argumentDict['general']['maxSimTime']=G.planningHorizon
    argumentDict['general']['numberOfReplications']=G.ReplicationNo
    
    # set current PPOS attributes
    argumentDict['argumentDict']['currentPPOS']={}
    argumentDict['argumentDict']['currentPPOS']['id']=G.TargetPPOS
    argumentDict['argumentDict']['currentPPOS']['quantity']=G.TargetPPOSqty
    argumentDict['argumentDict']['currentPPOS']['targetWeek']=G.TargetPPOSweek
    
    # set allocation attributes
    argumentDict['argumentDict']['allocationData']={}
    argumentDict['argumentDict']['allocationData']['maxEarliness']=G.maxEarliness
    argumentDict['argumentDict']['allocationData']['maxLateness']=G.maxLateness
    argumentDict['argumentDict']['allocationData']['minPackingSize']=G.minPackingSize
        
    # set capacity attributes
    argumentDict['argumentDict']['capacity']=G.CapacityDict    

    # set MA attributes
    argumentDict['argumentDict']['MAList']=G.RouteDict  
    
    G.argumentDictString=json.dumps(argumentDict, indent=5)
    argumentDictFile.write(G.argumentDictString)
    
    # create the future demand
    FDC=FutureDemandCreator()
    FDC.run()
    #call the AllocManagement routine
    AM = AllocManagement()
    AM.Run()
    writeOutput()   # currently to excel for verification. To be outputted in JSON
    print G.AllocationPPOS
    
if __name__ == '__main__':
    main()
