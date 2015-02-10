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
        if wipData:
            node=data['graph']['node']
            # create an empty wip list in all CapacityStationBuffers
            for (node_id,node_data) in node.iteritems():
                if node_data['_class']=='dream.simulation.applications.CapacityStations.CapacityStationBuffer.CapacityStationBuffer':
                    node_data['wip']=[]
            # get the number of projects
            numberOfProjects=len([pr for pr in wipData[0] if (pr and not pr=='Operation')])
            # get the number of operations
            numberOfOperations=len([op for op in wipData if (op[0] and not op[0]=='Operation')])
            # loop through all the columns>0    
            for col in range(1,numberOfProjects+1):
                projectId=wipData[0][col]
                # loop through all the rows>0
                for row in range(1,numberOfOperations+1):
                    stationId=wipData[row][0]
                    assert stationId in node.keys(), 'wip spreadsheet has station id that does not exist in production line'
                    requiredCapacity=float(wipData[row][col])
                    # if the cell has a requiredCapacity>0 create the entity
                    if requiredCapacity:
                        capacityBuffer=self.getBuffer(data, stationId)
                        data['graph']['node'][capacityBuffer]['wip'].append({
                            "_class": "dream.simulation.applications.CapacityStations.CapacityEntity.CapacityEntity", 
                            "requiredCapacity": requiredCapacity, 
                            "capacityProjectId": projectId, 
                            "name": projectId+'_'+stationId+'_'+str(requiredCapacity)                                                          
                        })
        return data

    # gets the data and the station id and returns the buffer id of this station    
    def getBuffer(self,data,stationId):
        for (edge_id, edge) in data['graph']['edge'].iteritems():
            if edge['destination']==stationId:
                return edge['source']
    