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
Created on 06 Jan 2013

@author: George
'''
'''
OrderDecomposition is a Core Object that takes an order after design and decomposes to order components
dummy object: infinite capacity no processing time
'''

# from SimPy.Simulation import Process, Resource
# from SimPy.Simulation import waituntil, now, hold, infinity, waitevent
import simpy

from Globals import G
from CoreObject import CoreObject
from RandomNumberGenerator import RandomNumberGenerator
from Entity import Entity

from Order import Order
from OrderDesign import OrderDesign
from OrderComponent import OrderComponent

# ===========================================================================
# Error in the setting up of the WIP
# ===========================================================================
class MouldComponentException(Exception):
    def __init__(self, mouldException):
        Exception.__init__(self, mouldException) 

# ===========================================================================
# the Order-Decomposition Object
# ===========================================================================
class OrderDecomposition(CoreObject):
    type = 'OrderDecomposition'

    # =======================================================================
    # the initialize method
    # =======================================================================
    def initialize(self):
        self.previous=G.ObjList
        self.next=[]
        CoreObject.initialize(self)                 # using the default CoreObject Functionality
        self.Res=simpy.Resource(self.env, 'inf')    # initialize the Internal resource (Queue) functionality. This is a dummy object so 
                                                    # infinite capacity is assumed
        self.newlyCreatedComponents=[]              # a list to hold components just after decomposition
        self.orderToBeDecomposed=None
    
    # =======================================================================
    # run just waits until there is something to get and gets it
    # =======================================================================
    def run(self):
        # check if there is WIP and signal receiver
        self.initialSignalReceiver()
        while 1:  
            #wait until the Queue can accept an entity and one predecessor requests it
            
            self.expectedSignals['isRequested']=1
            self.expectedSignals['canDispose']=1
            
            receivedEvent=yield self.env.any_of([self.isRequested , self.canDispose])
            # if the event that activated the thread is isRequested then getEntity
            if self.isRequested in receivedEvent:
                transmitter, eventTime=self.isRequested.value
                self.isRequested=self.env.event()
                # reset the isRequested signal parameter
                self.isRequested.signalparam=None
                self.getEntity()
                self.decompose()
            if self.canDispose in receivedEvent:
                transmitter, eventTime=self.canDispose.value
                self.canDispose=self.env.event()
            
            # if the event that activated the thread is canDispose then signalReceiver
            if self.haveToDispose():
#                 print now(), self.id, 'will try to signal a receiver from generator'
                self.signalReceiver()
                
    # =======================================================================
    #                    removes an entity from the Object
    # =======================================================================
    def removeEntity(self, entity=None):
        activeObject=self.getActiveObject()                                  
        activeEntity=CoreObject.removeEntity(self, entity)                  #run the default method
        if self.canAccept():
            self.signalGiver()
        if self.haveToDispose():
#             print now(), self.id, 'will try to signal a receiver from removeEntity'
            self.signalReceiver()
        return activeEntity
        
    # =======================================================================
    # as a dummy object can always accept 
    # =======================================================================
    def canAccept(self, callerObject=None):
        return True
    
    # =======================================================================
    # checks if the OrderDecomposition can accept an entity 
    # and there is an entity in some possible giver waiting for it
    # also updates the giver to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self,callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
#         giverObject=self.getGiverObject()
        giverObject=callerObject
        assert giverObject, 'there must be a caller for canAcceptAndIsRequested'
        # if we have only one possible giver just check if there is a place, 
        # the machine is up and the predecessor has an entity to dispose
        # this is done to achieve better (cpu) processing time
        return activeObject.Up and giverObject.haveToDispose(activeObject) 

    # ======================================================================= 
    # checks if the OrderDecomposition can dispose 
    # an entity to the following object
    # =======================================================================
    def haveToDispose(self, callerObject=None):
        activeObject = self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller = callerObject
        #if there is no Entity return False
        if len(activeObjectQueue)==0:
            return False

        activeEntity=activeObjectQueue[0]
        import Globals
        # update the next list of the object
        nextObjectIds=activeEntity.remainingRoute[0].get('stationIdsList',[])
        nextObjects = []
        for nextObjectId in nextObjectIds:
            nextObject = Globals.findObjectById(nextObjectId)
            nextObjects.append(nextObject)
        self.next=nextObjects
        
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(callerObject==None):
            return True
        
        #return True if the OrderDecomposition in the state of disposing and the caller is the receiver
        return self.Up and thecaller.isInRouteOf(activeObject)
    
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
    
    # =======================================================================
    # decomposes the order to its components
    # =======================================================================
    def decompose(self):
        activeObjectQueue=self.getActiveObjectQueue()
        #loop in the internal Queue. Decompose only if an Entity is of type order
        # XXX now instead of Order we have OrderDesign
        for entity in activeObjectQueue:
            if entity.type=='OrderDesign':
                self.orderToBeDecomposed=entity.order
                activeObjectQueue.remove(entity)            #remove the order from the internal Queue
                entity.currentStation=None                  # reset the currentStation of the entity
                self.printTrace(entity.id, destroy=self.id)
                # if the entity is in G.pendingEntities list remove it from there
                if entity in G.pendingEntities:
                    G.pendingEntities.remove(entity)
                #append the components in the internal queue
                for component in entity.order.componentsList:
                    self.createOrderComponent(component)
                # after the creation of the order's components update each components auxiliary list
                # if there are auxiliary components
                if len(entity.order.auxiliaryComponentsList):
                    # for every auxiliary component
                    for auxComponent in entity.order.auxiliaryComponentsList:
                        # run through the componentsList of the order
                        for reqComponent in entity.order.componentsList:
                            # to find the requestingComponent of the auxiliary component
                            if auxComponent.requestingComponent==reqComponent.id:
                                # and add the auxiliary to the requestingComponent auxiliaryList
                                reqComponent.auxiliaryList.append(auxComponent)
        #if there is an order for decomposition
        if self.orderToBeDecomposed:
            import Globals
            Globals.setWIP(self.newlyCreatedComponents)     #set the new components as wip
            # TODO: consider signalling the receivers if any WIP is set now
            #reset attributes
            self.orderToBeDecomposed=None
            self.newlyCreatedComponents=[]
    
    # =======================================================================
    # creates the components
    # =======================================================================
    def createOrderComponent(self, component):
        #read attributes from the json or from the orderToBeDecomposed
        id=component.get('id', 'not found')
        name=component.get('name', 'not found')
        try:
            # there is the case were the component of the componentsList of the parent Order
            # is of type Mould or OrderDesign and therefore has no argument componentType
            # in this case no Mould or OrderDesign object should be initiated
            if component.get('_class', 'not found')=='Dream.Mould' or component.get('_class', 'not found')=='Dream.OrderDesign':
                raise MouldComponentException('there is a mould/orderDesign in the componentList')
            # variable that holds the componentType which can be Basic/Secondary/Auxiliary
            componentType=component.get('componentType', 'Basic') 
            # the component that needs the auxiliary (if the componentType is "Auxiliary") during its processing
            requestingComponent = component.get('requestingComponent', 'not found')
            # dummy variable that holds the routes of the jobs the route from the JSON file is a sequence of dictionaries
            JSONRoute=component.get('route', [])
            # variable that holds the argument used in the Job initiation hold None for each entry in the 'route' list
            route = [x for x in JSONRoute]
                    
            # keep a reference of all extra properties passed to the job
            extraPropertyDict = {}
            for key, value in component.items():
                if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value
    
            #Below it is to assign an exit if it was not assigned in JSON
            #have to talk about it with NEX
            exitAssigned=False
            for element in route:
                elementIds = element.get('stationIdsList',[])
                for obj in G.ObjList:
                    for elementId in elementIds:
                        type=obj.__class__.__name__
                        if obj.id==elementId and (obj.type=='Exit' or type=='MouldAssemblyManaged' or type=='MouldAssemblyBufferManaged'):
                            exitAssigned=True
            # Below it is to assign assemblers if there are any in the corresponding Global list
            if not exitAssigned:                    
                if len(G.MouldAssemblyList)!=0:
                    bufferIDlist = []
                    assemblerIDlist = []
                    for assemblyBuffer in G.MouldAssemblyBufferList:
                        bufferIDlist.append(str(assemblyBuffer.id))
                    for assembler in G.MouldAssemblyList:
                        assemblerIDlist.append(str(assembler.id))
                    route.append({'stationIdsList':bufferIDlist})       # assign MouldAssemblyBuffers
                    route.append({'stationIdsList':assemblerIDlist})    # assign MouldAssemblies
                    # if assemblers are assigned then an 'exit' is assigned
                    exitAssigned=True
            if not exitAssigned:
                exitId=None
                for obj in G.ObjList:
                    if obj.type=='Exit':
                        exitId=obj.id
                        break
                if exitId:
                    route.append({'stationIdsList':[str(exitId)],\
                                  'processingTime':{}})
            
            # initiate the OrderComponent
            OC=OrderComponent(id, name, route, \
                              priority=self.orderToBeDecomposed.priority, \
                              dueDate=self.orderToBeDecomposed.dueDate, \
                              componentType=componentType,\
                              requestingComponent = requestingComponent, \
                              order=self.orderToBeDecomposed,\
                              orderDate=self.orderToBeDecomposed.orderDate, \
                              extraPropertyDict=extraPropertyDict,\
                              isCritical=self.orderToBeDecomposed.isCritical)
            
            # check the componentType of the component and accordingly add to the corresponding list of the parent order
            #===============================================================================
            if OC.componentType == 'Basic':
                self.orderToBeDecomposed.basicComponentsList.append(OC)
            elif OC.componentType == 'Secondary':
                self.orderToBeDecomposed.secondaryComponentsList.append(OC)
#             else:
#                 self.orderToBeDecomposed.auxiliaryComponentsList.append(OC)
            #===============================================================================
            G.OrderComponentList.append(OC)
            G.JobList.append(OC)   
            G.WipList.append(OC)  
            G.EntityList.append(OC)
            self.newlyCreatedComponents.append(OC)              #keep these to pass them to setWIP
            OC.initialize()                                     #initialize the component
        except MouldComponentException as mouldException:
            pass
#             # added for testing
#             print 'Mould component exception: {0}'.format(mouldException)
#             print 'the component of the order', self.orderToBeDecomposed.name, 'is of type Mould \
#             and thus nothing is created', 'time', now()
            
