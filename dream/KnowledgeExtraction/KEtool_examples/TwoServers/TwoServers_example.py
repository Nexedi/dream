'''
Created on 19 Feb 2014

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

from dream.KnowledgeExtraction.ImportExceldata import Import_Excel
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.ExcelOutput import Output
from dream.KnowledgeExtraction.JSONOutput import JSONOutput
from dream.KnowledgeExtraction.ReplaceMissingValues import HandleMissingValues
import dream.simulation.LineGenerationJSON as ManPyMain #import ManPy main JSON script
from xml.etree import ElementTree as et
import xlrd
import json

#================================================ This script is a simple example of the Knowledge extraction tool ===============================================================#

#The following is the Main script, that calls two Python objects in order to conduct the three main components of the Knowledge extraction tool
#In the following example the operation times of the topology's two machines are given in an Excel document. 
#Import_Excel object imports data from the Excel document to the tool and DistFittest object fits the data to a statistical distribution using Kolmogorov-Smirnov test
   
workbook = xlrd.open_workbook('inputsTwoServers.xls')      #Using xlrd library opens the Excel document with the input data 
worksheets = workbook.sheet_names()
worksheet_OperationTime = worksheets[0]             #It creates a variable that holds the first Excel worksheet 
 
X=Import_Excel()                                    #Call the import_Excel object
OperationTimes= X.Input_data(worksheet_OperationTime,workbook)      #It defines a Python dictionary, giving as name OpearationTimes and as value the returned dictionary from the import_Excel object 
Machine1_OpearationTimes = OperationTimes.get('Machine1',[])        #Two lists are defined (Machine1_OpearationTimes, Machine2_OpearationTimes) with the operation times data of each machine
Machine2_OpearationTimes = OperationTimes.get('Machine2',[])

A=HandleMissingValues()                                     #Call the HandleMissingValues object
Machine1_OpearationTimes= A.DeleteMissingValue(Machine1_OpearationTimes)        #It deletes the missing values in the lists with the operation times data
Machine2_OpearationTimes= A.DeleteMissingValue(Machine2_OpearationTimes)

Dict={}
B=DistFittest()                                     #It calls the DistFittest object
Dict['M1']=B.ks_test(Machine1_OpearationTimes)                 #It conducts the Kolmogorov-Smirnov test in the list with the operation times data 
Dict['M2']=B.ks_test(Machine2_OpearationTimes)
M1=Dict.get('M1')
M2=Dict.get('M2')


#==================================== Output preparation: output the updated values in the CMSD information model of Topology10 ====================================================#

datafile=('CMSD_TwoServers.xml')       #It defines the name or the directory of the XML file that is manually written the CMSD information model
tree = et.parse(datafile)                                               #This file will be parsed using the XML.ETREE Python library

M1Parameters=[]
M1ParameterValue=[]
for index in list(Dict['M1'].keys()):
    if index is not 'distributionType':
        M1Parameters.append(index)
        M1ParameterValue.append(Dict['M1'][index])
if Dict['M1']['distributionType']=='Normal':
    del M1['min']
    del M1['max']
elif Dict['M2']['distributionType']=='Normal':
    del M2['min']
    del M2['max']

M2Parameters=[]
M2ParameterValue=[]
for index in list(Dict['M2'].keys()):
    if index is not 'distributionType':
        M2Parameters.append(index)
        M2ParameterValue.append(Dict['M2'][index])       

root=tree.getroot()
process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
for process in process:
    process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
    if process_identifier=='A020':                                      #It checks using if...elif syntax if the process identifier is 'A020', so the process that uses the first machine
        OperationTime=process.get('OpeationTime')                       #It gets the element attribute OpearationTime inside the Process node
        Distribution=process.get('./OperationTime/Distribution')        #It gets the element attribute Distribution inside the OpearationTime node
        Name=process.find('./OperationTime/Distribution/Name')          #It finds the subelement Name inside the Distribution attribute
        Name.text=Dict['M1']['distributionType']                                     #It changes the text between the Name element tags, putting the name of the distribution (e.g. in Normal distribution that will be Normal) 
        DistributionParameterA=process.get('./OperationTime/Distribution/DistributionParameterA')
        Name=process.find('./OperationTime/Distribution/DistributionParameterA/Name')
        Name.text=str(M1Parameters[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
        Value=process.find('./OperationTime/Distribution/DistributionParameterA/Value')
        Value.text=str(M1ParameterValue[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
        DistributionParameterB=process.get('./OperationTime/Distribution/DistributionParameterB')
        Name=process.find('./OperationTime/Distribution/DistributionParameterB/Name')
        Name.text=str(M1Parameters[1])                                #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
        Value=process.find('./OperationTime/Distribution/DistributionParameterB/Value')
        Value.text=str(M1ParameterValue[1])                           #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
    elif process_identifier=='A040':                                #It checks using if...elif syntax if the process identifier is 'A040', so the process that uses the second machine 
        OperationTime=process.get('OpeationTime')
        Distribution=process.get('./OperationTime/Distribution')
        Name=process.find('./OperationTime/Distribution/Name')
        Name.text=Dict['M2']['distributionType'] 
        DistributionParameterA=process.get('./OperationTime/Distribution/DistributionParameterA')
        Name=process.find('./OperationTime/Distribution/DistributionParameterA/Name')
        Name.text=str(M2Parameters[0]) 
        Value=process.find('./OperationTime/Distribution/DistributionParameterA/Value')
        Value.text=str(M2ParameterValue[0]) 
        DistributionParameterB=process.get('./OperationTime/Distribution/DistributionParameterB')
        Name=process.find('./OperationTime/Distribution/DistributionParameterB/Name')
        Name.text=str(M2Parameters[1]) 
        Value=process.find('./OperationTime/Distribution/DistributionParameterB/Value')
        Value.text=str(M2ParameterValue[1]) 
    else:
        continue
    tree.write('CMSD_TwoServers_Output.xml',encoding="utf8")                         #It writes the element tree to a specified file, using the 'utf8' output encoding

#================================= Output preparation: output the updated values in the JSON file of Topology10 =========================================================#
jsonFile= open('JSON_TwoServers.json','r')      #It opens the Topology10 JSON file 
data = json.load(jsonFile)                                                              #It loads the file
jsonFile.close()

exportJSON=JSONOutput()
stationId1='M1'
stationId2='M2'
data=exportJSON.ProcessingTimes(data, stationId1, M1)                           
data1=exportJSON.ProcessingTimes(data, stationId2, M2)         

jsonFile = open('JSON_TwoServers_Output.json',"w")     #It opens the JSON file
jsonFile.write(json.dumps(data1, indent=True))                                           #It writes the updated data to the JSON file 
jsonFile.close()                                                                        #It closes the file
    
#================================ Calling the ExcelOutput object, outputs the outcomes of the statistical analysis in Excel files =============================================#
C=Output()
C.PrintDistributionFit(Machine1_OpearationTimes,'Machine1_DistFitResults.xls')   
C.PrintStatisticalMeasures(Machine1_OpearationTimes,'Machine1_StatResults.xls')
C.PrintDistributionFit(Machine2_OpearationTimes,'Machine2_DistFitResults.xls')   
C.PrintStatisticalMeasures(Machine2_OpearationTimes,'Machine2_StatResults.xls')

#================================ Call ManPy and run the simulation model =============================================#
#calls ManPy main script with the input
simulationOutput=ManPyMain.main(input_data=json.dumps(data))
# save the simulation output
jsonFile = open('ManPyOutput.json',"w")     #It opens the JSON file
jsonFile.write(simulationOutput)                                           #It writes the updated data to the JSON file 
jsonFile.close()                                                                        #It closes the file
    