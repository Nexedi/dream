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
Created on 14 Nov 2012

@author: George
'''

'''
models a repairman that can fix a machine when it gets failures
'''

from SimPy.Simulation import Resource, now
import xlwt
from ObjectResource import ObjectResource

# ===========================================================================
#                 the resource that repairs the machines
# ===========================================================================
class Repairman(ObjectResource):
    class_name = 'Dream.Repairman'
    def __init__(self, id, name, capacity=1):
        ObjectResource.__init__(self)
        self.id=id
        self.objName=name
        self.capacity=capacity      # repairman is an instance of resource
        self.type="Repairman"
#         self.Res=Resource(self.capacity)
        # lists to hold statistics of multiple runs
        self.Waiting=[]             # holds the percentage of waiting time 
        self.Working=[]             # holds the percentage of working time 
        # list with the coreObjects IDs that the repairman repairs
        self.coreObjectIds=[]
        # list with the coreObjects that the repairman repairs
        self.coreObjects=[]
        
    # =======================================================================    
    #            actions to be taken after the simulation ends
    # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime
        # if the repairman is currently working we have to count the time of this work    
#         if len(self.getResourceQueue())>0:
        if not self.checkIfResourceIsAvailable():
            self.totalWorkingTime+=now()-self.timeLastOperationStarted
                
        # Repairman was idle when he was not in any other state
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime   
        # update the waiting/working time percentages lists
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)
    
    # =======================================================================
    #                    outputs data to "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G
        from Globals import getConfidenceIntervals
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
        # if we had just one replication output the results to excel
        if(G.numberOfReplications==1): 
            G.outputSheet.write(G.outputIndex,0, "The percentage of working of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWorkingTime/MaxSimtime)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The percentage of waiting of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWaitingTime/MaxSimtime)
            G.outputIndex+=1
        #if we had multiple replications we output confidence intervals to excel
            # for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
            # so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
            # so for each output value we check if there was difference in the runs' results
            # if yes we output the Confidence Intervals. if not we output just the fix value    
        else:
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Working of "+ self.objName+" is:")
            working_ci = getConfidenceIntervals(self.Working)
            G.outputSheet.write(G.outputIndex, 1, working_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, working_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, working_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+ self.objName+" is:")
            waiting_ci = getConfidenceIntervals(self.Waiting)
            G.outputSheet.write(G.outputIndex, 1, waiting_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, waiting_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, waiting_ci['max'])
            G.outputIndex+=1
        G.outputIndex+=1

    # =======================================================================
    #                    outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        from Globals import getConfidenceIntervals
        json = {'_class': self.class_name,
                'id': self.id,
                'results': {}}
        if(G.numberOfReplications==1):
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
        else:
            json['results']['working_ratio'] = getConfidenceIntervals(self.Working)
            json['results']['waiting_ratio'] = getConfidenceIntervals(self.Waiting)
        G.outputJSON['elementList'].append(json)
