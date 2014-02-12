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
Created on 4 Feb 2014

@author: George
'''
'''
inherits from MachineJobShop. The difference is that it reads the operator from the Entity and
checks if he is available before it takes it
'''

from SimPy.Simulation import Process, Resource, activate, now

from OperatedPoolBroker import Broker
from OperatorPool import OperatorPool
from MachineJobShop import MachineJobShop

# ===========================================================================
# the MachineManagedJob object
# ===========================================================================
class MachineManagedJob(MachineJobShop):

    # =======================================================================
    # initialize the MachineManagedJob
    # =======================================================================
    def initialize(self):
        MachineJobShop.initialize(self)
        #creat an empty Operator Pool. This will be updated by canAcceptAndIsRequested
        id = self.id+'_OP'
        name=self.objName+'_operatorPool'
        self.operatorPool=OperatorPool(id, name, operatorsList=[])
        self.operatorPool.initialize()
        self.operatorPool.operators=[]
        #create a Broker
        self.broker = Broker(self)
        activate(self.broker,self.broker.run())
        
    # =======================================================================
    # checks if the Queue can accept an entity       
    # it checks also the next station of the Entity 
    # and returns true only if the active object is the next station
    # ======================================================================= 
    def canAccept(self, callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        thecaller=callerObject
        if (thecaller!=None):
            #check it the caller object holds an Entity that requests for current object
            if len(thecaller.getActiveObjectQueue())>0:
                # TODO: make sure that the first entity of the callerObject is to be disposed
                activeEntity=thecaller.getActiveObjectQueue()[0]
                # if the machine's Id is in the list of the entity's next stations
                if activeObject.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                    #return according to the state of the Queue
                    return len(activeObject.getActiveObjectQueue())<activeObject.capacity\
                        and activeObject.Up
        return False

    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some possible giver waiting for it
    # also updates the giver to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
    
        # dummy variables that help prioritise the objects requesting to give objects to the Machine (activeObject)
        isRequested=False                                           # is requested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked
        
        # loop through the possible givers to see which have to dispose and which is the one blocked for longer
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject) and object.receiver==self):# and not object.exitIsAssigned()):
                isRequested=True                                    # if the possible giver has entities to dispose of
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the possible giver has been down while trying to give away the Entity
                    timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                else:
                    timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
                
                #if more than one possible givers have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.giver=object                 # set the giver
                    maxTimeWaiting=timeWaiting    
        
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            if isRequested:
                # TODO: 
                # check whether this entity is the one to be hand in
                #     to be used in operatorPreemptive
                activeObject.requestingEntity=activeObject.giver.getActiveObjectQueue()[0]
                # TODO: 
                # update the object requesting the operator
                activeObject.operatorPool.requestingObject=activeObject.giver
                # TODOD: 
                # update the last object calling the operatorPool
                activeObject.operatorPool.receivingObject=activeObject
                              
                if activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                    and not activeObject.giver.exitIsAssigned():
                    activeObject.giver.assignExit()
                    #make the operatorsList so that it holds only the manager of the current order
#                     activeObject.operatorPool.operatorsList=[activeObject.giver.getActiveObjectQueue()[0].manager]
                    # TODO: think over the next line, this way sort entity is run multiple times throughout the life-span of 
                    #    an entity in the object. Maybe would be a good idea to pick the entity to be disposed from the giver
                    activeObject.giver.sortEntities()
                    activeObject.operatorPool.operators=[activeObject.giver.getActiveObjectQueue()[0].manager]
                    self.readLoadTime()
                    return True
            else:
                return False
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested
            # while if the set up is performed before the (automatic) loading of the machine then the availability of the
            # operator is requested
#             return (activeObject.operatorPool=='None' or activeObject.operatorPool.checkIfResourceIsAvailable())\
#                 and activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested    
    
