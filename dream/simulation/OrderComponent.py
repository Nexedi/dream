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

# ============================ The OrderComponent object ==============================
class OrderComponent(Job):                                  # inherits from the Job class   
    type="OrderComponent"
    
    def __init__(self, id=None, name=None, route=[], priority=0, dueDate=None, orderDate=None, extraPropertyDict=None,
                    componentType='Basic', order=None, isCritical=False):
        Job.__init__(self, id=None, name=None, route=[], priority=0, dueDate=None, orderDate=None, extraPropertyDict=None)
        self.auxiliaryList=[]
        self.order=order
        self.isCritical=isCritical  #this should be self.order.isCritical. Added now for testing
