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
Created on 20 Dec 2013

@author: George
'''
'''
OrderComponent is an Entity that is a component of a broader order
'''

from Globals import G
from Job import Job

# ===========================================================================
# The OrderComponent object
# ===========================================================================
class OrderComponent(Job):                                  # inherits from the Job class   
    type="OrderComponent"
    
    def __init__(self, id=None, name=None, 
                    route=[], 
                    priority=0, 
                    dueDate=0, 
                    orderDate=0, 
                    extraPropertyDict=None,
                    componentType='Basic', 
                    order=None, 
                    requestingComponent = None, 
                    readyForAssembly = 0, 
                    isCritical=False,
                    remainingProcessingTime={}, 
                    remainingSetupTime={},
                    currentStation=None,
                    **kw):
        Job.__init__(self, id, name, route=route, priority=priority, dueDate=dueDate, 
                     orderDate=orderDate, extraPropertyDict=extraPropertyDict, isCritical=isCritical,
                     remainingProcessingTime=remainingProcessingTime, remainingSetupTime=remainingSetupTime,
                     currentStation=currentStation)
        #=======================================================================
        self.auxiliaryList=[]       # Holds the auxiliary components that the component needs for a certain processing
        #=======================================================================
        self.order=order            # parent order of the order component
        # TODO: in case the order is not given as argument (when the component is given as WIP) have to give a manager as argument
        #     or create the initiate the parent order not as WIP 
        if self.order:
            # if the order is not None, and the order.manager is given
            if self.order.manager:
                self.manager=self.order.manager
        self.componentType = componentType  # the type of the component which can be Basic/Secondary/Auxiliary
        #=======================================================================
        # if the componentType of the component is Auxiliary then there need a requesting Component be defined
        # the requestingComponent is the component that needs the auxiliary component during its processing
        # the auxiliary component should then be added to the requestingComponent's auxiliaryList
        self.requestingComponent = requestingComponent  # the id of the requesting component
        #=======================================================================
        self.readyForAssembly = readyForAssembly        # flag informing weather the component was received
                                                        #     by the MouldAssembleBuffer
        # used by printRoute
        if self.order:
            self.alias=self.order.alias+'C'+str(len(G.OrderComponentList))
        
        G.OrderComponentList.append(self)
        G.WipList.append(self)
