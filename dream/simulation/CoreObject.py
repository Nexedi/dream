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
Created on 12 Jul 2012

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All the core-objects should inherit from it
'''

from SimPy.Simulation import Process, Resource, now

# =================================== the core object ==============================================
class CoreObject(Process):
    
    def initialize(self):
        Process.__init__(self) 
        self.predecessorIndex=0                         #holds the index of the predecessor from which the Machine will take an entity next
        self.successorIndex=0                           #holds the index of the successor where the Machine will dispose an entity next
        self.Up=True                                    #Boolean that shows if the machine is in failure ("Down") or not ("up")
        self.currentEntity=None      
        # ============================== total times ===============================================
        self.totalBlockageTime=0                        #holds the total blockage time
        self.totalFailureTime=0                         #holds the total failure time
        self.totalWaitingTime=0                         #holds the total waiting time
        self.totalWorkingTime=0                         #holds the total working time
        self.completedJobs=0                            #holds the number of completed jobs 
        # ============================== Entity related attributes =================================
        self.timeLastEntityEnded=0                      #holds the last time that an entity ended processing in the object
        self.nameLastEntityEnded=""                     #holds the name of the last entity that ended processing in the object
        self.timeLastEntityEntered=0                    #holds the last time that an entity entered in the object
        self.nameLastEntityEntered=""                   #holds the name of the last entity that entered in the object
        self.timeLastFailure=0                          #holds the time that the last failure of the object started
        self.timeLastFailureEnded=0                     #holds the time that the last failure of the object Ended
        # ============================== failure related times =====================================
        self.downTimeProcessingCurrentEntity=0          #holds the time that the machine was down while 
                                                        #processing the current entity
        self.downTimeInTryingToReleaseCurrentEntity=0   #holds the time that the object was down while trying 
                                                        #to release the current entity  
        self.downTimeInCurrentEntity=0                  #holds the total time that the 
                                                        #object was down while holding current entity
        self.timeLastEntityLeft=0                       #holds the last time that an entity left the object
        
        self.processingTimeOfCurrentEntity=0            #holds the total processing time that the current entity required                                               
        # ============================== waiting flag ==============================================                                      
        self.waitToDispose=False                        #shows if the object waits to dispose an entity   


    # ======================== the main process of the core object =================================
    # ================ this is dummy, every object must have its own implementation ================
    def run(self):
        raise NotImplementedError("Subclass must define 'run' method")
        
    # ======================== sets the routing in and out elements for the Object ==================
    def defineRouting(self, predecessorList=[], successorList=[]):
        self.next=successorList
        self.previous=predecessorList

    # ================================== removes an entity from the Object ==========================
    def removeEntity(self): 
        activeObjectQueue=self.getActiveObjectQueue()  
        activeEntity=activeObjectQueue[0]  
        activeObjectQueue.pop(0)                        #remove the Entity from the queue
        self.timeLastEntityLeft=now()
        try:
            self.outputTrace(activeEntity.name, "released "+self.objName) 
        except TypeError:
            pass
        return activeEntity          
        
    # ================================== gets an entity from the ====================================
    # ===================== predecessor that the predecessor index points to ========================     
    def getEntity(self):
        # get giver object, its queue, and sort the entities according to this object priorities
        giverObject=self.getGiverObject()
        giverObject.sortEntities()                      #sort the Entities of the giver 
                                                        #according to the scheduling rule if applied
        giverObjectQueue=self.getGiverObjectQueue()
        # get active object and its queue, as well as the active (to be) entity 
        #(after the sorting of the entities in the queue of the giver object)
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        activeEntity=giverObjectQueue[0]
        #get the entity from the previous object and put it in front of the activeQ 
        activeObjectQueue.append(activeEntity)   
        #remove the entity from the previous object
        giverObject.removeEntity()
        #append the time to schedule so that it can be read in the result
        #remember that every entity has it's schedule which is supposed to be updated every time 
        # the entity enters a new object
        activeEntity.schedule.append([activeObject,now()])
        activeEntity.currentStation=self
        self.timeLastEntityEntered=now()
        try:
            self.outputTrace(activeEntity.name, "got into "+self.objName)
        except TypeError:
            pass
        return activeEntity
        
    # ========================== actions to be taken after the simulation ends ======================
    def postProcessing(self, MaxSimtime=None):
        pass    
    
    # =========================== outputs message to the trace.xls ==================================
    #outputs message to the trace.xls. Format is (Simulation Time | Entity or Frame Name | message)
    def outputTrace(self, entityName, message):
        from Globals import G
        if(G.trace=="Yes"):         #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(now()))
            G.traceSheet.write(G.traceIndex,1,entityName)
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1       #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)    
    
    # =========================== outputs data to "output.xls" ======================================
    def outputResultsXL(self, MaxSimtime=None):
        pass
    
    # =========================== outputs results to JSON File ======================================
    def outputResultsJSON(self):
        pass
    
    # ================= checks if the Object can dispose an entity to the following object ==========
    def haveToDispose(self, callerObject=None): 
        activeObjectQueue=self.getActiveObjectQueue()    
        return len(activeObjectQueue)>0
    
    
    #checks if the Object can accept an entity and there is an entity in some predecessor waiting for it
    def canAcceptAndIsRequested(self):
        pass
    
    # ============================ checks if the Object can accept an entity ========================
    def canAccept(self, callerObject=None): 
        pass
    
    # ===================== sorts the Entities in the activeQ of the objects ========================
    def sortEntities(self):
        pass
    #takes the array and checks if all its values are identical (returns false) or not (returns true) 
    #needed because if somebody runs multiple runs in deterministic case it would crash!          
    def checkIfArrayHasDifValues(self, array):
        difValuesFlag=False 
        for i in range(1, len(array)):
           if(array[i]!=array[1]):
               difValuesFlag=True
        return difValuesFlag 
      
    # ===================== get the active object. This always returns self ========================  
    def getActiveObject(self):
        return self
    
    # ========================== get the activeQ of the active object. =============================
    def getActiveObjectQueue(self):
        return self.Res.activeQ
    
    # =================== get the giver object in a getEntity transaction. =========================        
    def getGiverObject(self):
        return self.previous[self.predecessorIndex]
    
    # ============== get the giver object queue in a getEntity transaction. ========================    
    def getGiverObjectQueue(self):
        return self.getGiverObject().Res.activeQ
    
    # ============== get the receiver object in a removeEntity transaction.  ======================= 
    def getReceiverObject(self):
        return self.next[self.successorIndex]
    
    # ========== get the receiver object queue in a removeEntity transaction. ======================    
    def getReceiverObjectQueue(self):
        return self.getReceiverObject().Res.activeQ
    
    # =======================================================================
    # calculates the processing time
    # =======================================================================
    def calculateProcessingTime(self):
        return self.rng.generateNumber()                            # this is if we have a default processing time for all the entities