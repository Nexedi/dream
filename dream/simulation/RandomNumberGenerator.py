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

import math

class RandomNumberGenerator(object):
    # data should be given as a dict:
#     "distribution": {
#         "distributionType": {
#             "mean": 10,
#             "stdev": 1,
#             "parameterX":X,
#            ...
#         },
    def __init__(self, obj, distribution):   
        # if the distribution is not given as a dictionary throw error
        if not isinstance(distribution, dict):
            raise ValueError("distribution must be given as a dict")             
        # check in case an unknown distribution was given
        unknownDistribution=True
        for key in distribution.keys():
            if key in ['Fixed', 'Normal','Exp','Gamma','Logistic','Erlang',
                           'Geometric','Lognormal','Weibull','Cauchy', 'Triangular']:
                unknownDistribution=False
                break
        if unknownDistribution:
            # XXX accept old format ??
            if 'distributionType' in distribution:
                from copy import copy
                distribution = copy(distribution) # we do not store this in json !
                distribution[distribution.pop('distributionType')] = (distribution)
            else:
                raise ValueError("Unknown distribution %r used in %s %s" %
                            (distribution, obj.__class__, obj.id)) 
        # pop irrelevant keys
        for key in distribution.keys():
            if key not in ['Fixed', 'Normal','Exp','Gamma','Logistic','Erlang',
                           'Geometric','Lognormal','Weibull','Cauchy', 'Triangular']:
                distribution.pop(key, None)
        self.distribution=distribution
        self.distributionType = distribution.keys()[0]
        parameters=distribution[self.distributionType]
        # if a parameter is passed as None or empty string set it to 0
        for key in parameters:
            if parameters[key] in [None,'']:
                parameters[key]=0.0
        self.mean = float(parameters.get('mean', 0))
        self.stdev = float(parameters.get('stdev', 0))
        self.min = float(parameters.get('min',0))
        self.max = float(parameters.get('max',0))
        self.alpha = float(parameters.get('alpha',0))
        self.beta = float(parameters.get('beta',0))
        self.logmean=float(parameters.get('logmean',0))
        self.logsd=float(parameters.get('logsd',0))
        self.probability=float(parameters.get('probability',0))
        self.shape=float(parameters.get('shape',0))
        self.scale=float(parameters.get('scale',0))
        self.location=float(parameters.get('location',0))
        self.rate=float(parameters.get('rate',0))
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
        elif self.distributionType=="Gamma" or self.distributionType=="Erlang":    #if the distribution is gamma or erlang
            # in case shape is given instead of alpha
            if not self.alpha:
                self.alpha=self.shape
            # in case rate is given instead of beta
            if not self.beta:
                self.beta=1/float(self.rate)          
            return G.Rnd.gammavariate(self.alpha, self.beta)
        elif(self.distributionType=="Logistic"):     #if the distribution is Logistic
            # XXX from http://stackoverflow.com/questions/3955877/generating-samples-from-the-logistic-distribution
            # to check
            while 1:
                x = G.Rnd.random()
                number=self.location + self.scale * math.log(x / (1-x))
                if number>0:
                    return number
                else:
                    continue
        elif(self.distributionType=="Geometric"):     #if the distribution is Geometric
            return G.numpyRnd.random.geometric(self.probability)
        elif(self.distributionType=="Lognormal"):     #if the distribution is Lognormal
            # XXX from the files lognormvariate(mu, sigma)
            # it would be better to use same mean,stdev
            return G.Rnd.lognormvariate(self.logmean, self.logsd)
        elif(self.distributionType=="Weibull"):     #if the distribution is Weibull
            return G.Rnd.weibullvariate(self.scale, self.shape)
        elif(self.distributionType=="Cauchy"):     #if the distribution is Cauchy
            # XXX from http://www.johndcook.com/python_cauchy_rng.html
            while 1:
                p = 0.0
                while p == 0.0:
                    p = G.Rnd.random()     
                number=self.location + self.scale*math.tan(math.pi*(p - 0.5))
                if number>0:
                    return number
                else:
                    continue
        elif(self.distributionType=="Triangular"):     #if the distribution is Triangular
            return G.numpyRnd.random.triangular(left=self.min, right=self.max, mode=self.mean)
        else:
            raise ValueError("Unknown distribution %r used in %s %s" %
                            (self.distributionType, self.obj.__class__, self.obj.id))

