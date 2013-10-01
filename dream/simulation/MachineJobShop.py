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

from RandomNumberGenerator import RandomNumberGenerator

#the MachineJobShop object
class MachineJobShop(Machine):
    
    #gets an entity from the predecessor that the predecessor index points to     
    def getEntity(self):
        Machine.getEntity(self)     #run the default code
        avtiveEntity=self.Res.activeQ[0]
        self.procTime=avtiveEntity.remainingRoute[0][1]
        self.nextStationId=avtiveEntity.remainingRoute[1][0]
        avtiveEntity.remainingRoute.pop(0)
        from Globals import G
        for obj in G.ObjList:
            if obj.id==self.nextStationId:
                self.nextStation=obj       

    #checks if the machine down or it can dispose the object
    def ifCanDisposeOrHaveFailure(self):
         return self.Up==False or self.nextStation.canAccept(self) or len(self.Res.activeQ)==0  
                                                                                        #the last part is added so that it is not removed and stack
                                                                                        #gotta think of it again     
                                                                                
    #calculates the processing time
    def calculateProcessingTime(self):
        return self.procTime    #this is the processing time for this unique entity 

    #checks if the Machine can dispose an entity. Returns True only to the potential receiver     
    def haveToDispose(self, callerObject=None):
        if callerObject!=None:        
            if self.Res.activeQ[0].remainingRoute[0][0]==callerObject.id:
                return len(self.Res.activeQ)>0 and self.waitToDispose and self.Up
        return False
                
                
                
                