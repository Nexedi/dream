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
Created on 8 Nov 2012

@author: George
'''
'''
Models an intro element that is never starved. 
In removeEntity, each time it falls below a specific level it creates new Entities
'''

import simpy
from Queue import Queue
# ===========================================================================
#                            the Queue object
# ===========================================================================
class NonStarvingEntry(Queue):
    family='Entry'
    def __init__(self, id, name, capacity=float('inf'), entityData={'_class':'Dream.Part'}, threshold=2, 
                 initialWIPLevel=2,**kw):
        Queue.__init__(self, id=id,name=name, capacity=capacity)
        self.threshold=int(threshold)
        self.initialWIPLevel=int(initialWIPLevel)
        self.entityData=dict(entityData)

    def initialize(self):
        Queue.initialize(self)
        from Globals import G
        import Globals
        for i in range(self.initialWIPLevel):
            self.createEntity()

    def removeEntity(self, entity=None):
        activeEntity=Queue.removeEntity(self, entity)                  #run the default method
        activeObjectQueue=self.getActiveObjectQueue()
        entityType=self.entityData.get('_class', None)
        if len(activeObjectQueue)<self.threshold:
            self.createEntity()
        return activeEntity
    
    def createEntity(self):
        from Globals import G
        import Globals
        entityType=self.entityData.get('_class', None)
        assert entityType, 'the entity type of the non starving buffer could not be identified'
        entityType=Globals.getClassFromName(entityType)
        Eargs={'id':G.numberOfEntities,
               'name':str(entityType)+str(G.numberOfEntities),
               'currentStation':self
               }
        E=entityType(**Eargs)
        Globals.setWIP([E])
        G.numberOfEntities+=1
        if not self.canDispose.triggered:
            self.canDispose.succeed(self.env.now)
    