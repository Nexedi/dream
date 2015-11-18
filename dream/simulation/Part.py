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
Created on 6 Feb 2013

@author: George
'''

'''
models a part entity that flows through the system
'''


from Globals import G
from Entity import Entity

#The part object
class Part(Entity):
    type="Part"
    def __init__(self, id=None, name=None, remainingProcessingTime=0,currentStation=None,**kw):
        Entity.__init__(self, id, name, remainingProcessingTime=remainingProcessingTime,currentStation=currentStation) 
        

