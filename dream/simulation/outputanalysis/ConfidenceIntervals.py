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
Created on 16 Nov 2013

@author: Panos
'''
from rpy2.robjects.packages import importr
from rpy2 import robjects

MASS= importr('MASS')


class Intervals:
    
    
    def ConfidIntervals(self,data,p): 
  
        data=robjects.FloatVector(data)  
        alpha=1-p
        rsqrt=robjects.r['sqrt']
        rsd=robjects.r['sd']
        rmean=robjects.r['mean']
        t=len(data)
        n=rsqrt(t)
        b=rsd(data)

        rqt=robjects.r['qt']
        q=rqt((1-(alpha/2)),t-1)
        m=rmean(data)

        me=q[0]*(b[0]/n[0])

        lo=m[0]-me
        up=m[0]+me
        l=[lo,up]
        return l




