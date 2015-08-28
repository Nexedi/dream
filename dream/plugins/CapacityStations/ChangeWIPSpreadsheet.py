from dream.plugins import plugin

class ChangeWIPSpreadsheet(plugin.InputPreparationPlugin):
    """ Input prepration 
        if the wip is given based on what is completed use this plugin to calculate what is needed and update the spreadsheet.
    """

    def preprocess(self, data):
        projectData=data['input'].get('projects_spreadsheet', None)
        # find the column where the WIP is given
        wipColumn=6 #default
        i=0
        for element in projectData[0]:
            if element=='Completed':
                wipColumn=i
                projectData[0][i]='WIP'
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
                    # for every project create a dict to keep what is completed
                    completedCapacityDict={}
                    # for every project create a dict to keep what is requested
                    requiredCapacityDict={}
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        completedCapacity=float(projectData[row+stationRecord][wipColumn])
                        requiredCapacity=float(projectData[row+stationRecord][5])
                        completedCapacityDict[stationId]=completedCapacity
                        requiredCapacityDict[stationId]=requiredCapacity
                    # create the wip dictionary
                    wipDict=self.calculateWIPDict(data, completedCapacityDict,requiredCapacityDict,projectId)
                    # change the completed data with the wip data in the spreadsheet
                    for stationRecord in range(numberOfOperations):
                        stationId=projectData[row+stationRecord][4]
                        projectData[row+stationRecord][wipColumn]=wipDict[stationId]
        return data
    
    # gets the dict that shows the completed capacities and returns the one with the actual wip
    def calculateWIPDict(self,data,completedCapacityDict,requiredCapacityDict,projectId):
        wipDict={}
        for stationId, completedCapacity in completedCapacityDict.iteritems():
            previous=self.getPredecessors(data, stationId)
            if previous:
                # if the station is assembly
                if len(previous)>1:
                    # if there is capacity completed, then the project was assembled. So set the remaining capacity (if any) as WIP
                    if completedCapacityDict[stationId]:
                        wipDict[stationId]=requiredCapacityDict[stationId]-completedCapacityDict[stationId]
                    # else, set wip ONLY if all the pre-decessors have finished this project
                    else:
                        readyForAssembly=True
                        for previousId in previous:
                            if requiredCapacityDict[previousId]>completedCapacityDict[previousId]:
                                 readyForAssembly=False            
                        wipDict[stationId]=0
                        if readyForAssembly:
                            wipDict[stationId]=requiredCapacityDict[stationId]
                # if the station is not assembly but has predecessor
                # check what the predecessor has finished and what workload comes to station. 
                # if the station has already finished some of the workload reduce it from the wip
                else:
                    previousId=previous[0]
                    completedFromPrevious=completedCapacityDict[previousId]
                    transferRate=requiredCapacityDict[stationId]/float(requiredCapacityDict[previousId])
                    wipDict[stationId]=(transferRate*completedFromPrevious)-completedCapacityDict[stationId] 
            else:
                wipDict[stationId]=requiredCapacityDict[stationId]-completedCapacityDict[stationId]     
            assert not (wipDict[stationId]<0), 'invalid WIP definition for '+projectId+' in '+stationId       
        return wipDict
        
    
    
    