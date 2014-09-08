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
Created on 08 Sep 2014

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All ManPy objects inherit from it
Also only abstract ManPy classes inherit directly (CoreObject, Entity, ObjectResource, ObjectInterruption)
'''

# ===========================================================================
# the ManPy object
# ===========================================================================
class ManPyObject(object):
    
    def __init__(self, id, name,**kw):
        self.id=id
        self.name=name
