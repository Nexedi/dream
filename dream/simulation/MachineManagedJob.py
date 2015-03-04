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

# from SimPy.Simulation import Process, Resource, activate, now
import simpy

from OperatedPoolBroker import Broker
from OperatorPool import OperatorPool
from OperatorRouterManaged import RouterManaged
from MachineJobShop import MachineJobShop

# ===========================================================================
# the MachineManagedJob object
# ===========================================================================
class MachineManagedJob(MachineJobShop):

    # =======================================================================
    # initialise the MachineManagedJob
    # =======================================================================
    def initialize(self):
        MachineJobShop.initialize(self)
        self.type="MachineManagedJob"
        # holds the Entity that is to be obtained and will be updated by canAcceptAndIsRequested
        self.entityToGet=None
    
    #===========================================================================
    # create an operatorPool if needed
    #===========================================================================
    def createOperatorPool(self,operatorPool):
        #create an empty Operator Pool. This will be updated by canAcceptAndIsRequested
        id = self.id+'_OP'
        name=self.objName+'_operatorPool'
        self.operatorPool=OperatorPool(id, name, operatorsList=[])
        from Globals import G
        G.OperatorPoolsList.append(self.operatorPool)
    
   
    #===========================================================================
    # create router if needed
    #===========================================================================
    def createRouter(self):
        #create a Router
        from Globals import G
        if not G.RouterList:
            self.router=RouterManaged()
            G.RouterList[0]=self.router          
        # otherwise set the already existing router as the machines Router
        else:
            self.router=G.RouterList[0]
            
    #===========================================================================
    # initialize broker if needed
    #===========================================================================
    def initializeOperatorPool(self):
        self.operatorPool.initialize()
        self.operatorPool.operators=[]
    
    #===========================================================================
    # initialize broker if needed
    #===========================================================================
    def initializeBroker(self):
        self.broker.initialize()
        self.env.process(self.broker.run())
                
    #===========================================================================
    # initialize router if needed
    #===========================================================================
    def initializeRouter(self):
        if not self.router.isInitialized:
            self.router.initialize()
        if not self.router.isActivated:
            self.env.process(self.router.run())
            self.router.isActivated=True
    
    # =======================================================================
    # checks if the Queue can accept an entity       
    # TODO: cannot check here if the station in the route of the entity that will be received (if any)
    # as the giver (QueueManagedJob) will be sorted from giver.haveToDispose in self.canAcceptAndIsRequested method
    # ======================================================================= 
    def canAccept(self, callerObject=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        #return according to the state of the Queue
        return len(activeObjectQueue)<activeObject.capacity\
                    and activeObject.checkIfMachineIsUp()\
                    and not activeObject.entryIsAssignedTo()
    
    # =======================================================================
    # checks if the Queue can accept an specific Entity       
    # it checks also the next station of the Entity 
    # and returns true only if the active object is the next station
    # ======================================================================= 
    def canAcceptEntity(self, callerEntity=None):
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        thecallerentity=callerEntity
        if (thecallerentity!=None):
            # if the machine's Id is in the list of the entity's next stations
            if activeObject.id in thecallerentity.remainingRoute[0].get('stationIdsList',[]):
                #return according to the state of the Queue
                return len(activeObjectQueue)<activeObject.capacity\
                        and activeObject.checkIfMachineIsUp()
        return False

    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some possible giver waiting for it
    # also updates the giver to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
#         giverObject=activeObject.getGiverObject()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        giverObjectQueue=giverObject.getActiveObjectQueue()
        # if the multOperationTypeList of the machine contains Load or Setup
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            if giverObject.haveToDispose(activeObject):
                if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity\
                    and activeObject.checkOperator(giverObject):
                    if not giverObject.exitIsAssignedTo():
                        giverObject.assignExitTo(activeObject)
                    elif giverObject.exitIsAssignedTo()!=activeObject:
                        return False
                    # update entityToGet
                    activeObject.entityToGet=giverObjectQueue[0]
                    #make the operators List so that it holds only the manager of the current order
                    activeObject.operatorPool.operators=[giverObjectQueue[0].manager]
                    # read the load time of the machine
                    activeObject.readLoadTime(giverObject)
                    return True
            else:
                return False
        # if the multOperationTypeList contains only Processing
        elif (activeObject.operatorPool!='None' and any(type=='Processing' for type in activeObject.multOperationTypeList)):
            if giverObject.haveToDispose(activeObject):
                # the operator must not be available for the object to receive the entity
                #     the exit of the giver should not be assigned
                #     the manager must not be available for the entity to be delivered
                #        the operator to the machine while he is not needed for receiving the entity
                if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity:
                    # the entityToGet should be updated
                    activeObject.entityToGet=giverObjectQueue[0]
                    #make the operators List so that it holds only the manager of the current order
                    activeObject.operatorPool.operators=[giverObjectQueue[0].manager]
                    # read the load time of the machine
                    activeObject.readLoadTime(giverObject)
                    return True
            else:
                return False
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity and giverObject.haveToDispose(activeObject):
                # update entityToGet
                activeObject.entityToGet=giverObject.getActiveObjectQueue()[0]
                activeObject.readLoadTime(giverObject)
            return activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity and giverObject.haveToDispose(activeObject)

    # =======================================================================
    # to be called by canAcceptAndIsRequested and check for the operator
    # =======================================================================    
    def checkOperator(self,callerObject=None): #, candidateEntity=None):
        assert callerObject!=None, 'checkOperator must have a caller for MachineManagedJob'
        activeObject=self.getActiveObject()
#         giverObject=activeObject.getGiverObject()
        giverObject=callerObject
        giverObjectQueue=giverObject.getActiveObjectQueue()
        if giverObjectQueue[0].manager:
            manager=giverObjectQueue[0].manager
            # TODO: consider using a caller in this case
            return manager.checkIfResourceIsAvailable(activeObject)
        else:
            return True 
#         if candidateEntity:
#             if candidateEntity.manager:
#                 manager=candidateEntity.manager
#                 return manager.checkIfResourceIsAvailable()
#             else:
#                 return True
#         return False 
        
    # =======================================================================
    #             identifies the Entity to be obtained so that 
    #            getEntity gives it to removeEntity as argument
    # =======================================================================    
    def identifyEntityToGet(self):
        # ToDecide
        # maybe we should work this way in all CoreObjects???
        return self.entityToGet

