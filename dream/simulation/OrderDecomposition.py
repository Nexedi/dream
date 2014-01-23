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

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import waituntil, now, hold, infinity

from Globals import G
from CoreObject import CoreObject
from RandomNumberGenerator import RandomNumberGenerator
from Entity import Entity

from Order import Order
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
    def __init__(self, id, name):
        CoreObject.__init__(self)
        self.id=id
        self.objName=name
        self.type='OrderDecomposition'
        
    # =======================================================================
    # the initialize method
    # =======================================================================
    def initialize(self):
        self.previous=G.ObjList
        self.next=G.ObjList
        CoreObject.initialize(self)                 # using the default CoreObject Functionality
        self.Res=Resource(infinity)                 # initialize the Internal resource (Queue) functionality. This is a dummy object so 
                                                    # infinite capacity is assumed
        self.newlyCreatedComponents=[]              # a list to hold components just after decomposition
        self.orderToBeDecomposed=None
    
    # =======================================================================
    # run just waits until there is something to get and gets it
    # =======================================================================
    def run(self):
        while 1:  
            yield waituntil, self, self.canAcceptAndIsRequested     #wait until the Queue can accept an entity
                                                                    #and one predecessor requests it                                                  
            self.getEntity()  
            self.decompose()                     
        
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
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        # if we have only one possible giver just check if there is a place, 
        # the machine is up and the predecessor has an entity to dispose
        # this is done to achieve better (cpu) processing time
        if(len(activeObject.previous)==1):
            return activeObject.Up and giverObject.haveToDispose(activeObject) 
        
        # dummy variables that help prioritize the objects requesting to give objects to the Machine (activeObject)
        isRequested=False                                           # is requested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked

        # loop through the possible givers to see which have to dispose and which is the one blocked for longer
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject) and object.receiver==self):
                isRequested=True                                    # if the predecessor objects have entities to dispose of
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the predecessor has been down while trying to give away the Entity
                    timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                else:
                    timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.giver=object                 # the object to deliver the Entity to the activeObject is set to the ith member of the previous list
                    maxTimeWaiting=timeWaiting    
                                                 # in the next loops, check the other predecessors in the previous list

        return activeObject.Up and isRequested    

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
        # find the suitable receiver
        
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(len(activeObject.next)==1 or callerObject==None):
            activeObject.receiver=activeObject.next[0]
            return len(activeObjectQueue)>0\
                    and thecaller==activeObject.receiver
        
        #give the entity to the possible receiver that is waiting for the most time. 
        #plant does not do this in every occasion!       
        maxTimeWaiting=0     
                                                        # loop through the object in the successor list
        for object in activeObject.next:
            if(object.canAccept()):                                 # if the object can accept
                timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                    maxTimeWaiting=timeWaiting
                    self.receiver=object                           # and update the receiver to the index of this object
        
#         self.receiver=Globals.findObjectById(activeEntity.remainingRoute[0][0])    #read the next station 
        #return True if the OrderDecomposition in the state of disposing and the caller is the receiver
        return self.Up and (callerObject is self.receiver) 
    
    # =======================================================================
    # decomposes the order to its components
    # =======================================================================
    def decompose(self):
        activeObjectQueue=self.getActiveObjectQueue()
        #loop in the internal Queue. Decompose only if an Entity is of type order
        for entity in activeObjectQueue:
            if entity.type=='Order':
                self.orderToBeDecomposed=entity
                activeObjectQueue.remove(entity)            #remove the order from the internal Queue
                #append the components in the internal queue
                for component in entity.componentsList:
                    self.createOrderComponent(component)
                # after the creation of the order's components update each components auxiliary list
                # if there are auxiliary components
                if len(entity.auxiliaryComponentsList):
                    # for every auxiliary component
                    for auxComponent in entity.auxiliaryComponentsList:
                        # run through the componentsList of the order
                        for reqComponent in entity.componentsList:
                            # to find the requestingComponent of the auxiliary component
                            if auxComponent.requestingComponent==reqComponent.id:
                                # and add the auxiliary to the requestingComponent auxiliaryList
                                reqComponent.auxiliaryList.append(auxComponent)
        #if there is an order for decomposition
        if self.orderToBeDecomposed:
            import Globals
            Globals.setWIP(self.newlyCreatedComponents)     #set the new components as wip
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
            # is of type Mould and therefore has no argument componentType
            # in this case no Mould object should be initiated
            if component.get('_class', 'not found')=='Dream.Mould':
                raise MouldComponentException('there is a mould in the componentList')
            # variable that holds the componentType which can be Basic/Secondary/Auxiliary
            componentType=component.get('componentType', 'Basic') 
            # the component that needs the auxiliary (if the componentType is "Auxiliary") during its processing
            requestingComponent = component.get('requestingComponent', 'not found') 
            # dummy variable that holds the routes of the jobs the route from the JSON file is a sequence of dictionaries
            JSONRoute=component.get('route', [])
            # variable that holds the argument used in the Job initiation hold None for each entry in the 'route' list
            route = [None for i in range(len(JSONRoute))]         
                    
            for routeentity in JSONRoute:                                          # for each 'step' dictionary in the JSONRoute
                stepNumber=int(routeentity.get('stepNumber', '0'))                 #    get the stepNumber
                route[stepNumber]=routeentity
                    
            # keep a reference of all extra properties passed to the job
            extraPropertyDict = {}
            for key, value in component.items():
                if key not in ('_class', 'id'):
                    extraPropertyDict[key] = value
    
            #Below it is to assign an exit if it was not assigned in JSON
            #have to talk about it with NEX
            exitAssigned=False
            for element in route:
    #             elementId=element[0]
                elementIds = element.get('stationIdsList',[])
                for obj in G.ObjList:
                    for elementId in elementIds:
                        if obj.id==elementId and obj.type=='Exit':
                            exitAssigned=True 
            if not exitAssigned:
                exitId=None
                for obj in G.ObjList:
                    if obj.type=='Exit':
                        exitId=obj.id
                        break
                if exitId:
    #                 route.append([exitId, 0])
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
            if OC.componentType == 'Basic':
                self.orderToBeDecomposed.basicComponentsList.append(OC)
            elif OC.componentType == 'Secondary':
                self.orderToBeDecomposed.secondaryComponentsList.append(OC)
            else:
                self.orderToBeDecomposed.auxiliaryComponentsList.append(OC)
                    
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
            