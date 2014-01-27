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
Created on 18 Aug 2013

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All the Resources should inherit from it
'''
from SimPy.Simulation import Resource

# ===========================================================================
#                    the resource that repairs the machines
# ===========================================================================
class ObjectResource(object):
    
    def __init__(self):
        self.initialized = False
        
    def initialize(self):
        self.totalWorkingTime=0         #holds the total working time
        self.totalWaitingTime=0         #holds the total waiting time
        self.timeLastOperationStarted=0    #holds the time that the last repair was started        
        self.Res=Resource(self.capacity)
        # variable that checks weather the resource is already initialized
        self.initialized = True
    
    # =======================================================================
    #                    checks if the worker is available
    # =======================================================================       
    def checkIfResourceIsAvailable(self,callerObject=None): 
        return len(self.Res.activeQ)<self.capacity   
    
    # =======================================================================
    #              actions to be taken after the simulation ends
    # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        pass    
    
    # =======================================================================
    #                     outputs message to the trace.xls
    # =======================================================================
    def outputTrace(self, message):
        pass
    
    # =======================================================================
    #                        outputs data to "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        pass
    
    # =======================================================================
    #                       outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        pass
    
    # =======================================================================
    #      takes the array and checks if all its values are identical 
    #   (returns false) or not (returns true) needed because if somebody 
    #       runs multiple runs in deterministic case it would crash!
    # =======================================================================          
    def checkIfArrayHasDifValues(self, array):
        difValuesFlag=False 
        for i in range(1, len(array)):
           if(array[i]!=array[1]):
               difValuesFlag=True
        return difValuesFlag 
    
    # =======================================================================
    #                           returns the resource
    # =======================================================================
    def getResource(self):
        return self.Res
    
    # =======================================================================
    #               returns the active queue of the resource
    # =======================================================================
    def getResourceQueue(self):
        return self.Res.activeQ
    
    # =======================================================================
    # check if the resource is already initialized
    # =======================================================================
    def isInitialized(self):
        return self.initialized
    
