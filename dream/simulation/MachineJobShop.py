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
extends the machine object so that it can act as a jobshop station. It reads the processing time and the successive station from the Entity
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold

from Machine import Machine

#the MachineJobShop object
class MachineJobShop(Machine):
    
    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):
        avtiveEntity=Machine.getEntity(self)     #run the default code
        self.procTime=avtiveEntity.remainingRoute[0][1]     #read the processing time from the entity
        self.nextStationId=avtiveEntity.remainingRoute[1][0]    #read the next station id
        avtiveEntity.remainingRoute.pop(0)      #remove data from the remaining route of the entity
        return avtiveEntity  
                                                                               
    #calculates the processing time
    def calculateProcessingTime(self):
        return self.procTime    #this is the processing time for this unique entity 

    #checks if the Machine can dispose an entity. Returns True only to the potential receiver     
    def haveToDispose(self, callerObject=None):
        if callerObject!=None:
            #check it the object that called the method holds an Entity that requests for current object        
            #if self.getActiveObjectQueue()[0].remainingRoute[0][0]==callerObject.id:
            if self.getReceiverObject()==callerObject:
                return len(self.getActiveObjectQueue())>0 and self.waitToDispose and self.Up   #return according to the state of the machine
        return False
                
                
    #get the receiver object in a removeEntity transaction.  
    def getReceiverObject(self):
        if len(self.getActiveObjectQueue())>0:
            from Globals import G
            receiverObjectId=self.getActiveObjectQueue()[0].remainingRoute[0][0]
            #loop through the objects to to assign the next station to the one that has the id
            for obj in G.ObjList:
                if obj.id==receiverObjectId:
                    return obj    
        else: 
            return None 
                