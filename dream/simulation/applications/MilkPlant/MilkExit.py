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
models the exit of the milk. Mostly to gather statistics
'''

from dream.simulation.ExitJobShop import ExitJobShop

class MilkExit(ExitJobShop):                 
    def initialize(self):
        ExitJobShop.initialize(self)
        self.finishedProductDict={}
                        
    def getEntity(self):
        activeEntity=ExitJobShop.getEntity(self)
        productId=activeEntity.productId
        if productId in self.finishedProductDict.keys():
            self.finishedProductDict[productId]['totalFat']+=activeEntity.fat
            self.finishedProductDict[productId]['volume']+=activeEntity.liters
            self.finishedProductDict[productId]['exitTime']=self.env.now
        else:
            self.finishedProductDict[productId]={'totalFat':activeEntity.fat,'volume':activeEntity.liters,'exitTime':self.env.now}
        return activeEntity
        
            
            
            
            
        
        
        