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


configuration=open("PilotCases\CapacityStations\sampleConfiguration.json", "r")
# configuration=open("sampleConfiguration.json", "r")
configurationData=configuration.read()
configurationJSON=json.loads(configurationData)

db=open("PilotCases\CapacityStations\sampleDBExtraction.json", "r")
# configuration=open("sampleConfiguration.json", "r")
dbData=db.read()
dbJSON=json.loads(dbData)
operations=dbJSON.get('operations',{})
stations=configurationJSON['graph']['node']
currentDate=configurationJSON['general']['currentDate']
currentDate=datetime.strptime(currentDate, '%Y/%m/%d')

# set the interval capacity of the stations
for operationId, operation in operations.iteritems():
    intervalCapacity=operation.get('intervalCapacity',[])
    for stationId, station in stations.iteritems():
        if stationId==operationId:
            station['intervalCapacity']=intervalCapacity

orders=dbJSON.get('orders',{})
configurationJSON['input']['BOM']['productionOrders']=[]

capacityRequirementDict={}
earliestStartDict={}
for order in orders:
    for operation in order['sequence']: 
        operationId=operation.keys()[0]
        capacityRequirementDict[operationId]=operation[operationId]['requiredCapacity']
        earliestStart=operation[operationId].get('earliestStart',None)
        if earliestStart:
            earliestStart=datetime.strptime(earliestStart, '%Y-%m-%d')
            earliestStartDict[operationId]=(earliestStart-currentDate).days
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
    

updatedModelJSONString=json.dumps(configurationJSON, indent=5)
updatedModel=open('UpdatedModel.json', mode='w')
updatedModel.write(updatedModelJSONString)






