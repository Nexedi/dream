from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class CapacityProjectSpreadsheet(plugin.InputPreparationPlugin):
    """ Input prepration 
        read the capacity projects from the spreadsheet
    """

    def preprocess(self, data):
        strptime = datetime.datetime.strptime
        projectData=data['input'].get('projects_spreadsheet', None)
        data['input']['BOM']={}     
        data['input']['BOM']['productionOrders']=[] 
        node=data['graph']['node']
        now = strptime(data['general']['currentDate'], '%Y/%m/%d')
        
        # find the column where the earliest start is given
        i=0
        for element in projectData[0]:
            if element=='Earliest Start Date':
                earliestStartColumn=i
                break
            i+=1

        if projectData:
            alreadyConsideredProjects=[]
            for row in range(1, len(projectData)):
                if projectData[row][0] and not (projectData[row][0] in alreadyConsideredProjects):
                    projectId=projectData[row][0]
                    alreadyConsideredProjects.append(projectData[row][0])
                    orderDate=strptime(projectData[row][1], '%Y/%m/%d')
                    orderDate=(orderDate-now).days 
                    if projectData[row][2]:
                        dueDate=strptime(projectData[row][2], '%Y/%m/%d')
                        dueDate=(dueDate-now).days 
                    # if no due date is given set it to 180 (about 6 months)
                    else:
                        dueDate=120
                    assemblySpaceRequirement=float(projectData[row][3])
                    capacityRequirementDict={}
                    earliestStartDict={}
                    # get the number of operations of the project
                    numberOfOperations=1
                    i=1
                    # if the id changes or is empty it means there is no more data on the project
                    while (not projectData[row+i][0]) or (projectData[row+i][0]==projectId):
                        # if a completely empty line is found break
                        if all(v in [None, ''] for v in projectData[row+i]):
                            break
                        numberOfOperations+=1
                        i+=1
                                    
                    # for every operation get capacityRequirementDict and earliestStartDict
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        requiredCapacity=projectData[row+stationRecord][5]
                        earliestStart=projectData[row+stationRecord][earliestStartColumn]
                        capacityRequirementDict[stationId]=float(requiredCapacity)
                        if earliestStart:
                            earliestStart=strptime(earliestStart, '%Y/%m/%d')
                            earliestStartDict[stationId]=(earliestStart-now).days
                    # define the order in BOM 
                    data['input']['BOM']['productionOrders'].append({
                         'orderDate':orderDate,
                         'dueDate':dueDate,
                         'assemblySpaceRequirement':assemblySpaceRequirement,
                         'capacityRequirementDict':capacityRequirementDict,
                         'earliestStartDict':earliestStartDict,
                         'id':projectId,
                         'name':projectId,
                         '_class':"dream.simulation.applications.CapacityStations.CapacityProject.CapacityProject"
                     })
        return data
    
    