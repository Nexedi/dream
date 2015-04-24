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

import json
from datetime import datetime

# gets the data and the station id and returns the buffer id of this station    
def getBuffer(data,stationId):
    for (edge_id, edge) in data['graph']['edge'].iteritems():
        if edge['destination']==stationId:
            return edge['source']

def OutputPreparation(data,extractedData):
    configurationJSON=data
    dbJSON=extractedData
    operations=dbJSON.get('operations',{})
    stations=configurationJSON['graph']['node']
    currentDate=configurationJSON['general']['currentDate']
    currentDate=datetime.strptime(currentDate, '%Y/%m/%d')
    
    orders=dbJSON.get('orders',{})
    configurationJSON['input']['BOM']={}
    configurationJSON['input']['BOM']['productionOrders']=[]
    
    capacityRequirementDict={}
    earliestStartDict={}
    for order in orders:
        for operation in order['sequence']: 
            operationId=operation.keys()[0]
            capacityRequirementDict[operationId]=operation[operationId]['requiredCapacity']
            earliestStart=operation[operationId].get('earliestStart',None)
            try:
                earliestStart=datetime.strptime(earliestStart, '%Y-%m-%d')
                earliestStartDict[operationId]=(earliestStart-currentDate).days
            except ValueError:
                continue
        assemblySpaceRequirement=order.get('floorSpaceRequired',100)
        orderId=order['orderID']
        dueDate=order.get('dueDate',100)
        dueDate=datetime.strptime(dueDate, '%Y-%m-%d')
        dueDate=(dueDate-currentDate).days
        orderDate=order.get('orderDate',0)
        orderDate=datetime.strptime(orderDate, '%Y-%m-%d')
        orderDate=(orderDate-currentDate).days
        name=order.get('orderName',orderId)
        configurationJSON['input']['BOM']['productionOrders'].append({
                "capacityRequirementDict":capacityRequirementDict,
                "assemblySpaceRequirement":assemblySpaceRequirement,
                "name":name,
                "id":orderId,
                "earliestStartDict":earliestStartDict,
                "_class": "dream.simulation.applications.CapacityStations.CapacityProject.CapacityProject",
                "dueDate":dueDate,
                "orderDate":orderDate
                })
        
    WIP=dbJSON.get('WIP',{})
    if WIP:
        node=configurationJSON['graph']['node']
        #create an empty wip list in all CapacityStationBuffers
        for (node_id,node_data) in node.iteritems():
            if node_data['_class']=='dream.simulation.applications.CapacityStations.CapacityStationBuffer.CapacityStationBuffer':
                node_data['wip']=[]
        for taskid, wip in WIP.iteritems():
            oper=wip.get('operation',[])
            requiredCapacity=wip.get('Capacity required', 0)
            buffered=wip.get('buffered', 0)
            orderId=wip.get('order_id',[])
            if requiredCapacity or buffered:
                capacityBuffer=getBuffer(configurationJSON,oper)
                configurationJSON['graph']['node'][capacityBuffer]['wip'].append({
                                "_class": "dream.simulation.applications.CapacityStations.CapacityEntity.CapacityEntity", 
                                "requiredCapacity": max([requiredCapacity,buffered]), 
                                "capacityProjectId": orderId, 
                                "name": orderId+'_'+oper+'_'+str(requiredCapacity)                                                          
                            })
                        
    return configurationJSON




