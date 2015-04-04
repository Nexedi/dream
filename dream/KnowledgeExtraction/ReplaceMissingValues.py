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
Created on 19 Feb 2014

@author: Panos
'''
from StatisticalMeasures import BasicStatisticalMeasures

#The HandleMissingValues object
class HandleMissingValues(BasicStatisticalMeasures):
#Three different approaches to handle missing values are included in this object 
    def ReplaceWithZero(self,mylist):          #Replace in the given list the missing values with zero
        i=0   
        for value in mylist:                    
            if value is '' :
                mylist[i]=0.0                  #For the values in the list if there is a missing value replace it with zero
            i+=1  
        return mylist                          #Return the replaced list 
    
    def DeleteMissingValue(self,mylist):       #Delete the missing value in the given list 
        i=0
        listX=[]                               #Create a new list 
        for value in mylist:
            if value != '':
                listX.append(value)            #Add in the new list the non missing values from the given list  
            i+=1 
        return listX                           #Return the new list, which has the non missing values from the initial given list 
    
    def ReplaceWithMean(self,mylist):          #Replace in the given list the missing values with the mean value  
        list1=self.DeleteMissingValue(mylist)  #Create a new list, which is the given list deleting the missing values (calling the DeleteMissingValue method)
#         mean=sum(list1)/float(len(list1))      #Calculate the mean value of the new list
        mean=self.mean(list1)
        i=0
        for value in mylist:
            if value is '' :
                mylist[i]=mean                #For the values in the initial given list if there is a missing value replace it with the mean value of the new list
            i+=1 
        return mylist                         #Return the given list, in which the missing values are replaced with the mean value 
    
    def ReplaceWithMedian(self,mylist):       #Replace in the given list the missing values with the median value 
        list1=self.DeleteMissingValue(mylist) #Create a new list, which is the given list deleting the missing values (calling the DeleteMissingValue method)
#         A=BasicStatisticalMeasures()          #Call the BasicStatisticalMeasures to calculate the median value
        median=self.median(list1)                #Calculate the median value of the new list
        i=0
        for value in mylist:
            if value is '' :
                mylist[i]=median                #For the values in the initial given list if there is a missing value replace it with the mean value of the new list
            i+=1 
        return mylist                         #Return the given list, in which the missing values are replaced with the mean value
