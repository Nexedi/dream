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

from SimPy.Simulation import Resource
import xlwt
import scipy.stats as stat
from ObjectResource import ObjectResource

#the resource that repairs the machines
class Repairman(ObjectResource):
    
    def __init__(self, id, name, capacity):    
        self.id=id      
        self.objName=name
        self.capacity=capacity  #repairman is an instance of resource
        self.type="Repairman"
        
        #lists to hold statistics of multiple runs
        self.Waiting=[]
        self.Working=[]
        
        self.coreObjectIds=[]   #list with the coreObjects that the repairman repairs
                
    
    #actions to be taken after the simulation ends
    def postProcessing(self, MaxSimtime):
        #if the repairman is currently working we have to count the time of this work    
        if len(self.Res.activeQ)>0:
            self.totalWorkingTime+=now()-self.timeLastRepairStarted
                
        #Repairman was idle when he was not in any other state
        self.totalWaitingTime=MaxSimtime-self.totalWorkingTime   
        
        self.Waiting.append(100*self.totalWaitingTime/MaxSimtime)
        self.Working.append(100*self.totalWorkingTime/MaxSimtime)

    #outputs data to "output.xls"
    def outputResultsXL(self, MaxSimtime):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            G.outputSheet.write(G.outputIndex,0, "The percentage of working of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWorkingTime/MaxSimtime)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The percentage of waiting of "+self.objName +" is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWaitingTime/MaxSimtime)
            G.outputIndex+=1
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value                 
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Working of "+self.objName +" is:")
            if self.checkIfArrayHasDifValues(self.Working): 
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1])  
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Working[0])
                G.outputSheet.write(G.outputIndex,2,self.Working[0])
                G.outputSheet.write(G.outputIndex,3,self.Working[0])                            
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+self.objName +" is:")            
            if self.checkIfArrayHasDifValues(self.Waiting):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Waiting[0])
                G.outputSheet.write(G.outputIndex,2,self.Waiting[0])
                G.outputSheet.write(G.outputIndex,3,self.Waiting[0]) 
            G.outputIndex+=1
        G.outputIndex+=1

    #outputs results to JSON File
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            json={}
            json['_class'] = 'Dream.Repairman';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
        else: #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value           
            json={}
            json['_class'] = 'Dream.Repairman';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['working_ratio']={}
            if self.checkIfArrayHasDifValues(self.Working):
                json['results']['working_ratio']['min']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0]
                json['results']['working_ratio']['avg']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0]
                json['results']['working_ratio']['max']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1]
            else:
                json['results']['working_ratio']['min']=self.Working[0]
                json['results']['working_ratio']['avg']=self.Working[0]
                json['results']['working_ratio']['max']=self.Working[0]                
            json['results']['waiting_ratio']={}
            if self.checkIfArrayHasDifValues(self.Waiting):
                json['results']['waiting_ratio']['min']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][0]
                json['results']['waiting_ratio']['avg']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][0]
                json['results']['waiting_ratio']['max']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][1]
            else:
                json['results']['waiting_ratio']['min']=self.Waiting[0]
                json['results']['waiting_ratio']['avg']=self.Waiting[0]
                json['results']['waiting_ratio']['max']=self.Waiting[0] 
                
        G.outputJSON['elementList'].append(json)
        
