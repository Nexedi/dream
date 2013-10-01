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
Created on 01 Oct 2013

@author: George
'''
'''
Job is an Entity that implements the logic of a job shop. Job carries attributes for its route 
in the system and also in the processing times at each station
'''

from Globals import G
from Entity import Entity

#The part object
class Job(Entity):    
    type="Job"
    
    def __init__(self, name, id, route):
        Entity.__init__(self, name)
        self.id=id
        self.fullRoute=route    #the route that the job follows, also contains the processing times in each station
        self.remainingRoute=route   #the remaining route. in the beginning this should be the same as the full route
        self.currentStop=route[0][0]    #the starting stop should be the first in the route

        
        
        
        
        
    
    