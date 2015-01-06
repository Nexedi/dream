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
Created on 5 June 2013

@author: George
'''
'''
entity that requires specific capacity from a station
'''

from dream.simulation.Entity import Entity

# ===========================================================================
# The CapacityEntity object 
# ===========================================================================
class CapacityEntity(Entity):
    type="CapacityEntity"
    
    def __init__(self, id=None, name=None, capacityProjectId=None, requiredCapacity=10, priority=0, dueDate=0,
                  orderDate=0, currentStation=None, isCritical=False, **kw):
        Entity.__init__(self, id, name, priority, dueDate, orderDate, isCritical, currentStation=currentStation)
        self.capacityProjectId=capacityProjectId    # the project id hat the capacity Entity is part of
        self.capacityProject=None                   # the project that the capacity Entity is part of. It is defined in initialize
        self.requiredCapacity=requiredCapacity  # the capacity that the capacity entity requires from the following station
        self.shouldMove=False
        from dream.simulation.Globals import G
        if hasattr(G, 'CapacityEntityList'):
            G.CapacityEntityList.append(self)
        else:
            G.CapacityEntityList=[]
            G.CapacityEntityList.append(self)

    def initialize(self):
        Entity.initialize(self)
        self.shouldMove=False
        from dream.simulation.Globals import G
        # find the project that the capacity entity is part of
        for project in G.CapacityProjectList:
            if project.id==self.capacityProjectId:
                self.capacityProject=project
                break
        