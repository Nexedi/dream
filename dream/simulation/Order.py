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
from Entity import Entity

# ============================ The Order object ==============================
class Order(Entity):
    type="Order"
    
    def __init__(self, id=None, name=None, priority=0, dueDate=None, orderDate=None, isCritical=False,
                 componentsList=[], designTime=0, manager=None, basicsEnded=False):
        Entity. __init__(self, id=id, name=name, priority=priority, dueDate=dueDate, orderDate=orderDate)
        self.isCritical=isCritical
        self.componentsList=componentsList
        self.designTime=designTime
        self.manager=manager
        self.basicsEnded=basicsEnded



