from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class BatchesWIPShort(plugin.InputPreparationPlugin):
    """ Input preparation 
        reads the WIP from the short format
    """

    def preprocess(self, data):
        nodes=data['graph']['node']
        WIPData=data['input'].get(self.configuration_dict['input_id'], {})
        from pprint import pprint
               
        # get the number of units for a standard batch
        standardBatchUnits=0
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchSource':
                standardBatchUnits=int(node['batchNumberOfUnits']) 
            node['wip']=[]

        # remove the titles
        WIPData.pop(0)

        for row in WIPData:
            # on the first empty row break
            if not row[0]:
                break
            # if there is not record for the station continue
            if (not row[1]) and not (row[2]):
                pass
                # continue
            stationId=row[0]
            workingBatchSize=nodes[stationId]['workingBatchSize']
            
            # get a list with the stations that the station might share batches with (if any)           
            sharingStations=[]
            if workingBatchSize!=standardBatchUnits:
                sharingStations=self.findSharingStations(data,stationId)
                self.checkIfDefinitionIsValid(data, WIPData, stationId, sharingStations,standardBatchUnits)
            
            print stationId, self.getDistanceFromSource(data, stationId)
        return data
    
    # gets the data and a station id and returns a list with all the stations that the station may share batches
    def findSharingStations(self,data,stationId):
        nodes=data['graph']['node']
        sharingStations=[]
        current=stationId
        # find all the predecessors that may share batches
        while 1:
            previous=self.getPredecessors(data, current)[0]
            # when a decomposition is reached break
            if 'Decomposition' in nodes[previous]['_class']:
                break
            # when a station is reach add it
            if 'Machine' in nodes[previous]['_class'] or 'M3' in nodes[previous]['_class']:
                sharingStations.append(previous)
                # append also the parallel stations (this implies a symmetry)
                parallelStations=self.getParallelStations(data, previous)
                sharingStations.extend(parallelStations)
            current=previous
        current=stationId
        # find all the successors that may share batches
        while 1:
            next=self.getSuccessors(data, current)[0]
            # when a reassembly is reached break
            if 'Reassembly' in nodes[next]['_class']:
                break
            # when a station is reach add it
            if 'Machine' in nodes[next]['_class'] or 'M3' in nodes[next]['_class']:
                sharingStations.append(next)
                # append also the parallel stations (this implies a symmetry)
                parallelStations=self.getParallelStations(data, next)
                sharingStations.extend(parallelStations)
            current=next
        return sharingStations
        
    # validates the definition of WIP and throws an error message in case it is not valid, i.e. not full batches are formed
    def checkIfDefinitionIsValid(self,data,WIPData,stationId,sharingStations,standardBatchUnits):
        # find all the stations in the group. For example PackagingA may not share batches with PackagingB. 
        # but carding does share with both so the group should contain all 3 stations
        allStations=[stationId]+sharingStations
        stationsToAdd=[]
        for station in allStations:
            parallelStations=self.getParallelStations(data, station)
            for id in parallelStations:
                if id not in allStations:
                    stationsToAdd.append(id)
        allStations.extend(stationsToAdd)
        totalUnits=0
        for row in WIPData:
            if row[0] in allStations:
                if row[1]:
                    totalUnits+=int(row[1])
                if row[2]:
                    totalUnits+=int(row[2])
        assert totalUnits % standardBatchUnits == 0, 'wrong wip definition in group '+str(allStations)+'. Not full batches.'
                
    # returns how far a station is from source. Useful for sorting
    def getDistanceFromSource(self,data,stationId):
        distance=0
        nodes=data['graph']['node']
        current=stationId
        # find all the predecessors that may share batches
        while 1:
            previous=self.getPredecessors(data, current)[0]      
            if 'Source' in nodes[previous]['_class']:
                break
            distance+=1
            current=previous  
        return distance
        
        
    