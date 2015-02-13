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
Created on 2 oct 2012

@author: George
'''
'''
extends the Exit object so that it can act as a jobshop station. Preceding station is read from the Entity
'''

# from SimPy.Simulation import Process, Resource
# from SimPy.Simulation import activate, passivate, waituntil, now, hold
import simpy
from Exit import Exit

# ===========================================================================
# the ExitJobShop object
# ===========================================================================
class ExitJobShop(Exit):   
    
    # =======================================================================
    # set all the objects in previous
    # =======================================================================
    def initialize(self):
        from Globals import G
        self.previous=G.ObjList
        Exit.initialize(self)   #run default behaviour
        
    #===========================================================================
    # method used to check whether the station is in the entity-to-be-received route
    # TODO: consider giving the activeEntity as attribute
    #===========================================================================
    def isInRouteOf(self, callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        thecaller=callerObject
        # if the caller is not defined then return True. We are only interested in checking whether 
        # the station can accept whatever entity from whichever giver
        if not thecaller:
            return True
        #check it the caller object holds an Entity that requests for current object
        if len(thecaller.getActiveObjectQueue())>0:
            # TODO: make sure that the first entity of the callerObject is to be disposed
            activeEntity=thecaller.getActiveObjectQueue()[0]
            # if the machine's Id is in the list of the entity's next stations
            if activeObject.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                return True
        return False
    
