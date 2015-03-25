# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================

'''
Created on 25 Mar 2015

@author: Panos
'''
#=========================================== The JSONOutput object =============================================================#
#The JSONOutput object exports the data prepared by the KE tool to a format that follows the JSON schema. It uses predefined tags in the JSON schema. 
class JSONOutput(object):
    def Distributions(self,data):
        data1={}
        dist=data['distributionType']
        del data['distributionType']
        data1[dist]=data
        data=data1
        return data
        
    def ProcessingTimes(self,data,stationId,distDict):
        nodes = data['graph']['node']    #It creates a variable that holds the 'nodes' dictionary
        for element in nodes:  
            if element==stationId:                #It checks using if syntax if the element is the provided as argument stationId
                nodes[stationId]['processingTime']=self.Distributions(distDict)          
        return data
    
    def TTF(self,data,stationId,distDict):
        nodes = data['graph']['node']    #It creates a variable that holds the 'nodes' dictionary
        for element in nodes:
            if element==stationId:                #It checks using if syntax if the element is the provided as argument stationId
                nodes[stationId]['interruptions']['failure']['TTF']=self.Distributions(distDict)          
        return data
    
    def TTR(self,data,stationId,distDict):
        nodes = data['graph']['node']    #It creates a variable that holds the 'nodes' dictionary
        for element in nodes:
            if element==stationId:                #It checks using if syntax if the element is the provided as argument stationId
                nodes[stationId]['interruptions']['failure']['TTR']=self.Distributions(distDict)          
        return data
    
    def InterarrivalTime(self,data,stationId,distDict):
        nodes = data['graph']['node']    #It creates a variable that holds the 'nodes' dictionary
        for element in nodes:  
            if element==stationId:                #It checks using if syntax if the element is the provided as argument stationId
                nodes[stationId]['interarrivalTime']=self.Distributions(distDict)          
        return data
        
    
            
            
        
        
    
        
        
        
        
        
        