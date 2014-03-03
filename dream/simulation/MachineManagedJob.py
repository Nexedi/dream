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
                # TODO:  check whether this entity is the one to be hand in
                #     to be used in operatorPreemptive
                activeObject.requestingEntity=activeObject.giver.getActiveObjectQueue()[0]
                # TODO:  update the object requesting the operator
                activeObject.operatorPool.requestingObject=activeObject.giver
                # TODO:  update the last object calling the operatorPool
                activeObject.operatorPool.receivingObject=activeObject
                              
                if activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                    and self.checkOperator()\
                    and not activeObject.giver.exitIsAssigned():
                    activeObject.giver.assignExit()
                    # if the activeObject is not in manager's activeCallersList of the entityToGet
                    if self not in activeObject.giver.getActiveObjectQueue()[0].manager.activeCallersList:
                        # append it to the activeCallerList of the manager of the entity to be received
                        activeObject.giver.getActiveObjectQueue()[0].manager.activeCallersList.append(self)
                        # update entityToGet
                        self.entityToGet=activeObject.giver.getActiveObjectQueue()[0]
                    #make the operators List so that it holds only the manager of the current order
                    activeObject.operatorPool.operators=[activeObject.giver.getActiveObjectQueue()[0].manager]
#                     # set the variable operatorAssignedTo to activeObject, the operator is then blocked
#                     activeObject.operatorPool.operators[0].operatorAssignedTo=activeObject
#                     # TESTING
#                     print now(), activeObject.operatorPool.operators[0].objName, 'got assigned to', activeObject.id
                    # read the load time of the machine
                    self.readLoadTime()
                    return True
            else:
                return False
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            if activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested:
                # update entityToGet
                self.entityToGet=self.giver.getActiveObjectQueue()[0]
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested 

    # =======================================================================
    # to be called by canAcceptAndIsRequested and check for the operator
    # =======================================================================    
    def checkOperator(self):
        if self.giver.getActiveObjectQueue()[0].manager:
            manager=self.giver.getActiveObjectQueue()[0].manager
#             print ''
#             print 'Entity',self.giver.getActiveObjectQueue()[0].id
#             print 'manager',manager.id
            return manager.checkIfResourceIsAvailable()
        else:
            return True    
        
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

