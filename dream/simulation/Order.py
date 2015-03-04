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
Order is an Entity that can have its design, get broken to sub-components
'''

from Globals import G
from Job import Job

# =======================================================================
# The Order object 
# =======================================================================
class Order(Job):
    type="Order"
    # XX define which are the valid assembly types - for which components should the order be searching for 
    assemblyValidTypes=set(['Mold Base', 'Mold Insert', 'Slider', 'Misc', 'Electrode','Z-Standards', 'K-Standards'])
    assemblyInvalidTypes=set(['Mold','Injection Molding Part'])
    def __init__(self, id=None, 
                        name=None, 
                        route=[], 
                        priority=0, 
                        dueDate=None, 
                        orderDate=None, 
                        isCritical=False,
                        componentsList=[], 
                        manager=None, 
                        basicsEnded=0, 
                        componentsReadyForAssembly=0, 
                        extraPropertyDict=None,
                        **kw):
        Job. __init__(self, id=id, name=name, route=route, priority=priority, dueDate=dueDate, orderDate=orderDate, 
                      isCritical=isCritical, extraPropertyDict=extraPropertyDict)
        self.componentsList=componentsList  # list of components that the order will be broken into
        self.components=[]                  # list of all the child components of the order 
        self.assemblyComponents=[]          # list of the required components to build the mould
        self.assemblyRequested=False        # flag used to check whether a mould is created out of other orderComponents
        #=======================================================================
        self.basicComponentsList = []       # list that holds the Basic Components of the order
        self.secondaryComponentsList = []   # list that holds the Secondary Components of the order
        self.auxiliaryComponentsList = []   # list of the auxiliary components of the order 
        self.basicsEnded=basicsEnded        # flag that informs that the basic components of the order are finished
        self.manager=manager                # the manager responsible to handle the order
        #======================================================================= 
        # flag that informs weather the components needed for the assembly are present in the Assembly Buffer
        self.componentsReadyForAssembly = componentsReadyForAssembly
        
#         self.decomposed=False
        # used by printRoute
        self.alias='O'+str(len(G.OrderList))
        def createRoute(self, route):
            return route
    
    #===========================================================================
    # find all the active child components of the order 
    # returns only the components that are present in the system 
    #===========================================================================
    def findActiveComponents(self):
        from Globals import findObjectById
        for componentDict in self.componentsList:
            componentId=componentDict.get('id',0)
            componentClass=componentDict.get('_class','not found')
            # if there is mould defined in the componentsList and the mould is not yet created, then assembly is requested
            if componentClass=='Dream.Mould':
                if not componentId in [x.id for x in G.EntityList]:
                    self.assemblyRequested=True
            # if the component is not yet created then there is no entity to find. 
            component=findObjectById(componentId)
            if component:
                # if the component is not in the components list and has a currentStation add it
                if not component in self.components and component.currentStation:
                    self.components.append(component)
                # if the component is in the components list and has no currentStation remove it
                if component in self.components and not component.currentStation:
                    self.components.remove(component)
    
    #===========================================================================
    # return the all the active child components of the order
    #===========================================================================
    def getActiveComponents(self):
        self.findActiveComponents()
        return self.components
    
    #===========================================================================
    # find all the child components of the order that are required for the building of the mould
    #===========================================================================
    def findAssemblyComponents(self):
        for child in self.getActiveComponents():
            if getattr(child, 'componentType', None) in self.assemblyValidTypes:
                if not child in self.assemblyComponents:
                    self.assemblyComponents.append(child)
    
    #===========================================================================
    # get the components that are required for the construction of the mould
    #===========================================================================
    def getAssemblyComponents(self):
        if not self.assemblyComponents:
            self.findAssemblyComponents()
        return self.assemblyComponents
        
    