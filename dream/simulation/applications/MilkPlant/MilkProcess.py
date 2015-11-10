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
models the process of the milk
'''

from dream.simulation.MachineJobShop import MachineJobShop

class MilkProcess(MachineJobShop):                                     
    family='Server'
    
    def initialize(self):
        # keep the ids of products that have already been processed
        self.alreadyProcessedProductIds=[]
        MachineJobShop.initialize(self)

    # processing time will be used only for the first unit of the product. Otherwise it will be dummy 0
    def getEntity(self):
        activeEntity=MachineJobShop.getEntity(self)
        productId=activeEntity.productId
        if productId not in self.alreadyProcessedProductIds:
            self.alreadyProcessedProductIds.append(productId)
        else:
            self.procTime=0
        return activeEntity

        
            
            
            
            
        
        
        