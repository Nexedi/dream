from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class CapacityStationWIPSpreadsheet(plugin.InputPreparationPlugin):
    """ Input prepration 
        read wip-srpeadsheet data and update the wip property of the stations.
    """

    def preprocess(self, data):
        """ Set the WIP in queue from spreadsheet data.
        """
        wipData=data['input'].get('wip_spreadsheet', None)
        node=data['graph']['node']
        # create an empty wip list in all CapacityStationBuffers
        for (node_id,node_data) in node.iteritems():
            if node_data['_class']=='dream.simulation.applications.CapacityStations.CapacityStationBuffer.CapacityStationBuffer':
                node_data['wip']=[]
        # get the number of projects
        numberOfProjects=0
        for col in range(1,len(wipData[0])):
            if wipData[0][col]:
                numberOfProjects+=1
            else:
                break
        # get the number of operations
        numberOfOperations=0
        for row in range(1,len(wipData)):
            if wipData[row][0]:
                numberOfOperations+=1 
            else:
                break
        # loop through all the columns>0    
        for col in range(1,numberOfProjects+1):
            projectId=wipData[0][col]
            # loop through all the rows>0
            for row in range(1,numberOfProjects+1):
                stationId=wipData[row][0]
                assert stationId in node.keys(), 'wip spreadsheet has station id that does not exist in production line'
                requiredCapacity=wipData[row][col]
                # if the cell has a requiredCapacity>0 create the entity
                if requiredCapacity:
                    buffer=self.getBuffer(data, stationId)
                    data['graph']['node'][buffer]['wip'].append({
                        "_class": "dream.simulation.applications.CapacityStations.CapacityEntity.CapacityEntity", 
                        "requiredCapacity": float(requiredCapacity), 
                        "capacityProjectId": projectId, 
                        "name": projectId+'_'+stationId+'_'+str(requiredCapacity)                                                          
                    })
        return data

    # gets the data and the station id and returns the buffer id of this station    
    def getBuffer(self,data,stationId):
        for (edge_id, edge) in data['graph']['edge'].iteritems():
            if edge['destination']==stationId:
                return edge['source']
    