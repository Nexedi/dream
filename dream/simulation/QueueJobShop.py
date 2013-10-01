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
Created on 1 oct 2012

@author: George
'''
'''
extends the Queue object so that it can act as a jobshop station. Preceding station from the Entity
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold

from Queue import Queue

from RandomNumberGenerator import RandomNumberGenerator

#the MachineJobShop object
class QueueJobShop(Queue):
    
    #checks if the Queue can accept an entity       
    #it checks also who called it and returns TRUE only to the object that will give the entity.  
    def canAccept(self, callerObject=None): 
        if callerObject!=None:
            #check it the caller object holds an Entity that requests for current object
            if len(callerObject.Res.activeQ)>0:
                activeEntity=callerObject.Res.activeQ[0]
                if activeEntity.remainingRoute[0][0]==self.id:
                    return len(self.Res.activeQ)<self.capacity  #return according to the state of the Queue
        return False

    #checks if the Queue can accept an entity and there is an entity in some predecessor waiting for it
    #also updates the predecessorIndex to the one that is to be taken
    def canAcceptAndIsRequested(self):        
        from Globals import G
        #loop through the objects to see if there is one that holds an Entity requesting for current object
        for obj in G.ObjList:
            if len(obj.Res.activeQ)>0 and now()!=0:
                activeEntity=obj.Res.activeQ[0]
                if activeEntity.remainingRoute[0][0]==self.id:
                    self.previousStation=obj
                    return len(self.Res.activeQ)<self.capacity and self.previousStation.haveToDispose(self)
        return False
                
    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):
        self.Res.activeQ.append(self.previousStation.Res.activeQ[0])    #get the entity from the previous object
                                                                        #and put it in front of the activeQ       
        self.previousStation.removeEntity()                             #remove the entity from the previous object 
        self.Res.activeQ[0].remainingRoute[0][0]=""                     #remove data from the remaining route. 
                                                                        #This is needed so that the Queue will not request again for the Entity
        
        