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
#The Import_Excel object
class ImportExceldata(object):
#This object reads data from different worksheets of an Excel document
    def Input_data(self,worksheetName,inputbook):         #This method takes as an argument the Name of the preferred worksheet 
            
            workbook = inputbook
            worksheet = workbook.sheet_by_name(worksheetName)
            num_rows = worksheet.nrows 
            num_cols = worksheet.ncols 
            
            title=[]                            #Create a new list 
            i=1
            for i in range(num_cols):
                title.append(worksheet.cell_value(0, i))  #Put in this new list the names of the first row (attributes)of the worksheet
            
            i=2
            j=1   
            worksheetDict = {}                  #Create a python dictionary 
            for i in range(num_cols):
                tempList = []                   #Create a new list
                for j in range(1,num_rows):    
                    tempList.append(worksheet.cell_value(j,i))  #Put in this list the cells' values of each column in the worksheet
                if title[i] != '':                              
                    worksheetDict.update({title[i]: tempList})  #Update the dictionary only with excel columns with existed data, give as a key the name of the name of the attribute (e.g. Moulding) 
            return worksheetDict                                #Return the created dictionary
