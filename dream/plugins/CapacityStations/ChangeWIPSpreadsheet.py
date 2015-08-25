from dream.plugins import plugin

class ChangeWIPSpreadsheet(plugin.InputPreparationPlugin):
    """ Input prepration 
        if the wip is given based on what is completed use this plugin to calculate what is needed and update the spreadsheet.
    """

    def preprocess(self, data):
        projectData=data['input'].get('projects_spreadsheet', None)
        # find the column where the WIP is given
        i=0
        for element in projectData[0]:
            if element=='WIP':
                wipColumn=i
                break
            i+=1
        from pprint import pprint
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
                    completedCapacityDict={}
                    requiredCapacityDict={}
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        completedCapacity=float(projectData[row+stationRecord][wipColumn])
                        requiredCapacity=float(projectData[row+stationRecord][5])
                        completedCapacityDict[stationId]=completedCapacity
                        requiredCapacityDict[stationId]=requiredCapacity
#                     print '------------',projectId
#                     pprint(completedCapacityDict)  
                    wipDict=self.calculateWIPDict(data, completedCapacityDict,requiredCapacityDict)
                    print '------------',projectId
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        projectData[row+stationRecord][wipColumn]=wipDict[stationId]
                        
                    pprint(wipDict)                             
        return data
    
    # gets the dict that shows the completed capacities and returns the one with the actual wip
    def calculateWIPDict(self,data,completedCapacityDict,requiredCapacityDict):
        wipDict={}
        for stationId, completedCapacity in completedCapacityDict.iteritems():
            if self.checkIfStationIsFirst(data, stationId):
                wipDict[stationId]=requiredCapacityDict[stationId]-completedCapacityDict[stationId]
            else:
                wipDict[stationId]=0
        return wipDict

    # returns True if the station has no predecessors
    def checkIfStationIsFirst(self,data,stationId):
        previous=self.getPredecessors(data, stationId)
        if previous:
            return False
        return True
        
    
    
    