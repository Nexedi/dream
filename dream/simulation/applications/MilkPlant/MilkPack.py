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
Created on 09 11 2015

@author: George
'''
'''
models a pack of milk
'''

from dream.simulation.Job import Job

class MilkPack(Job):  
    type='Job'
    family='Job'
    
    def __init__(self, id=None, name=None, route=[], currentStation=None,liters=1,fat=1,productId=None,**kw):
        Job.__init__(self,id=id,name=name,route=route,currentStation=currentStation)
        self.liters=liters
        self.fat=fat
        self.productId=productId
        