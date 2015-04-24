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
Created on 16 Apr 2014

@author: Panos
'''

import rpy2.robjects as robjects

#The DataManipulation object
class DataManipulation(object):
    
    def round(self, data):                      #returns the rounded values of the data sample
        data=robjects.FloatVector(data)          ##The given list changes into float vector in order to be handled by RPy2
        rround = robjects.r['round']            #Call the round  function-R function
        return list(rround(data))
        
    def ceiling(self, data):                      #returns the smallest integers bigger than the values of the data sample
        data=robjects.FloatVector(data)          
        ceiling = robjects.r['ceiling']           #Call the ceiling function-R function
        return list(ceiling(data))
    
    def floor(self, data):                      #returns the largest integers smaller than the values of the data sample
        data=robjects.FloatVector(data)          
        floor = robjects.r['floor']             #Call the floor function-R function
        return list(floor(data))
    
    def abs(self,data):                         #returns a list with the absolute values of the data sample
        data=robjects.FloatVector(data)          
        rabs = robjects.r['abs']                 #Call the abs function-R function
        return list(rabs(data))
    
    def sqrt(self,data):                        #returns the square root of the values in the data sample
        data=robjects.FloatVector(data)          
        rsqrt = robjects.r['sqrt']              #Call the sqrt function-R function
        return list(rsqrt(data))
        
    
    