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
Created on 16 Dec 2013

@author: Panos
'''
from rpy2 import robjects

class Graphs:
    
    def Plots(self,data, fileName="plotChart.jpg"):
        data=robjects.FloatVector(data)
        rplot=robjects.r['plot']
        rdev=robjects.r['dev.off']
        rjpeg=robjects.r['jpeg']
    
        output=rjpeg(fileName)
        rplot(data, type="o", col="blue")
        rdev
        return output
    
    def ScatterPlot(self,data1,data2, fileName="scatterplot.jpg"):
        data1=robjects.FloatVector(data1)
        data2=robjects.FloatVector(data2)
        
        rplot=robjects.r['plot']
        rdev=robjects.r['dev.off']
        rjpeg=robjects.r['jpeg']
    
        output=rjpeg(fileName)
        rplot(data1,data2, type="o", col="red")
        rdev
        return output

    def Pie(self, data1, fileName="pieChart.jpg"):
        data1=robjects.FloatVector(data1)
        rpaste=robjects.r['paste']
        rround=robjects.r['round']
        rsum=robjects.r['sum']
        rpie=robjects.r['pie']
   
        rdev=robjects.r['dev.off']

        colors=robjects.StrVector(["white","grey70","grey90","grey50","grey60","black"])
        s=rsum(data1)
        d_labels=[0]*(len(data1))
   
        i=0
        while i<len(data1):
            d_labels[i]=((rround((data1[i]/s[0])*100,1)))
            i+=1
    
        d_labels=rpaste(d_labels,"%",sep="")
        rjpeg=robjects.r['jpeg']
    
        export=rjpeg(fileName)
        rpie(data1,main="Data",col=colors,labels=d_labels,cex=0.8)
        rdev
        return export


