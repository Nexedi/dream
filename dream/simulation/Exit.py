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

# from SimPy.Simulation import now, Process, Resource, infinity, waituntil, waitevent
import simpy
import xlwt
from CoreObject import CoreObject

# ===========================================================================
#                            The exit object
# ===========================================================================
class Exit(CoreObject):
    family='Exit'
    
    
    def __init__(self, id, name, **kw):
        self.type="Exit" # XXX needed ?
        #lists to hold statistics of multiple runs
        self.Exits=[]
        self.UnitExits=[]
        self.Lifespan=[] 
        self.TaktTime=[]   
        # if input is given in a dictionary
        CoreObject.__init__(self, id, name) 
        from Globals import G
        G.ExitList.append(self)           
                   
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
        
        # initialize the internal Queue (type Resource) of the Exit 
        self.Res=simpy.Resource(self.env, capacity=float('inf'))         
        # The number of resource that exited through this exit.
        # XXX bug: cannot output as json when nothing has exited.
        self.numOfExits=0
        self.totalNumberOfUnitsExited=0
        self.totalLifespan=0
        
        self.totalTaktTime=0            # the total time between to consecutive exits    
        self.intervalThroughPutList=[]
        
        self.expectedSignals['isRequested']=1                         
                                                      
  
    def run(self):
        while 1:
            # wait until the Queue can accept an entity and one predecessor requests it
            self.expectedSignals['isRequested']=1
            yield self.isRequested
            self.isRequested=self.env.event()
            # TODO: insert extra controls to check whether the self.giver attribute is correctly updated
            self.getEntity()
            self.signalGiver()

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
#         G.pendingEntities[:]=(entity for entity in G.pendingEntities if not entity is activeEntity)
        if G.RouterList:
            if activeEntity in G.pendingEntities:
                G.pendingEntities.remove(activeEntity)
#         if activeEntity in G.EntityList:
#             G.EntityList.remove(activeEntity)
#         self.clear(activeEntity)
        self.totalLifespan+=self.env.now-activeEntity.startTime    #Add the entity's lifespan to the total one. 
        self.numOfExits+=1                                          # increase the exits by one
        self.totalNumberOfUnitsExited+=activeEntity.numberOfUnits   # add the number of units that xited
        self.totalTaktTime+=self.env.now-self.timeLastEntityLeft           # add the takt time
        self.timeLastEntityLeft=self.env.now                               # update the time that the last entity left from the Exit
        activeObjectQueue=self.getActiveObjectQueue()
        del self.Res.users[:]
        return activeEntity
    
    @staticmethod
    def clear(entity):
        from Globals import G
        def deleteEntityfromlist(entity, list):            
            if entity in list:
                list.remove(entity)
        lists=(G.EntityList, G.PartList, G.pendingEntities, G.WipList)
#         lists=(G.EntityList, G.PartList, G.BatchList, G.SubBatchList,
#                G.JobList, G.OrderList, G.OrderComponentList, G.MouldList,
#                G.pendingEntities, G.WipList)
        for list in lists:
            deleteEntityfromlist(entity,list)
    
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
    #                        outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        json = { '_class': 'Dream.%s' % self.__class__.__name__,
                  'id': self.id,
                  'family': self.family,
                  'results': {} }
        json['results']['throughput'] = self.Exits
        json['results']['lifespan'] = self.Lifespan
        json['results']['takt_time'] = self.TaktTime
        if self.Exits!=self.UnitExits:      #output this only if there was variability in units
            json['results']['unitsThroughput'] = self.UnitExits
        G.outputJSON['elementList'].append(json)
