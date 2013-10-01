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
Created on 18 Feb 2013

@author: George
'''

'''
models a frame entity. This can flow through the system and carry parts
'''

from SimPy.Simulation import Resource
from Globals import G
from Entity import Entity

#The entity object
class Frame(Entity):    
    type="Frame"
    numOfParts=4    #the number of parts that the frame can take
          
    def __init__(self, name):
        Entity.__init__(self, name)

        self.Res=Resource(self.numOfParts)
        #dimension data
        self.width=2.0
        self.height=2.0
        self.lenght=2.0        
        

