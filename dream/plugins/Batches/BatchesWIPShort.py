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
        # if the WIP data is to be read by KE tool just return
        if data['general'].get('wipSource',None)=='KE tool':
            return data
        
        nodes=data['graph']['node']
        WIPData=data['input'].get(self.configuration_dict['input_id'], {})
        batchCounter=0
        # get the number of units for a standard batch
        standardBatchUnits=0
        for node_id, node in nodes.iteritems():
            if node['_class']=='Dream.BatchSource':
                standardBatchUnits=int(node['batchNumberOfUnits']) 
            node['wip']=[]

        # remove the titles
        WIPData.pop(0)

        # group the stations that may share sub-batches
        groups=[]
        alreadyGrouped=[]
        for row in WIPData:
            # on the first empty row break
            if not row[0]:
                break
            stationId=row[0]
            if stationId in alreadyGrouped:
                continue
            
            workingBatchSize=nodes[stationId]['workingBatchSize']

            # get a list with the stations that the station might share batches with (if any)           
            sharingStations=[]
            if workingBatchSize!=standardBatchUnits:
                sharingStations=self.findSharingStations(data,stationId)
                self.checkIfDefinitionIsValid(data, WIPData, stationId, sharingStations,standardBatchUnits)
            if sharingStations:
                groups.append([stationId]+sharingStations)
                alreadyGrouped.extend(sharingStations)
            else:
                groups.append([stationId])
        
        # set the WIP for every group
        for group in groups:
            # if the station does not work in full batch
            groupWorkingBatchSize=nodes[group[0]]['workingBatchSize']
            currentBatchId='Batch_'+str(batchCounter)+'_WIP'
            subBatchCounter=0
            unitsToCompleteBatch=standardBatchUnits
            group.sort(key=lambda x: self.getDistanceFromSource(data, x))
            if groupWorkingBatchSize<standardBatchUnits:
                for stationId in group:
                    workingBatchSize=nodes[stationId]['workingBatchSize']
                    stationWIPData=[element for element in WIPData if element[0] == stationId][0]
                    awaiting=stationWIPData[1]
                    complete=stationWIPData[2]
                    startingBatchCounter=batchCounter
                    if not awaiting:
                        awaiting=0
                    awaiting=int(awaiting)
                    if not complete:
                        complete=0                    
                    complete=int(complete)
                    
                    # we calculate how many sub-batches are 
                    # before station (in buffer or decomposition)
                    # after station (in buffer or reassembly) and
                    # inside station (currently worked)
                    buffered=awaiting - (awaiting % workingBatchSize)
                    proceeded=complete - (complete % workingBatchSize)
                    currentCompleted=awaiting % workingBatchSize
                    bufferedSubBatches=int(buffered/workingBatchSize)
                    # if the station is after decomposition and has full batches waiting
                    # these should go to the buffer before decomposition
                    if self.checkIfStationIsAfterDecomposition(data, stationId):
                        if buffered>=standardBatchUnits:
                            bufferedBatches=int(buffered/standardBatchUnits)                        
                            bufferedSubBatches=int((buffered-bufferedBatches*standardBatchUnits)/workingBatchSize)
                            
                            for i in range(bufferedBatches):
                                bufferId=self.getBuffer(data, stationId)
                                self.createBatch(data, bufferId, currentBatchId, currentBatchId,standardBatchUnits)
                                batchCounter+=1
                                currentBatchId='Batch_'+str(batchCounter)+'_WIP'
                    
                    # set the buffered sub-batches to the previous station
                    for i in range(bufferedSubBatches):
                        receiver=None
                        
                        if startingBatchCounter!=batchCounter and bufferedSubBatches % (standardBatchUnits/workingBatchSize):
                            if (proceeded or currentCompleted):
                                receiver=stationId
                            else:
                                receiver=self.getParallelStations(data, stationId)[0]
                        
                        bufferId=self.getPredecessors(data, stationId)[0]
                        self.createSubBatch(data, bufferId, currentBatchId, currentBatchId, subBatchCounter, 
                                            workingBatchSize,receiver=receiver)
                        subBatchCounter+=1
                        unitsToCompleteBatch-=workingBatchSize
                        if unitsToCompleteBatch==0:
                            subBatchCounter=0
                            batchCounter+=1
                            currentBatchId='Batch_'+str(batchCounter)+'_WIP'
                            unitsToCompleteBatch=standardBatchUnits                       
                    # set the completed sub-batches to the next station
                    for i in range(int(proceeded/workingBatchSize)):
                        bufferId=self.getSuccessors(data, stationId)[0]
                        self.createSubBatch(data, bufferId, currentBatchId, currentBatchId, subBatchCounter, workingBatchSize)
                        subBatchCounter+=1
                        unitsToCompleteBatch-=workingBatchSize
                        if unitsToCompleteBatch==0:
                            subBatchCounter=0
                            batchCounter+=1
                            currentBatchId='Batch_'+str(batchCounter)+'_WIP'
                            unitsToCompleteBatch=standardBatchUnits
                    # set the sub-batch inside the station
                    if currentCompleted:
                        self.createSubBatch(data, stationId, currentBatchId, currentBatchId, subBatchCounter, workingBatchSize,
                                            unitsToProcess=currentCompleted)
                        subBatchCounter+=1
                        unitsToCompleteBatch-=workingBatchSize
                        if unitsToCompleteBatch==0:
                            subBatchCounter=0
                            batchCounter+=1
                            currentBatchId='Batch_'+str(batchCounter)+'_WIP'
                            unitsToCompleteBatch=standardBatchUnits
            # for stations that operate on full batches
            else:
                stationId=group[0]
                workingBatchSize=standardBatchUnits
                stationWIPData=[element for element in WIPData if element[0] == stationId][0]
                awaiting=stationWIPData[1]
                complete=stationWIPData[2]
                if not awaiting:
                    awaiting=0
                awaiting=int(awaiting)
                if not complete:
                    complete=0                    
                complete=int(complete)
                # calculate how many full batches wait in buffer
                buffered=awaiting - (awaiting % workingBatchSize)
                bufferedBatches=int(buffered/standardBatchUnits)
                # create the full batches in buffer
                for i in range(bufferedBatches):
                    bufferId=self.getBuffer(data, stationId)
                    self.createBatch(data, bufferId, currentBatchId, currentBatchId,standardBatchUnits)
                    batchCounter+=1
                    currentBatchId='Batch_'+str(batchCounter)+'_WIP'
                # if there is work in progress, create the batch giving the remaining units (unitsToProcess)
                if complete:
                    unitsToProcess=standardBatchUnits-complete
                    self.createBatch(data, stationId, currentBatchId, currentBatchId,standardBatchUnits,unitsToProcess=unitsToProcess)
        return data
    
    # creates a sub-batch in a station
    def createSubBatch(self,data,stationId,parentBatchId,parentBatchName,subBatchId,numberOfUnits,
                        unitsToProcess=0,receiver=None):
#         print 'creating sub-batch',stationId,parentBatchId,receiver
        if stationId:
            data['graph']['node'][stationId]['wip'].insert(0,{
                  "_class": 'Dream.SubBatch',
                  "id": parentBatchId+'_SB_'+str(subBatchId)+'_wip', 
                  "name":parentBatchName+'_SB_'+str(subBatchId)+'_wip', 
                  "numberOfUnits":numberOfUnits,
                  "unitsToProcess": unitsToProcess,   
                  "parentBatchId":parentBatchId,
                  "parentBatchName":parentBatchName,
                  "receiver":receiver                                               
                  }
            )   
        
    # creates a batch in a station
    def createBatch(self,data,stationId,batchId,batchName,numberOfUnits,unitsToProcess=0):
#         print 'creating batch',stationId,batchId,numberOfUnits
        if stationId:
            data['graph']['node'][stationId]['wip'].insert(0,{
                  "_class": 'Dream.Batch',
                  "id": batchId+'_wip',
                  "name":batchName+'_wip', 
                  "numberOfUnits":numberOfUnits,
                  "unitsToProcess": unitsToProcess,                                            
                  }
            )   
    
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
        
    # returns the buffer for a station id.
    def getBuffer(self,data,stationId):
        nodes=data['graph']['node']
        current=stationId
        # find all the predecessors that may share batches
        while 1:
            previous=self.getPredecessors(data, current)[0]
            # when a decomposition is reached break
            if 'Queue' in nodes[previous]['_class'] or 'Clearance' in nodes[previous]['_class']:
                return previous    
            if 'Source' in nodes[previous]['_class'] or 'Clearance' in nodes[previous]['_class']:
                return None       
            current=previous
        
    # returns true if the buffer is closer to a decompositions than a buffer
    def checkIfStationIsAfterDecomposition(self,data,stationId):       
        nodes=data['graph']['node']
        current=stationId
        # find all the predecessors that may share batches
        while 1:
            previous=self.getPredecessors(data, current)[0]
            # when a decomposition is reached break
            if 'Queue' in nodes[previous]['_class'] or 'Clearance' in nodes[previous]['_class']:
                return False    
            if 'Decomposition' in nodes[previous]['_class']:
                return True
            current=previous        
        
        
    