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
Created on 14 Nov 2013

@author: Panos
'''

import rpy2.robjects as robjects

#The BasicTransformations object
class Transformations(object):
# A variety of transformations are calculated in this object
    def sum(self, data):                      #calculates the sum of data sample
        data=robjects.FloatVector(data)          ##The given list changes into float vector in order to be handled by RPy2
        rsum = robjects.r['sum']           #Call sum function-R function
        return rsum(data)[0]
    
    def subtraction(self, data1, data2):
        data1=robjects.FloatVector(data1)
        data2=robjects.FloatVector(data2)
        rsubtraction = data1.ro - data2
        return list(rsubtraction)
    
    def multiplication(self, data1, data2):
        data1=robjects.FloatVector(data1)
        data2=robjects.FloatVector(data2)
        rmultiplication = data1.ro * data2
        return list(rmultiplication)
    
    def division(self, data1, data2):
        data1=robjects.FloatVector(data1)
        data2=robjects.FloatVector(data2)
        rdivision = data1.ro / data2
        return list(rdivision)
    
    def scale(self, data):                    #centers around the mean and scales by the standard deviation (sd) 
        data=robjects.FloatVector(data)
        rscale = robjects.r['scale']        #Call scale - R function
        return list(rscale(data))
    
    def cumsum(self,data):                  #returns the cumulative sum of data sample
        data=robjects.FloatVector(data)
        rcumsum = robjects.r['cumsum']        #Call cumsum - R function
        return list(rcumsum(data))
    
    def cumprod(self,data):                  #returns the cumulative product of data sample
        data=robjects.FloatVector(data)
        rcumprod = robjects.r['cumprod']        #Call cumprod - R function
        return list(rcumprod(data))
    
    def cummax(self,data):                  #returns the cumulative maximum of data sample
        data=robjects.FloatVector(data)
        rcummax = robjects.r['cummax']        #Call cummax - R function
        return list(rcummax(data))
     
    def cummin(self,data):                   #returns the cumulative minimum of data sample
        data=robjects.FloatVector(data)
        rcummin = robjects.r['cummin']        #Call cummin - R function
        return list(rcummin(data)) 
    
    def rev(self,data):                  #reverse the order of values in the data sample
        data=robjects.FloatVector(data)
        rrev = robjects.r['rev']        #Call rev - R function
        return list(rrev(data))   
        