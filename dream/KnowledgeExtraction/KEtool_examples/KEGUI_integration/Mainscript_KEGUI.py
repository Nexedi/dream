'''
Created on 28 Feb 2014

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

import xlrd
import json
from DistributionFitting import DistFittest
from ImportExceldata import ImportExceldata

workbook = xlrd.open_workbook('Mockup_ProcessingTimes.xls')      #Using xlrd library opens the Excel document with the input data 
worksheets = workbook.sheet_names()
worksheet_ProcessingTimes = worksheets[0]   #It defines the worksheet_ProcessingTimes as the first sheet of the Excel file

A=ImportExceldata()            #Call the Import_Excel object 
B=DistFittest()             #Call the Distribution Fitting object
ProcessingTimes= A.Input_data(worksheet_ProcessingTimes, workbook)  #Create a dictionary with the imported data from the Excel file

jsonFile= open('BatchesInput.json','r')       #open the json file
data = json.load(jsonFile)                            #It loads the file
jsonFile.close()
nodes = data['nodes'] 

lista=[]
for (element_id, element) in nodes.iteritems():  #This loop appends in a list the id's of the json file
    element['id'] = element_id 
    lista.append(element ['id'])

fittingDict={}
for element in ProcessingTimes:             #This loop searches the elements of the Excel imported data and if these elements exist in json file append the distribution fitting results in a dictionary   
    if element in lista:
        fittingDict[element]=B.ks_test(ProcessingTimes[element])

for (element_id, element) in nodes.iteritems():  #This loop searches the ids in the json file and if the id exist in the dictionary with the distribution fitting results, replace the processing time node
    if element_id in fittingDict:
        element['processingTime']=fittingDict[element_id]
           
jsonFile = open('BatchesOutput.json',"w")     #It opens the JSON file
jsonFile.write(json.dumps(data, indent=4))                                           #It writes the updated data to the JSON file 
jsonFile.close()                                                                        #It closes the file
