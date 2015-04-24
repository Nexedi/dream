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

#The StatisticalMeasures object
class StatisticalMeasures(object):
# A variety of statistical measures are calculated in this object
    def length(self, data):                      #Calculate the length of data sample
        data=robjects.FloatVector(data)          ##The given list changes into float vector in order to be handled by RPy2
        rlength = robjects.r['length']           #Call length function-R function
        return rlength(data)[0]
     
    def summary(self, data):                    #Calculate the summary of data sample (output the results in a specific format used in R)
        data=robjects.FloatVector(data)
        rsummary = robjects.r['summary']        #Call summary - R function
        return rsummary(data)
        
    def quantile(self,data):                   #Calculate the quantiles (0%,25%,50%,75%,100%) of the data sample
        data=robjects.FloatVector(data)
        rquantile = robjects.r['quantile']     #Call quantile - R function
        return rquantile(data)
    
    def min(self,data):                     #Calculate the minimum value of a data sample
        data=robjects.FloatVector(data)
        rmin= robjects.r['min']            #Call min - R function
        return rmin(data)[0]
    
    def max(self,data):                     #Calculate the maximum value of a data sample
        data=robjects.FloatVector(data)
        rmax= robjects.r['max']            #Call max - R function
        return rmax(data)[0]
         
    def frequency(self,data):                  #Calculate the frequency of a data point in the sample
        data=robjects.FloatVector(data)
        rtable= robjects.r['table']            #Call table - R function
        return rtable(data)
        
    def mean(self, data):                     #Calculate the mean value of a data sample 
        data=robjects.FloatVector(data)
        rmean = robjects.r['mean']             #Call mean - R function
        return rmean(data)[0]
    
    def median (self, data):                     #Calculate the median value of a data sample 
        data=robjects.FloatVector(data)
        rmedian = robjects.r['median']             #Call median - R function
        return rmedian(data)[0]
    
    def var (self, data):                      #Calculate the variance of a data sample
        data=robjects.FloatVector(data)
        rvar = robjects.r['var']               #Call variance function - R function
        return rvar(data)[0]
    
    def sd (self, data):                       #Calculate the standard deviation of a data sample
        data=robjects.FloatVector(data)
        rsd = robjects.r['sd']                 #Call standard deviation function - R function
        return rsd(data)[0]

    def range (self, data):                    #Calculate the range of a data sample
        data=robjects.FloatVector(data)
        rrange = robjects.r['range']           #Call range function - R function
        return list(rrange(data))
    
    def mad (self,data):                        #Calculate the median absolute deviation of a data sample
        data=robjects.FloatVector(data)
        rmad = robjects.r['mad']                  #Call mad function - R function
        return rmad(data)[0]
        
    def IQR (self, data):                      #Calculate the Interquartile range (IQR) of a data sample
        data=robjects.FloatVector(data)
        rIQR = robjects.r['IQR']               #Call IQR function - R function
        return rIQR(data)[0]
    
    def all(self, data):                       #Print the results of the above measures
        data=robjects.FloatVector(data)
        print 'The length of the data set is:', self.length(data)
        print 'The summary is:', self.summary(data)
        print 'The quartiles and percentiles of the data set are:', self.quantile(data)
        print 'The frequency of the datapoints are:', self.frequency(data)
        print 'The mean value is:', self.mean(data)
        print 'The median value is:', self.median(data)
        print 'The max value is:', self.max(data)
        print 'The min value is:', self.min(data)
        print 'The standard deviation is:', self.sd(data)
        print 'The variance is:', self.var(data)
        print 'The median absolute deviation is:', self.mad(data)
        print 'The range is:', self.range(data)
        print 'The Interquartile Range is:', self.IQR(data)