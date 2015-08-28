from copy import copy
import json
import time
import random
import operator
from datetime import datetime

from dream.plugins import plugin

class CapacityStationWIP(plugin.InputPreparationPlugin):
    """ Input prepration 
        read the wip from the project spreadsheet.
    """

    def preprocess(self, data):
        """ Set the WIP in queue from spreadsheet data.
        """
        projectData=data['input'].get('projects_spreadsheet', None)
        # find the column where the WIP is given
        wipColumn=6 #default
        i=0
        for element in projectData[0]:
            if element=='WIP':
                wipColumn=i
                break
            i+=1
        if projectData:
            alreadyConsideredProjects=[]
            for row in range(1, len(projectData)):
                if projectData[row][0] and not (projectData[row][0] in alreadyConsideredProjects):
                    projectId=projectData[row][0]
                    alreadyConsideredProjects.append(projectData[row][0])

                    numberOfOperations=1
                    i=1
                    # if the id changes or is empty it means there is no more data on the project
                    while (not projectData[row+i][0]) or (projectData[row+i][0]==projectId):
                        # if a completely empty line is found break
                        if all(v in [None, ''] for v in projectData[row+i]):
                            break
                        numberOfOperations+=1
                        i+=1

                    # for every operation get the wip and define it
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        requiredCapacity=float(projectData[row+stationRecord][wipColumn])
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
    