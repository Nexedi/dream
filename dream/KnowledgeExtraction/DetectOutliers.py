'''
Created on 24 Sep 2014

@author: Panos
'''
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

from StatisticalMeasures import BasicStatisticalMeasures 

#The DetectOuliers object
class HandleOutliers(BasicStatisticalMeasures):
#Two different approaches to handle the outliers are included in this object, 
#the first one delete both the mild and extreme outliers while the second approach delete only the extreme outliers in the given data set 
    def DeleteOutliers(self,mylist):              #Delete the ouliers (both mild and extreme) in a given data set
        Q1= self.quantile(mylist)[1]
        Q3= self.quantile(mylist)[3]
        IQ= self.IQR(mylist)
        LIF= Q1 - 1.5*IQ                        #Calculate the lower inner fence
        UIF= Q3 + 1.5*IQ                        #Calculate the upper inner fence
        LOF= Q1 - 3*IQ                          #Calculate the lower outer fence
        UOF= Q3 + 3*IQ                          #Calculate the upper outer fence
        i=0
        listx=[]
        for value in mylist:                       
            if not ((float(value)<float(LOF) or float(value)>float(UOF)) or (float(value)<float(LIF) or float(value)>float(UIF))):    #If the value is beyond the inner fence ([LIF,UIF]) on either side (mild outlier) or beyond the outer fence ([LOF,UOF]) on either side (extreme outlier) doesn't pass the control and deleted  
                listx.append(value)
            i+=1 
        return listx
    
    def DeleteExtremeOutliers(self,mylist):            #Delete only the  extreme ouliers in a given data set
        Q1= self.quantile(mylist)[1]
        Q3= self.quantile(mylist)[3]
        IQ= self.IQR(mylist)
        LOF= Q1 - 3*IQ 
        UOF= Q3 + 3*IQ
        i=0
        listx=[]
        for value in mylist:
            if not (float(value)<float(LOF) or float(value)>float(UOF)):           #If the value is  beyond the outer fence ([LOF,UOF]) on either side (extreme outlier) doesn't pass the control and deleted  
                listx.append(value)
            i+=1
        return listx
        
                
                
                
            
    