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
Created on 15 Feb 2013

@author: George
'''

'''
Models a LIFO queue where entities can wait in order to get into a server
'''


from Queue import Queue

class QueueLIFO(Queue):
       
    #gets an entity from the predecessor     
    def getEntity(self):
        activeObject=self       #use this to refer to the current object which receives the Entity
        activeEntity=[self.previous[self.predecessorIndex].Res.activeQ[0]]       #use this to refer to the Entity that is received       
        giverObject=self.previous[self.predecessorIndex]        #use this to refer to the object that disposes the entity              
                      
        activeObject.Res.activeQ=activeEntity+activeObject.Res.activeQ   #get the entity from the previous object
                                                                         #and put it in front of the activeQ       
        giverObject.removeEntity()     #remove the entity from the previous object   
        
         