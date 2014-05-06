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
    FDC=FutureDemandCreator()
    FDC.run()
    
if __name__ == '__main__':
    main()
