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
from OperatorRouter import Router
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
        #create an empty Operator Pool. This will be updated by canAcceptAndIsRequested
        id = self.id+'_OP'
        name=self.objName+'_operatorPool'
        self.operatorPool=OperatorPool(id, name, operatorsList=[])
        from Globals import G
        G.OperatorPoolsList.append(self.operatorPool)
        self.operatorPool.initialize()
        self.operatorPool.operators=[]
        #create a Broker
        self.broker = Broker(self)
        activate(self.broker,self.broker.run())
        #create a Router
        from Globals import G
        if len(G.RoutersList)==0:
            self.router=Router()
            activate(self.router,self.router.run())
            G.RoutersList.append(self.router)
        # otherwise set the already existing router as the machines Router
        else:
            self.router=G.RoutersList[0]
        # holds the Entity that is to be obtained and will be updated by canAcceptAndIsRequested
        self.entityToGet=None

        
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
        giverObject=activeObject.getGiverObject()
        giverObjectQueue=giverObject.getActiveObjectQueue()
        # if the multOperationTypeList of the machine contains Load or Setup
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            if giverObject.haveToDispose(activeObject):
                #===============================================================
                # # TODO:  check whether this entity is the one to be hand in
                # #     to be used in operatorPreemptive
                # activeObject.requestingEntity=activeObject.giver.getActiveObjectQueue()[0]
                # # TODO:  update the object requesting the operator
                # activeObject.operatorPool.requestingObject=activeObject.giver
                # # TODO:  update the last object calling the operatorPool
                # activeObject.operatorPool.receivingObject=activeObject
                #===============================================================
                if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity\
                    and activeObject.checkOperator():
                    if not giverObject.exitIsAssignedTo():
                        giverObject.assignExitTo()
                    elif giverObject.exitIsAssignedTo()!=activeObject:
                        return False
                    # if the activeObject is not in manager's activeCallersList of the entityToGet
                    if activeObject not in giverObjectQueue[0].manager.activeCallersList:
                        # append it to the activeCallerList of the manager of the entity to be received
                        giverObjectQueue[0].manager.activeCallersList.append(self)
                        # update entityToGet
                        activeObject.entityToGet=giverObjectQueue[0]
                    #make the operators List so that it holds only the manager of the current order
                    activeObject.operatorPool.operators=[giverObjectQueue[0].manager]
                    # read the load time of the machine
                    activeObject.readLoadTime()
                    return True
            else:
                return False
        # if the multOperationTypeList contains only Processing
        elif (activeObject.operatorPool!='None' and any(type=='Processing' for type in activeObject.multOperationTypeList)):
            if giverObject.haveToDispose(activeObject):
                #===============================================================
                # # TODO:  check whether this entity is the one to be hand in
                # #     to be used in operatorPreemptive
                # activeObject.requestingEntity=activeObject.giver.getActiveObjectQueue()[0]
                # # TODO:  update the object requesting the operator
                # activeObject.operatorPool.requestingObject=activeObject.giver
                # # TODO:  update the last object calling the operatorPool
                # activeObject.operatorPool.receivingObject=activeObject
                #===============================================================
                
                # TODO: the operator must not be available for the object to receive the entity
                #     the exit of the giver should not be assigned
                #     the manager must not be available for the entity to be delivered
                #     the machine can be appended to the activeCallersList of the manager
                #        there may be a problem with the activeCallersList as the Router may assign 
                #        the operator to the machine while he is not needed for receiving the entity
                #     the entityToGet should be updated
                if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity:#\
#                     and self.checkOperator()\
#                     and not activeObject.giver.exitIsAssignedTo():
#                     activeObject.giver.assignExitTo()
#                     # if the activeObject is not in manager's activeCallersList of the entityToGet
#                     if self not in activeObject.giver.getActiveObjectQueue()[0].manager.activeCallersList:
#                         # append it to the activeCallerList of the manager of the entity to be received
#                         activeObject.giver.getActiveObjectQueue()[0].manager.activeCallersList.append(self)
#                         # update entityToGet
#                         self.entityToGet=activeObject.giver.getActiveObjectQueue()[0]
                    activeObject.entityToGet=giverObjectQueue[0]
                    #make the operators List so that it holds only the manager of the current order
                    activeObject.operatorPool.operators=[giverObjectQueue[0].manager]
                    # read the load time of the machine
                    activeObject.readLoadTime()
                    return True
            else:
                return False
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            if activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity and giverObject.haveToDispose(activeObject):
                # update entityToGet
                activeObject.entityToGet=self.giver.getActiveObjectQueue()[0]
                activeObject.readLoadTime()
            return activeObject.checkIfActive() and len(activeObjectQueue)<activeObject.capacity and giverObject.haveToDispose(activeObject)

    # =======================================================================
    # to be called by canAcceptAndIsRequested and check for the operator
    # =======================================================================    
    def checkOperator(self): #, candidateEntity=None):
        activeObject=self.getActiveObject()
        giverObject=activeObject.getGiverObject()
        giverObjectQueue=giverObject.getActiveObjectQueue()
        if giverObjectQueue[0].manager:
            manager=giverObjectQueue[0].manager
#             print ''
#             print 'Entity',self.giver.getActiveObjectQueue()[0].id
#             print 'manager',manager.id
            return manager.checkIfResourceIsAvailable()
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
    
#     # =======================================================================
#     # checks if the object is ready to receive an Entity
#     # =======================================================================    
#     def isReadyToGet(self):
#         # check if the entity that is about to be obtained has a manager (this should be true for this object)
#         if self.entityToGet.manager:
#             manager=self.entityToGet.manager
#             if len(manager.activeCallersList)>0:
#                 manager.sortEntities()      # sort the callers of the manager to be used for scheduling rules
#                 # return true if the manager is available
#                 return manager.checkIfResourceIsAvailable()
#         else:
#             return True
        

#     # =======================================================================
#     #                   prepare the machine to be released
#     # =======================================================================
#     def releaseOperator(self):
#         self.outputTrace(self.currentOperator.objName, "released from "+ self.objName)
# #         # TESTING
# #         print now(), self.id, 'will release operator', self.operatorPool.operators[0].objName
#         # set the flag operatorAssignedTo to None
#         self.currentOperator.operatorAssignedTo=None
#         self.broker.invokeBroker()
#         self.toBeOperated = False

