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
        node=data['graph']['node']
        now = strptime(data['general']['currentDate'], '%Y/%m/%d')
        if capacityData:
            # get the number of stations
            numberOfStations=len([st for st in capacityData[0] if (st and not st=='DAY')])
            # loop through stations
            for col in range(numberOfStations):
                stationId=capacityData[0][col+1]
                assert stationId in data['graph']['node'].keys(), ('available capacity spreadsheet has station id:',stationId, 
                                                            'that does not exist in production line')
                # for every station read the interval capacity (Monday to Sunday)
                intervalCapacity=[]
                for row in range(7):
                    intervalCapacity.append(float(capacityData[row+1][col+1]))
                node[stationId]['intervalCapacity']=intervalCapacity
                # for every station read the interval capacity exceptions
                for row in range(8,len(capacityData)):
                    # at the first empty line break
                    if not capacityData[row][0]:
                        break
                    exeptionDate=strptime(capacityData[row][0], '%Y/%m/%d')   
                    dayDifference=(exeptionDate-now).days 
                    assert dayDifference>=0, 'exception date for past day given'   
                    intervalCapacityExceptions=node[stationId].get('intervalCapacityExceptions',{})
                    if not intervalCapacityExceptions:
                        node[stationId]['intervalCapacityExceptions']={}
                    node[stationId]['intervalCapacityExceptions'][str(float(dayDifference))]=float(capacityData[row][col+1])
                # set the interval capacity start
                node[stationId]['intervalCapacityStart']=now.weekday()
        return data
    
    