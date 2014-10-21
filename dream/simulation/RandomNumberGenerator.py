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
Created on 14 Feb 2013

@author: George
'''

'''
holds methods for generations of numbers from different distributions
'''
class RandomNumberGenerator(object):
    def __init__(self, obj, distributionType, mean=0, stdev=0, min=0, max=0, alpha=0, beta=0,
                 logmean=0,logsd=0, probability=0, shape=0, scale=0, location=0):
        self.distributionType = distributionType
        self.mean = float(mean or 0)
        self.stdev = float(stdev or 0)
        self.min = float(min or 0)
        self.max = float(max or 0)
        self.alpha = float(alpha or 0)
        self.beta = float(beta or 0)
        self.logmean=float(logmean or 0)
        self.logsd=float(logsd or 0)
        self.probability=float(probability or 0)
        self.shape=float(shape or 0)
        self.scale=float(scale or 0)
        self.location=float(location or 0)
        self.obj = obj

        

    def generateNumber(self):
        from Globals import G
        if(self.distributionType=="Fixed"):     #if the distribution is Fixed 
            return self.mean
        elif(self.distributionType=="Exp"):     #if the distribution is Exponential
            return G.Rnd.expovariate(1.0/(self.mean))
        elif(self.distributionType=="Normal"):      #if the distribution is Normal
            if self.max < self.min:
                 raise ValueError("Normal distribution for %s uses wrong "
                                  "parameters. max (%s) > min (%s)" % (
                                    self.obj.id, self.max, self.min))
            while 1:
                number=G.Rnd.normalvariate(self.mean, self.stdev)
                if number>self.max or number<self.min and max!=0:  #if the number is out of bounds repeat the process                                                                      #if max=0 this means that we did not have time "time" bounds             
                    continue
                else:           #if the number is in the limits stop the process
                    return number
        elif self.distributionType=="Erlang":    #if the distribution is erlang          
            return G.Rnd.gammavariate(self.alpha, self.beta)
        else:
            raise ValueError("Unknown distribution %r used in %s %s" %
                            (self.distributionType, self.obj.__class__, self.obj.id))

