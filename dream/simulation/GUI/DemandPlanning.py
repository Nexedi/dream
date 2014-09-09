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
from dream.simulation.AllocationManagement import AllocationManagement
from dream.simulation.LineGenerationJSON import main as simulate_line_json
from dream.simulation.Globals import G

from dream.simulation.GUI.Default import Simulation as DefaultSimulation
from dream.simulation.GUI.Default import schema, overloaded_property

class IG:
    TargetPPOS = 0
    TargetPPOSqty = 0
    TargetPPOSweek = 0
    maxEarliness = 0        # max number of weeks for earliness
    maxLateness = 0         # max number of weeks for lateness
    minPackingSize = 0
    CapacityDict={}
    RouteDict={}

def createGlobals():
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


#    filterItem = 0
#    filterWeek = 0

#===================================
# import simulation input data
#===================================
def readGeneralInput(data):
    # Info on PPOS to be disaggregated    
    # PPOS ID     1
    # PPOS Quantity   430
    IG.TargetPPOS = data['general']['TargetPPOS'] - 1
    IG.TargetPPOSqty = data['general']['TargetPPOSqty']

    # Time Line   
    # Week when the disaggregation has to be performed    2
    # Planning horizon (consistent with capacity info)    3
    IG.TargetPPOSweek = data['general']['TargetPPOSweek'] - 1
    G.planningHorizon = data['general']['planningHorizon']

    # Info on Global Demand - normal distribution parameters  
    # DistributionType    Normal
    # Mean    100000
    # Standard Deviation  3000
    #   XXX those 3 cannot be configured

    # Info on scenario analysis   
    # Number of Iterations    1
    G.ReplicationNo = data['general']['numberOfReplications']

    # Info on Time Cosntraints for Allocation 
    # Max Earliness   1
    # Max Lateness    1
    IG.maxEarliness = data['general']['maxEarliness']
    IG.maxLateness = data['general']['maxLateness']

    # Info on minimum allocable size  
    # Min Packing Size    10
    IG.minPackingSize = data['general']['minPackingSize']

    capacity_data = data['dp_capacity_spreadsheet']
    assert(len(capacity_data[0]) == G.planningHorizon+2)
    capacity = []
    for i in range(2, len(capacity_data) - 1):
        capacity.append([int(x) for x in capacity_data[i][1:-1]])
    G.Capacity = capacity

    route_data = data['dp_route_spreadsheet']
    for i in range(3, len(route_data[0]) - 1):
        IG.CapacityDict[route_data[2][i]] = G.Capacity[i-3]

    for i in range(4, len(route_data) - 1):
        id = float(route_data[i][2])
        ppos = float(route_data[i][0])
        sp = float(route_data[i][1])

        IG.RouteDict[id] = {'PPOS': ppos, 'SP': sp, 'route':{}}
        for j in range(3, len(route_data[i]) - 1):
            IG.RouteDict[id]['route'][route_data[2][j]] = float(route_data[i][j])


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
    import StringIO
    out = StringIO.StringIO()
    wbin.save(out)
    return out.getvalue()


class Simulation(DefaultSimulation):
    def getConfigurationDict(self):
        conf = {'Dream-Configuration':
            DefaultSimulation.getConfigurationDict(self)['Dream-Configuration']}

        conf["Dream-Configuration"]["gui"]["exit_stat"] = 0
        conf["Dream-Configuration"]["gui"]["debug_json"] = 0
        conf["Dream-Configuration"]["gui"]["graph_editor"] = 0
        conf["Dream-Configuration"]["gui"]["station_utilisation_graph"] = 0
        conf["Dream-Configuration"]["gui"]["exit_stat"] = 0
        conf["Dream-Configuration"]["gui"]["queue_stat"] = 0

        conf["Dream-Configuration"]["gui"]["download_excel_spreadsheet"] = 1
        conf["Dream-Configuration"]["gui"]["dp_capacity_spreadsheet"] = 1
        conf["Dream-Configuration"]["gui"]["dp_route_spreadsheet"] = 1

        prop_list = conf["Dream-Configuration"]["property_list"] = []
        prop_list.append({
            "id": "TargetPPOS",
            "name": "PPOS ID",
            "description": "Info on PPOS to be disaggregated",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 1
        })
        prop_list.append({
            "id": "TargetPPOSqty",
            "name": "PPOS Quantity",
            "description": "Info on PPOS to be disaggregated",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 430
        })
        prop_list.append({
            "id": "TargetPPOSweek",
            "name": "PPOS Week",
            "description": "Week when the disaggregation has to be performed",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 2
        })
        prop_list.append({
            "id": "planningHorizon",
            "name": "Planning horizon",
            "description": "Planning horizon (consistent with capacity info)",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 3
        })
        prop_list.append(overloaded_property(schema['numberOfReplications'],
                        {'_default': 1}))
        prop_list.append({
            "id": "maxEarliness",
            "name": "Max Earliness",
            "description": "Info on Time Constraints for Allocation",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 1
        })
        prop_list.append({
            "id": "maxLateness",
            "name": "Max Lateness",
            "description": "Info on Time Constraints for Allocation",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 1
        })
        prop_list.append({
            "id": "minPackingSize",
            "name": "Min Packing Size",
            "description": "Info on minimum allocable size",
            "type": "number",
            "_class": "Dream.Property",
            "_default": 10
        })
        return conf

    def run(self, data):
        # set up global variables
        createGlobals()
        # read from inputs spreadsheet
        readGeneralInput(data)
        inputDict={}

        inputDict['_class']='Dream.Simulation'

        # set general attributes
        inputDict['general']={}
        inputDict['general']['maxSimTime']=G.planningHorizon
        inputDict['general']['numberOfReplications']=G.ReplicationNo
        inputDict['general']['_class']='Dream.Simulation'

        inputDict['edges']={}
        inputDict['nodes']={}
        inputDict['nodes']['AM']={}
        inputDict['nodes']['AM']['_class']='Dream.AllocationManagement'
        inputDict['nodes']['AM']['id']='AM1'
        inputDict['nodes']['AM']['name']='AM1'
        inputDict['nodes']['AM']['argumentDict']={}

        # set current PPOS attributes
        inputDict['nodes']['AM']['argumentDict']['currentPPOS']={}
        inputDict['nodes']['AM']['argumentDict']['currentPPOS']['id']=IG.TargetPPOS
        inputDict['nodes']['AM']['argumentDict']['currentPPOS']['quantity']=IG.TargetPPOSqty
        inputDict['nodes']['AM']['argumentDict']['currentPPOS']['targetWeek']=IG.TargetPPOSweek

        # set allocation attributes
        inputDict['nodes']['AM']['argumentDict']['allocationData']={}
        inputDict['nodes']['AM']['argumentDict']['allocationData']['maxEarliness']=IG.maxEarliness
        inputDict['nodes']['AM']['argumentDict']['allocationData']['maxLateness']=IG.maxLateness
        inputDict['nodes']['AM']['argumentDict']['allocationData']['minPackingSize']=IG.minPackingSize

        # set capacity attributes
        inputDict['nodes']['AM']['argumentDict']['capacity']=IG.CapacityDict

        # set MA attributes
        inputDict['nodes']['AM']['argumentDict']['MAList']=IG.RouteDict

        G.argumentDictString=json.dumps(inputDict, indent=5)

        out = json.loads(simulate_line_json(input_data=(G.argumentDictString)))

        output = writeOutput()
        out['demandPlannerOutput.xls'] = output.encode('base64')
        return [{'key': 'default', 'score':0, 'result': out}]



