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
Created on 15 Jan 2014

@author: Ioannis
'''
'''
Inherits from QueuePreemptive. Checks the condition of (a) component(s) before in can dispose of them/it
'''

from QueuePreemptive import QueuePreemptive
from SimPy.Simulation import now

# ===========================================================================
# the QueuePreemptive object
# ===========================================================================
class ConditionalBuffer(QueuePreemptive):
    # ===========================================================================
    # the __init__ function
    # ===========================================================================
    def __init__(self, id, name, capacity=1, dummy=False, schedulingRule="CB"):
        # run the default method, change the schedulingRule to CB 
        # for description, check activeQSorter function of Queue coreObject 
        QueuePreemptive.__init__(self, id, name, capacity, dummy, schedulingRule)
                    
    # =======================================================================
    # checks if the Buffer can dispose an entity. 
    # Returns True only to the potential receiver
    # If it holds secondary components, checks first if the basicsEnded is
    # True first. Otherwise, it waits until the basics are ended.
    # =======================================================================     
    def haveToDispose(self, callerObject=None):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        thecaller = callerObject
        
        # if the type of the component is Secondary then assert that the basics of the same order
        # are already processed before disposing them to the next object
        activeEntity = activeObjectQueue[0]
        if activeEntity.componentType=='Secondary':
            if not activeEntity.order.basicsEnded:
                return False
        
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
            if(object.canAccept(activeObject)):                                 # if the object can accept
                timeWaiting=now()-object.timeLastEntityLeft         # compare the time that it has been waiting 
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# with the others'
                    maxTimeWaiting=timeWaiting
                    self.receiver=object                           # and update the receiver to the index of this object
        
        #return True if the Queue has Entities and the caller is the receiver
        return len(activeObjectQueue)>0 and (thecaller is self.receiver) 
        
    
    
    