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
Created on 6 Feb 2013

@author: George
'''
'''
models the exit of the model
'''

from SimPy.Simulation import now, Process, Resource, infinity, waituntil
import xlwt
import scipy.stats as stat
from CoreObject import CoreObject
# ===========================================================================
#                            The exit object
# ===========================================================================
class Exit(CoreObject):    
          
    def __init__(self, id, name):
        CoreObject.__init__(self)
        Process.__init__(self)
        self.predecessorIndex=0         # holds the index of the predecessor from which the Exit will take an entity next
        # general properties of the Exit
        self.id=id
        self.objName=name
        self.type="Exit"
#         # list with routing information
#         self.previous=[]                # list with the previous objects in the flow
#         self.nextIds=[]                 # list with the ids of the next objects in the flow. For the exit it is always empty!
#         self.previousIds=[]             # list with the ids of the previous objects in the flow
        
        #lists to hold statistics of multiple runs
        self.Exits=[]
        self.UnitExits=[]
        self.Lifespan=[] 
        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        # no predecessorIndex nor successorIndex
        
        # initialize the internal Queue (type Resource) of the Exit 
        self.Res=Resource(capacity=infinity)         
        # The number of resource that exited through this exit.
        # XXX bug: cannot output as json when nothing has exited.
        self.numOfExits=0
        self.totalNumberOfUnitsExited=0
        self.totalLifespan=0
        
        self.totalTaktTime=0            # the total time between to consecutive exits    
        self.TaktTime=[]                # list that holds the avg time between to consecutive exits     
        self.dailyThroughPutList=[]                                  
                                                      
  
    def run(self):
        while 1:
            yield waituntil, self, self.canAcceptAndIsRequested     # wait until the Queue can accept an entity
                                                                     # and one predecessor requests it  
            self.getEntity()                                                                                                  

    # =======================================================================
    #                sets the routing in element for the Exit
    # =======================================================================
    def defineRouting(self, predecessorList=[]):
        self.previous=predecessorList                               # no successorList for the Exit
    # =======================================================================
    #                checks if the Exit can accept an entity       
    # =======================================================================    
    def canAccept(self, callerObject=None): 
        return True                                                 #the exit always can accept an entity
    # =======================================================================
    #                checks if the Exit can accept an entity 
    #                 and there is an entity waiting for it
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get the active object and its internal queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        # check if there is only one predecessor 
        # and if true is returned then control if the 
        # predecessor has an Entity to dispose off 
        if(len(activeObject.previous)==1):  
            object=activeObject.previous[0]
            return object.haveToDispose(self)    
    
        isRequested=False   # dummy variable used to check if any of the  possible givers has something to deliver
        # check if any of the possible givers has something to deliver
        # if yes, then return true and update the giver
        for object in self.previous:
            if(object.haveToDispose(activeObject) and object.receiver==self): 
                isRequested=True
                self.giver=object
        return isRequested
    # =======================================================================
    #                    gets an entity from the predecessor     
    # =======================================================================
    def getEntity(self): 
        activeEntity = CoreObject.getEntity(self)           #run the default method
        self.totalLifespan+=now()-activeEntity.startTime    #Add the entity's lifespan to the total one. 
        self.numOfExits+=1                                          # increase the exits by one
        self.totalNumberOfUnitsExited+=activeEntity.numberOfUnits   # add the number of units that xited
        self.totalTaktTime+=now()-self.timeLastEntityLeft           # add the takt time
        self.timeLastEntityLeft=now()                               # update the time that the last entity left from the Exit
        return activeEntity          

    # =======================================================================
    #            actions to be taken after the simulation ends
    # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        from Globals import G
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
        # hold the numberOfExits of each replication
        self.Exits.append(self.numOfExits)
        self.UnitExits.append(self.totalNumberOfUnitsExited) 
        try:                            # throw exception in case the numOfExits is zero
            self.Lifespan.append(((self.totalLifespan)/self.numOfExits)/G.Base)
        except ZeroDivisionError:       # the lifespan in this case is zero
            self.Lifespan.append(0)
        try:                            # throw exception in case of zero division
            self.TaktTime.append(((self.totalTaktTime)/self.numOfExits)/G.Base)
        except ZeroDivisionError:       # the average time between exits is zero if no Entity exited
            self.TaktTime.append(0)
            
    # =======================================================================
    #                        outputs data to "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G   
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            G.outputSheet.write(G.outputIndex,0, "The Throughput in " +self.objName + " is:")
            G.outputSheet.write(G.outputIndex,1,self.numOfExits)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The average lifespan of an entity that exited from "+ self.objName  +" is:")
            try:
                G.outputSheet.write(G.outputIndex,1,((self.totalLifespan)/self.numOfExits)/G.Base)
            except ZeroDivisionError:
                G.outputSheet.write(G.outputIndex,1,0)
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "The average takt time in "+ self.objName  +" is:")            
            try:
                G.outputSheet.write(G.outputIndex,1,((self.totalTaktTime)/self.numOfExits)/G.Base)
            except ZeroDivisionError:
                G.outputSheet.write(G.outputIndex,1,0)
            G.outputIndex+=1            
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value                 
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean Throughput in " +self.objName + " is:")
            if self.checkIfArrayHasDifValues(self.Exits): 
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][1][1])  
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Exits[0])
                G.outputSheet.write(G.outputIndex,2,self.Exits[0])
                G.outputSheet.write(G.outputIndex,3,self.Exits[0])                            
            G.outputIndex+=1
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean Lifespan of an entity that exited from "+ self.objName  + " is:")            
            if self.checkIfArrayHasDifValues(self.Lifespan):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Lifespan[0])
                G.outputSheet.write(G.outputIndex,2,self.Lifespan[0])
                G.outputSheet.write(G.outputIndex,3,self.Lifespan[0]) 
            G.outputIndex+=1
            
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the avg takt time in "+ self.objName  + " is:")            
            if self.checkIfArrayHasDifValues(self.TaktTime):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.TaktTime[0])
                G.outputSheet.write(G.outputIndex,2,self.TaktTime[0])
                G.outputSheet.write(G.outputIndex,3,self.TaktTime[0]) 
            G.outputIndex+=1
        G.outputIndex+=1
    # =======================================================================
    #                        outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            json={}
            json['_class'] = 'Dream.Exit';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['throughput']=self.numOfExits
            if self.totalNumberOfUnitsExited!=self.numOfExits:   #output this only if there was variability in units
                json['results']['unitsThroughput']=self.totalNumberOfUnitsExited
            if len(self.dailyThroughPutList):
                json['results']['dailyThroughputList']=self.dailyThroughPutList
            json['results']['lifespan']=self.Lifespan[0]
            json['results']['takt_time']=self.TaktTime[0]            
                
        else: #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value           
            json={}
            json['_class'] = 'Dream.Exit';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['throughput']={}
            if self.checkIfArrayHasDifValues(self.Exits):
                json['results']['throughput']['min']=stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][1][0]
                json['results']['throughput']['avg']=stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][0]
                json['results']['throughput']['max']=stat.bayes_mvs(self.Exits, G.confidenceLevel)[0][1][1]
            else:
                json['results']['throughput']['min']=self.Exits[0]
                json['results']['throughput']['avg']=self.Exits[0]
                json['results']['throughput']['max']=self.Exits[0]   
            if self.Exits!=self.UnitExits:      #output this only if there was variability in units
                json['results']['unitThroughput']={}
                if self.checkIfArrayHasDifValues(self.Exits):
                    json['results']['throughput']['min']=stat.bayes_mvs(self.UnitExits, G.confidenceLevel)[0][1][0]
                    json['results']['throughput']['avg']=stat.bayes_mvs(self.UnitExits, G.confidenceLevel)[0][0]
                    json['results']['throughput']['max']=stat.bayes_mvs(self.UnitExits, G.confidenceLevel)[0][1][1]
                else:
                    json['results']['throughput']['min']=self.UnitExits[0]
                    json['results']['throughput']['avg']=self.UnitExits[0]
                    json['results']['throughput']['max']=self.UnitExits[0]                           
            json['results']['lifespan']={}
            if self.checkIfArrayHasDifValues(self.Lifespan):
                json['results']['lifespan']['min']=stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][1][0]
                json['results']['lifespan']['avg']=stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][0]
                json['results']['lifespan']['max']=stat.bayes_mvs(self.Lifespan, G.confidenceLevel)[0][1][1]
            else:
                json['results']['lifespan']['min']=self.Lifespan[0]
                json['results']['lifespan']['avg']=self.Lifespan[0]
                json['results']['lifespan']['max']=self.Lifespan[0]                
            json['results']['taktTime']={}            
            if self.checkIfArrayHasDifValues(self.TaktTime):
                json['results']['taktTime']['min']=stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][1][0]
                json['results']['taktTime']['avg']=stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][0]
                json['results']['taktTime']['max']=stat.bayes_mvs(self.TaktTime, G.confidenceLevel)[0][1][1]
            else:
                json['results']['taktTime']['min']=self.TaktTime[0]
                json['results']['taktTime']['avg']=self.TaktTime[0]
                json['results']['taktTime']['max']=self.TaktTime[0]        
        G.outputJSON['elementList'].append(json)
