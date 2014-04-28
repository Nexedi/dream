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

from SimPy.Simulation import now, Process, Resource, infinity, waituntil, waitevent
import xlwt
from CoreObject import CoreObject

# ===========================================================================
#                            The exit object
# ===========================================================================
class Exit(CoreObject):
    class_name = 'Dream.Exit'
    def __init__(self, id, name=None):
        if not name:
          name = id
        CoreObject.__init__(self, id, name)
        self.predecessorIndex=0         # holds the index of the predecessor from which the Exit will take an entity next
        # general properties of the Exit
        self.type="Exit" # XXX needed ?
        
        #lists to hold statistics of multiple runs
        self.Exits=[]
        self.UnitExits=[]
        self.Lifespan=[] 
        self.TaktTime=[]                  

        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        
        # initialize the internal Queue (type Resource) of the Exit 
        self.Res=Resource(capacity=infinity)         
        # The number of resource that exited through this exit.
        # XXX bug: cannot output as json when nothing has exited.
        self.numOfExits=0
        self.totalNumberOfUnitsExited=0
        self.totalLifespan=0
        
        self.totalTaktTime=0            # the total time between to consecutive exits    
        self.intervalThroughPutList=[]                                  
                                                      
  
    def run(self):
        while 1:
            # wait until the Queue can accept an entity and one predecessor requests it
            yield waitevent, self, self.isRequested
            # TODO: insert extra controls to check whether the self.giver attribute is correctly updated
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
    def canAcceptAndIsRequested(self,callerObject=None):
        # get the active object and its internal queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
#         giverObject=activeObject.getGiverObject()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested' 
        return giverObject.haveToDispose(self)
    
    # =======================================================================
    #                    gets an entity from the predecessor     
    # =======================================================================
    def getEntity(self): 
        activeEntity = CoreObject.getEntity(self)           #run the default method
        # if the entity is in the G.pendingEntities list then remove it from there
        from Globals import G
        if activeEntity in G.pendingEntities:
            G.pendingEntities.remove(activeEntity)
        self.totalLifespan+=now()-activeEntity.startTime    #Add the entity's lifespan to the total one. 
        self.numOfExits+=1                                          # increase the exits by one
        self.totalNumberOfUnitsExited+=activeEntity.numberOfUnits   # add the number of units that xited
        self.totalTaktTime+=now()-self.timeLastEntityLeft           # add the takt time
        self.timeLastEntityLeft=now()                               # update the time that the last entity left from the Exit
        return activeEntity
    
    #===========================================================================
    # haveToDispose of an exit must always return False
    #===========================================================================
    def haveToDispose(self, callerObject=None):
        return False
    
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
        from Globals import getConfidenceIntervals
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
            throughput_ci = getConfidenceIntervals(self.Exits)
            G.outputSheet.write(G.outputIndex, 1, throughput_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, throughput_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, throughput_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean Lifespan of an entity that exited from "+ self.objName  + " is:")
            lifespan_ci = getConfidenceIntervals(self.Lifespan)
            G.outputSheet.write(G.outputIndex, 1, lifespan_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, lifespan_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, lifespan_ci['max'])
            G.outputIndex+=1

            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the avg takt time in "+ self.objName  + " is:")
            takt_time_ci = getConfidenceIntervals(self.TaktTime)
            G.outputSheet.write(G.outputIndex, 1, takt_time_ci['min'])
            G.outputSheet.write(G.outputIndex, 2, takt_time_ci['avg'])
            G.outputSheet.write(G.outputIndex, 3, takt_time_ci['max'])
            G.outputIndex+=1
        G.outputIndex+=1
    # =======================================================================
    #                        outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        from Globals import getConfidenceIntervals
        json = { '_class': self.class_name,
                  'id': self.id,
                  'results': {} }
        if(G.numberOfReplications==1):
            json['results']['throughput']=self.numOfExits
            if self.totalNumberOfUnitsExited!=self.numOfExits:   #output this only if there was variability in units
                json['results']['unitsThroughput']=self.totalNumberOfUnitsExited
            if len(self.intervalThroughPutList):    #output this only if there is an interval throughput
                                                    #TODO - check how to output in stochastic cases
                json['results']['intervalThroughputList']=self.intervalThroughPutList
            json['results']['lifespan']=self.Lifespan[0]
            json['results']['takt_time']=self.TaktTime[0]
        else:
            json['results']['throughput'] =self.Exits
            json['results']['lifespan'] = self.Lifespan
            json['results']['takt_time'] = self.TaktTime
            if self.Exits!=self.UnitExits:      #output this only if there was variability in units
                json['results']['unitsThroughput'] = self.UnitExits
#             json['results']['throughput'] = getConfidenceIntervals(self.Exits)
#             json['results']['lifespan'] = getConfidenceIntervals(self.Lifespan)
#             json['results']['takt_time'] = getConfidenceIntervals(self.TaktTime)
#             if self.Exits!=self.UnitExits:      #output this only if there was variability in units
#                 json['results']['unitsThroughput'] = getConfidenceIntervals(self.UnitExits)

        G.outputJSON['elementList'].append(json)
