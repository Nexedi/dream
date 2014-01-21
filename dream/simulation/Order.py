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
                        extraPropertyDict=None):
        Job. __init__(self, id=id, name=name, route=route, priority=priority, dueDate=dueDate, orderDate=orderDate, 
                      extraPropertyDict=extraPropertyDict)
        self.isCritical=isCritical          # flag to inform weather the order is critical -> preemption
        self.componentsList=componentsList  # list of components that the order will be broken into
        self.basicComponentsList = []      # list that holds the Basic Components of the order
        self.secondaryComponentsList = []   # list that holds the Secondary Components of the order
        self.auxiliaryComponentsList = []   # list of the auxiliary components of the order 
        self.manager=manager                # the manager responsible to handle the order 
        self.basicsEnded=basicsEnded        # flag that informs that the basic components of the order are finished
        # flag that informs weather the components needed for the assembly are present in the Assembly Buffer
        self.componentsReadyForAssembly = componentsReadyForAssembly



