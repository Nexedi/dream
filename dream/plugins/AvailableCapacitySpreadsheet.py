from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class AvailableCapacitySpreadsheet(plugin.InputPreparationPlugin):
    """ Input prepration 
        read capacity data and update the capacity property of the stations.
    """

    def preprocess(self, data):      
        strptime = datetime.datetime.strptime
        capacityData=data['input'].get('available_capacity_spreadsheet', None)
        nodes=data['graph']['node']
                      
        now = strptime(data['general']['currentDate'], '%Y/%m/%d')
        if capacityData:           
            poolDict={}
            for node_id, node in nodes.iteritems():
                pool=node.get('pool',None)
                if pool and not pool in nodes.keys():
                    if not poolDict.get(pool,None):
                        poolDict[pool]=[]                    
                    poolDict[pool].append(node_id)
                    
            # loop through columns and get those that contain a pool
            columnsToErase=[]
            for col in range(len(copy(capacityData[0]))):
                # if the column contains a pool create new columns with the actual station id
                if capacityData[0][col] in poolDict.keys():
                    pool=capacityData[0][col]
                    if pool in ['DAY',None,'']:
                        continue
                    poolCapacity=[c[col] for c in capacityData]      
                    columnsToErase.append(col) 
                    for stationId in poolDict[pool]:
                        capacityData[0].append(stationId)
                        i=1
                        for row in capacityData[1:]:
                            row.append(poolCapacity[i])
                            i+=1
                            
            # erase the columns that contain pools
            for col in columnsToErase:
                for row in capacityData:
                    row.pop(col)
            
            # loop through stations
            for col in range(len(capacityData[0])):
                stationId=capacityData[0][col]
                if stationId in ['DAY',None,'']:
                    continue
                assert stationId in data['graph']['node'].keys(), ('available capacity spreadsheet has station id:',stationId, 
                                                            'that does not exist in production line')
                # for every station read the interval capacity (Monday to Sunday)
                intervalCapacity=[]
                for row in range(7):
                    intervalCapacity.append(float(capacityData[row+1][col]))
                nodes[stationId]['intervalCapacity']=intervalCapacity
                # for every station read the interval capacity exceptions
                for row in range(8,len(capacityData)):
                    # at the first empty line break
                    if not capacityData[row][0]:
                        break
                    exeptionDate=strptime(capacityData[row][0], '%Y/%m/%d')   
                    dayDifference=(exeptionDate-now).days 
                    assert dayDifference>=0, 'exception date for past day given'   
                    intervalCapacityExceptions=nodes[stationId].get('intervalCapacityExceptions',{})
                    if not intervalCapacityExceptions:
                        nodes[stationId]['intervalCapacityExceptions']={}
                    nodes[stationId]['intervalCapacityExceptions'][str(float(dayDifference))]=float(capacityData[row][col])
                # set the interval capacity start
                nodes[stationId]['intervalCapacityStart']=now.weekday()
        return data
    
    
    