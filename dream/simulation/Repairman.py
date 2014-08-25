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
Created on 14 Nov 2012

@author: George
'''

'''
models a repairman that can fix a machine when it gets failures
'''

# from SimPy.Simulation import Resource, now
import simpy
from Operator import Operator

# ===========================================================================
#                 the resource that repairs the machines
# ===========================================================================
class Repairman(Operator):
    def __init__(self, id, name, capacity=1,**kw):
        Operator.__init__(self,id=id, name=name, capacity=capacity)
        self.type="Repairman"
        from Globals import G
        G.RepairmanList.append(self) 
        
