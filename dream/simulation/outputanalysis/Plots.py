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

#The Graphs object
class Graphs:
    #Graphs that can visualize the data samples 
    
    def Plots(self,data, fileName="plotChart.jpg"):
        data=robjects.FloatVector(data)   #The given list changes into float vector in order to be handled by RPy2
        rplot=robjects.r['plot']      #Call plot function - R function
        rdev=robjects.r['dev.off']    #Call dev.off - R function
        rjpeg=robjects.r['jpeg']      #Call jpeg - R function
    
        output=rjpeg(fileName)        #output the plot (jpeg file format) in the given directory
        rplot(data, type="o", col="blue")     #Graph data sample and define color and type for the data points visualization
        rdev
        return output
    
    def ScatterPlot(self,data1,data2, fileName="scatterplot.jpg"):
        #The given lists change into float vector in order to be handled by RPy2
        data1=robjects.FloatVector(data1)
        data2=robjects.FloatVector(data2)
        
        rplot=robjects.r['plot']
        rdev=robjects.r['dev.off']
        rjpeg=robjects.r['jpeg']
    
        output=rjpeg(fileName)            #Graph data samples and define color and type for the data points visualization
        rplot(data1,data2, type="o", col="red")
        rdev
        return output

    def Pie(self, data1, fileName="pieChart.jpg"):
        data1=robjects.FloatVector(data1)      #The given list changes into float vector in order to be handled by RPy2
        rpaste=robjects.r['paste']          #Call paste - R function 
        rround=robjects.r['round']          #Call round - R function 
        rsum=robjects.r['sum']              #Call sum - R function
        rpie=robjects.r['pie']              #Call pie - R function
   
        rdev=robjects.r['dev.off']

        colors=robjects.StrVector(["white","grey70","grey90","grey50","grey60","black"])  #Define colors to be used for black&white print
        s=rsum(data1)
        d_labels=[0]*(len(data1))
   
        i=0
        while i<len(data1):
            d_labels[i]=((rround((data1[i]/s[0])*100,1)))      #Calculate the percentage for each data point, rounded to one decimal place
            i+=1
    
        d_labels=rpaste(d_labels,"%",sep="")    #Concatenate a "%" car after each value           
        rjpeg=robjects.r['jpeg']
    
        export=rjpeg(fileName)
        rpie(data1,main="Data",col=colors,labels=d_labels,cex=0.8)   #Create a pie chart with defined heading and custom colors 
        rdev
        return export


