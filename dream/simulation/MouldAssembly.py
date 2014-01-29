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
Created on 16 Jan 2014

@author: Ioannis
'''
'''
inherits from MachinePreemptive. It takes the components of an order and reassembles them as mould
'''

'''
the mould should be described in the componentList of the parent order 
as a dictionary with the following layout if the mould is not already in WIP
{
    "_class": "Dream.Mould",
    "id": "M1",
    "name": "Mould1",
    "isCritical": "1",
    "processingTime": {
        "distributionType": "Fixed",
        "mean": "0"
    },
    "route": [
        {
            "stepNumber": "0",
            "stationIdsList": [
                "MA1"
            ],                                                                # the mould assembly stations
            "processingTime": {
                "distributionType": "Fixed",
                "mean": "3"
            }
        },
        {
            "stepNumber": "1",
            "stationIdsList": [
                "IM1"
            ],                                                                # the injection moulding station
            "processingTime": {
                "distributionType": "Fixed",
                "mean": "4.25"
            }
        }
    ]
}
There is no need to assign an exit, exit is assigned automatically by the createMould method
TODOs: check the case when a mould is already in the WIP by the beginning of the simulation
'''
from MachinePreemptive import MachinePreemptive
from SimPy.Simulation import Resource, reactivate, now
from Globals import G

# =======================================================================
# Error in the assembling of the mould
# =======================================================================
class AssembleMouldError(Exception):
    def __init__(self, mouldAssembleError):
        Exception.__init__(self, mouldAssembleError) 

# ===========================================================================
# the MachineJobShop object
# ===========================================================================
class MouldAssembly(MachinePreemptive):
    # =======================================================================
    # the initialize method
    # =======================================================================
    def initialize(self):
        self.mouldParent = None                 # the mould's to be assembled parent order
        self.mouldToBeCreated = None            # the mould to be assembled
        MachinePreemptive.initialize(self)      # run default behaviour
        
    # =======================================================================
    # getEntity method that gets the entity from the giver
    # it should run in a loop till it get's all the entities from the same order
    # (with the flag componentsReadyForAssembly set)
    # it is run only once, and receives all the entities to be assembled inside a while loop
    # =======================================================================
    def getEntity(self):
        activeObject = self.getActiveObject()
        giverObejct = activeObject.getGiverObject()
        # get the first entity from the predecessor
        # TODO: each machinePreemtive.getEntity is invoked, 
        #     the self.procTime is updated. Have to decide where to assign 
        #     the processing time of the assembler 
        activeEntity=MachinePreemptive.getEntity(self)
        # check weather the activeEntity is of type Mould
        if activeEntity.type=='Mould':
            # and return the mould received
            return activeEntity
        # otherwise, collect all the entities to be assembled
        
        # read the number of basic and secondary components of the moulds
        capacity = len(activeEntity.order.basicComponentsList\
                       +activeEntity.order.secondaryComponentsList)
        # clear the active object queue
        del activeObject.getActiveObjectQueue()[:]
        # and set the capacity of the internal queue of the assembler
        activeObject.updateCapacity(capacity)
        # append the activeEntity to the activeObjectQueue
        activeObjectQueue = activeObject.getActiveObjectQueue()
        activeObjectQueue.append(activeEntity)
        # dummy variable to inform when the sum of needed components is received 
        # before the assembly-processing
        orderGroupReceived = False
        # all the components are received at the same time
        while not orderGroupReceived:
            # get the next component
            activeEntity=MachinePreemptive.getEntity(self)
            # check weather the activeEntity is of type Mould
            try:
                if activeEntity.type=='Mould':
            # and return the mould received
                    raise AssembleMouldError('Having already received an orderComponent the assembler\
                                                is not supposed to receive an object of type Mould')
            # check if the last component received has the same parent order as the previous one
                elif not (activeEntity.order is activeObjectQueue[1].order):
                    raise AssembleMouldError('The orderComponents received by the assembler must have the\
                                                same parent order')
            except AssembleMouldError as mouldError:
                print 'Mould Assembly Error: {0}'.format(mouldError)
                return False
            # if the length of the internal queue is equal to the updated capacity
            if len(activeObject.getActiveObjectQueue())==self.capacity:
            # then exit the while loop
                orderGroupReceived=True
        # perform the assembly-action and return the assembled mould
        activeEntity = activeObject.assemble()
        return activeEntity
    
    # =======================================================================
    # method that updates the capacity according to the componentsList of the 
    # activeEntity's parent order
    # =======================================================================
    def updateCapacity(self,capacity):
        activeObject = self.getActiveObject()
        self.capacity = capacity
        self.Res=Resource(self.capacity)
    
    # =======================================================================
    #     assemble method that assembles the components together to a mould (order
    # and returns the product of the assembly. Furthermore, it resets the capacity
    # of the internal queue to 1
    # =======================================================================
    def assemble(self):
        activeObject = self.getActiveObject()
        # get the internal queue of the active core object
        activeObjectQueue=activeObject.getActiveObjectQueue()
        # assert that all the components are of the same parent order
        for entity in activeObjectQueue:
            assert entity.order==activeObjectQueue[0].order,\
                'The components residing in the MouldAssembly internal queue\
                are not of the same parent order!'
        # if we have to create a new Entity (mould) this should be modified
        # we need the new entity's route, priority, isCritical flag, etc. 
        self.mouldParent = activeObjectQueue[0].order
        # assert that there is a parent order
        assert self.mouldParent.type=='Order', 'the type of the assembled to be mould\' s parent is not correct'
        # delete the contents of the internal queue
        for element in activeObjectQueue:
            activeObjectQueue.remove(element)
#         del activeObjectQueue[:]
        # after assembling reset the capacity
        activeObject.updateCapacity(1)
        #if there is a mould to be assembled
        try:
            if self.mouldParent:
                # find the component which is of type Mould
                # there must be only one mould component
                for entity in self.mouldParent.componentsList:
                    entityClass=entity.get('_class', None)
                    if entityClass=='Dream.Mould':
                        self.mouldToBeCreated=entity
                        break
                # create the mould
                self.createMould(self.mouldToBeCreated)
                # set the created mould as WIP
                import Globals
                Globals.setWIP([self.mouldToBeCreated])
                # read the activeObjectQueue again as it has been updated by the setWIP()
                activeObjectQueue=activeObject.getActiveObjectQueue()
                # reset attributes
                self.mouldParent = None
                self.mouldToBeCreated = None
                # return the assembled mould
                return activeObjectQueue[0]
            else:
                raise AssembleMouldError('There is no mould to be assembled')
        except AssembleMouldError as mouldError:
            print 'Mould Assembly Error: {0}'.format(mouldError)
            
    # =======================================================================
    # creates the mould
    # =======================================================================
    def createMould(self, component):
        #read attributes from the json or from the orderToBeDecomposed
        id=component.get('id', 'not found')
        name=component.get('name', 'not found')
        try:
            
            # dummy variable that holds the routes of the jobs the route from the JSON file is a sequence of dictionaries
            JSONRoute=component.get('route', [])
            # variable that holds the argument used in the Job initiation hold None for each entry in the 'route' list
            route = [None for i in range(len(JSONRoute))]         
                    
            for routeentity in JSONRoute:                                          # for each 'step' dictionary in the JSONRoute
                stepNumber=int(routeentity.get('stepNumber', '0'))                 #    get the stepNumbe
                route[stepNumber]=routeentity
            # assert that the assembler is in the moulds route and update the initial step of the mould's route
            firstStep = route.pop(0)
            assert (self.id in firstStep.get('stationIdsList',[])),\
                         'the assembler must be in the mould-to-be-created route\' initial step'
            processingTime=firstStep['processingTime']  
            # update the activeObject's processing time according to the readings in the mould's route
            self.distType=processingTime.get('distributionType','not found')
            self.procTime=float(processingTime.get('mean', 0))
            # update the first step of the route with the activeObjects id as sole element of the stationIdsList
            route.insert(0, {'stationIdsList':[str(self.id)],'processingTime':{'distributionType':str(self.distType),\
                                                                               'mean':str(self.procTime)}})
            #Below it is to assign an exit if it was not assigned in JSON
            #have to talk about it with NEX
            exitAssigned=False
            for element in route:
                elementIds = element.get('stationIdsList',[])
                for obj in G.ObjList:
                    for elementId in elementIds:
                        if obj.id==elementId and obj.type=='Exit':
                            exitAssigned=True 
            # assign an exit to the route of the mould 
            if not exitAssigned:
                exitId=None
                for obj in G.ObjList:
                    if obj.type=='Exit':
                        exitId=obj.id
                        break
                if exitId:
                    route.append({'stationIdsList':[str(exitId)],'processingTime':{}})
            # keep a reference of all extra properties passed to the job
            extraPropertyDict = {}
            for key, value in component.items():
                if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value
            # create and initiate the OrderComponent
            from Mould import Mould
            M=Mould(id, name, route, \
                              priority=self.mouldParent.priority, \
                              order=self.mouldParent,\
                              dueDate=self.mouldParent.dueDate, \
                              orderDate=self.mouldParent.orderDate, \
                              extraPropertyDict=extraPropertyDict,\
                              isCritical=self.mouldParent.isCritical)
            # update the mouldToBeCreated
            self.mouldToBeCreated=M
            G.JobList.append(M)
            G.WipList.append(M)
            G.EntityList.append(M)
            G.MouldList.append(M)
            #initialize the component
            M.initialize()
        except:
            # added for testing
            print 'the mould to be created', component.get('name', 'not found'), 'cannot be created', 'time', now()
        
    # =======================================================================
    # check if the assemble can accept an entity
    # returns true if it is empty 
    # =======================================================================   
    def canAccept(self, callerObject=None): 
        activeObject=self.getActiveObject()
        activeObjectQueue=activeObject.getActiveObjectQueue()
        thecaller=callerObject
        if thecaller!=None:
            #check it the caller object holds an Entity that requests for current object
            if len(thecaller.getActiveObjectQueue())>0:
                # TODO: make sure that the first entity of the callerObject is to be disposed
                activeEntity=thecaller.getActiveObjectQueue()[0]
                # if the machine's Id is in the list of the entity's next stations 
                if activeObject.id in activeEntity.remainingRoute[0].get('stationIdsList',[]):
                    #return according to the state of the Queue
                    # check if (if the machine is to be operated) there are available operators
                    if (activeObject.operatorPool!='None' and any(type=='Load' or 'Setup' for type in activeObject.multOperationTypeList)):
                        return activeObject.operatorPool.checkIfResourceIsAvailable()\
                                 and len(activeObject.getActiveObjectQueue())==0\
                                 and activeObject.Up
                    else:
                        return len(activeObject.getActiveObjectQueue())==0\
                                 and activeObject.Up
        return False
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some predecessor waiting for it and updates the giver to the one that is to be taken
    # The internal queue of the assembler must be empty 
    # and the parent order of the entities to be received must have 
    # the flag componentsReadyForAssembly set to True 
    # =======================================================================    
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        # if we have only one predecessor just check if the machine is empty, 
        # the machine is up and the predecessor has an entity to dispose
        if(len(activeObject.previous)==1):
            # if the machine has to compete for an Operator that loads the entities onto it
            #     check if the predecessor if blocked by an other Machine 
            # if not then the machine has to block the predecessor giverObject to avoid conflicts
            #     with other competing machines
            if (activeObject.operatorPool!='None' and any(type=='Load' for type in activeObject.multOperationTypeList)):
                if activeObject.operatorPool.checkIfResourceIsAvailable()\
                    and activeObject.Up\
                    and len(activeObjectQueue)==0\
                    and giverObject.haveToDispose(activeObject)\
                    and not giverObject.exitIsAssigned():
                    activeObject.giver.assignExit()
                    return True
                else:
                    return False
            # otherwise, use the default behaviour
            else:
                return activeObject.Up and len(activeObjectQueue)==0\
                        and giverObject.haveToDispose(activeObject)                
        # dummy variables that help prioritise the objects requesting to give objects to the Machine (activeObject)
        isRequested=False   # isRequested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0    # dummy variable counting the time a predecessor is blocked
        
        # loop through the possible givers to see which have to dispose and which is the one blocked for longer
        for object in activeObject.previous:
            # if the predecessor objects have entities to dispose of
            if(object.haveToDispose(activeObject) and object.receiver==self):
                isRequested=True
                # and if the predecessor has been down while trying to give away the Entity
                if(object.downTimeInTryingToReleaseCurrentEntity>0):
                # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                    timeWaiting=now()-object.timeLastFailureEnded
                # in any other case, it holds the time since the end of the Entity processing
                else:
                    timeWaiting=now()-object.timeLastEntityEnded
                #if more than one predecessor have to dispose, take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting):
                    activeObject.giver=object
                    maxTimeWaiting=timeWaiting
        if (activeObject.operatorPool!='None' and any(type=='Load' for type in activeObject.multOperationTypeList)):
            if activeObject.operatorPool.checkIfResourceIsAvailable()\
                and activeObject.Up\
                and len(activeObjectQueue)==0\
                and isRequested\
                and not activeObject.giver.exitIsAssigned():
                activeObject.giver.assignExit()
                return True
            else:
                return False
        else:
            return activeObject.Up and len(activeObjectQueue)==0 and isRequested
