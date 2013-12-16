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
from rpy2.robjects.packages import importr

MASS= importr('MASS')

class BasicStatisticalMeasures:

    def length(self, data):
        data=robjects.FloatVector(data)
        rlength = robjects.r['length']
        return rlength(data)
     
    def summary(self, data):
        data=robjects.FloatVector(data)
        rsummary = robjects.r['summary']
        return rsummary(data)
        
    def quantile(self,data):
        data=robjects.FloatVector(data)
        rquantile = robjects.r['quantile']
        return rquantile(data)
    
    def frequency(self,data):
        data=robjects.FloatVector(data)
        rtable= robjects.r['table']
        return rtable(data)
        
    def mean (self, data):
        data=robjects.FloatVector(data)
        rmean = robjects.r['mean']
        return rmean(data)
    
    def var (self, data):
        data=robjects.FloatVector(data)
        rvar = robjects.r['var']
        return rvar(data)
    
    def sd (self, data):
        data=robjects.FloatVector(data)
        rsd = robjects.r['sd']
        return rsd(data)

    def range (self, data):
        data=robjects.FloatVector(data)
        rrange = robjects.r['range']
        return rrange(data)
        
    def IQR (self, data):
        data=robjects.FloatVector(data)
        rIQR = robjects.r['IQR']
        return rIQR(data)
    
    def all(self, data):
        data=robjects.FloatVector(data)
        print 'The length of the data set is:', self.length(data)[0]
        print 'The summary is:', self.summary(data)
        print 'The quartiles and percentiles of the data set are:', self.quantile(data)
        print 'The frequency of the datapoints are:', self.frequency(data)
        print 'The mean value is:', self.mean(data)[0]
        print 'The standard deviation is:', self.sd(data)[0]
        print 'The variance is:', self.var(data)[0]
        print 'The range is:', self.range(data)[0]
        print 'The Interquartile Range is:', self.IQR(data)[0]