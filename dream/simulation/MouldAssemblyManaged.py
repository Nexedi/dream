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
inherits from MachineManagedJob. It takes the components of an order and reassembles them as mould
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
            "stationIdsList": [
                "MA1"
            ],                                                                # the mould assembly stations
            "processingTime": {
                "distributionType": "Fixed",
                "mean": "3"
            }
        },
        {
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
from MachineManagedJob import MachineManagedJob
# from SimPy.Simulation import Resource, reactivate, now
import simpy
from Globals import G

# =======================================================================
# Error in the assembling of the mould
# =======================================================================
class AssembleMouldError(Exception):
    def __init__(self, mouldAssembleError):
        Exception.__init__(self, mouldAssembleError) 

# ===========================================================================
# the MachineManagedJob object
# ===========================================================================
class MouldAssemblyManaged(MachineManagedJob):

    # =======================================================================
    # the initialize method
    # =======================================================================
    def initialize(self):
        self.mouldParent = None                 # the mould's to be assembled parent order
        self.mouldToBeCreated = None            # the mould to be assembled
        MachineManagedJob.initialize(self)      # run default behaviour
        
    # =======================================================================
    # getEntity method that gets the entity from the giver
    # it should run in a loop till it get's all the entities from the same order
    # (with the flag componentsReadyForAssembly set)
    # it is run only once, and receives all the entities to be assembled inside a while loop
    # =======================================================================
    def getEntity(self):
        activeObject = self.getActiveObject()
        giverObject = activeObject.getGiverObject()
        # get the first entity from the predecessor
        # TODO: each MachineManagedJob.getEntity is invoked, 
        #     the self.procTime is updated. Have to decide where to assign 
        #     the processing time of the assembler
        activeEntity=MachineManagedJob.getEntity(self)
        # this is kept so that in the next loop it will not try to re-get this Entity
        firstObtained=activeEntity  
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
        # loop through the basic/secondary components of the order that is currently obtained
        # all the components are received at the same time
        for entity in activeEntity.order.basicComponentsList\
                       +activeEntity.order.secondaryComponentsList:
            # continue for the one that is already  obtained before
            if entity is firstObtained:
                continue

            self.entityToGet=entity
            # get the next component
            activeEntity=MachineManagedJob.getEntity(self)
            # check whether the activeEntity is of type Mould
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
        self.Res=simpy.Resource(self.env, self.capacity)
    
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
        temp_activeObjectQueue=list(activeObjectQueue)
        for element in temp_activeObjectQueue:
            # update their schedule
            element.schedule[-1]["exitTime"] = self.env.now
            # remove the elements
            activeObjectQueue.remove(element)
        del temp_activeObjectQueue[:]
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
            route = [x for x in JSONRoute]       #    copy JSONRoute
            # assert that the assembler is in the moulds route and update the initial step of the mould's route
            firstStep = route.pop(0)
            assert (self.id in firstStep.get('stationIdsList',[])),\
                         'the assembler must be in the mould-to-be-created route\' initial step'
            processingTime=firstStep['processingTime']  
            # update the activeObject's processing time according to the readings in the mould's route
            self.distType=processingTime.keys()[0]
            self.procTime=float(processingTime[self.distType].get('mean', 0))
            # update the first step of the route with the activeObjects id as sole element of the stationIdsList
            route.insert(0, {'stationIdsList':[str(self.id)],'processingTime':{str(self.distType):{'mean':str(self.procTime)}}})
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
            print 'the mould to be created', component.get('name', 'not found'), 'cannot be created', 'time', self.env.now
            raise
        