'''
Created on 13 Jun 2014

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
import csv
#The Import_CSV object
class ImportCSVdata(object):
#This object reads data from a CSV document
    def Input_data(self,fileName):         #This method takes as an argument the Name of the CSV file
        #Opens the CSV for the reader to use
        reader = csv.reader(open(fileName, "rb"), delimiter = ',')
        headers=[]   #Create a new list to insert the labels of the data sets
        csvInput=list(reader)
        for element in csvInput[0]:
            headers.append(element)       #Insert the labels in the list headers

            dictData={}         #Create a dictionary to input the CSV data
            for header in headers:
                dictData[header]=[]    #Insert as keys in the dictionary the labels of the data sets 

        for row in csvInput:
            if row==csvInput[0]:     #Input in the dictionary the data apart from the first row (headers)
                continue
            else:
                for j in range(len(row)):
                    dictData[headers[j]].append(row[j])
        return dictData