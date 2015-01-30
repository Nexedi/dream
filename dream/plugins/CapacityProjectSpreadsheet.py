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
        data['input']['BOM']={}     # Put the projects in BOM. Discuss this!
        node=data['graph']['node']
        now = strptime(data['general']['currentDate'], '%Y/%m/%d')
        if projectData:
            for row in range(1, len(projectData)):
                if projectData[row][0]:
                    projectId=projectData[row][0]
                    orderDate=strptime(projectData[row][1], '%Y/%m/%d')
                    orderDate=(orderDate-now).days 
                    try:
                        dueDate=strptime(projectData[row][2], '%Y/%m/%d')
                        dueDate=(dueDate-now).days 
                    # if no due date is given set it to 180 (about 6 months)
                    except ValueError:
                        dueDate=180
                    assemblySpaceRequirement=float(projectData[row][3])
                    capacityRequirementDict={}
                    earliestStartDict={}
                    # get the number of operations of the project
                    numberOfOperations=1
                    i=1
                    while not projectData[row+i][0]:
                        # if a completely empty line is found break
                        if all(v is None for v in projectData[row+i]):
                            break
                        numberOfOperations+=1
                        i+=1
                    # for every operation get capacityRequirementDict and earliestStartDict
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        requiredCapacity=projectData[row+stationRecord][5]
                        earliestStart=projectData[row+stationRecord][6]
                        capacityRequirementDict[stationId]=float(requiredCapacity)
                        if earliestStart:
                            earliestStart=strptime(earliestStart, '%Y/%m/%d')
                            earliestStartDict[stationId]=(earliestStart-now).days
                    # define the order in BOM 
                    data['input']['BOM'][projectId]={
                         'orderDate':orderDate,
                         'dueDate':dueDate,
                         'assemblySpaceRequirement':assemblySpaceRequirement,
                         'capacityRequirementDict':capacityRequirementDict,
                         'earliestStartDict':earliestStartDict
                     }
        print data['input']['BOM']
        return data
    
    