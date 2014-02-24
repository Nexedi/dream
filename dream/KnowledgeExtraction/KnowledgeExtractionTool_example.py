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

from ImportExceldata import Import_Excel
from DistributionFitting import DistFittest
from xml.etree import ElementTree as et
from ExcelOutput import Output
from ReplaceMissingValues import HandleMissingValues
import xlrd
import json

#================================================ This script is a simple example of the Knowledge extraction tool ===============================================================#

#The following is the Main script, that calls two Python objects in order to conduct the three main components of the Knowledge extraction tool
#In the following example the operation times of the topology's two machines are given in an Excel document. 
#Import_Excel object imports data from the Excel document to the tool and DistFittest object fits the data to a statistical distribution using Kolmogorov-Smirnov test
   
workbook = xlrd.open_workbook('inputsKEtool.xls')      #Using xlrd library opens the Excel document with the input data 
worksheets = workbook.sheet_names()
worksheet_OperationTime = worksheets[0]             #It creates a variable that holds the first Excel worksheet 
 
X=Import_Excel()                                    #Call the import_Excel object
OperationTimes= X.Input_data(worksheet_OperationTime,workbook)      #It defines a Python dictionary, giving as name OpearationTimes and as value the returned dictionary from the import_Excel object 
Machine1_OpearationTimes = OperationTimes.get('Machine1',[])        #Two lists are defined (Machine1_OpearationTimes, Machine2_OpearationTimes) with the operation times data of each machine
Machine2_OpearationTimes = OperationTimes.get('Machine2',[])

A=HandleMissingValues()                                     #Call the HandleMissingValues object
Machine1_OpearationTimes= A.DeleteMissingValue(Machine1_OpearationTimes)        #It deletes the missing values in the lists with the operation times data
Machine2_OpearationTimes= A.DeleteMissingValue(Machine2_OpearationTimes)

B=DistFittest()                                     #It calls the DistFittest object
B.ks_test(Machine2_OpearationTimes)                 #It conducts the Kolmogorov-Smirnov test in the list with the operation times data 
B.ks_test(Machine1_OpearationTimes)
lista=[]                                            #It creates a list, that contains the outcome of the Kolmogorov-Smirnov tests  
lista.append(B.ks_test(Machine1_OpearationTimes))
lista.append(B.ks_test(Machine2_OpearationTimes))

names = []                                          #It defines the following five lists
aParameters=[]
bParameters=[]
aParameterValue=[]
bParameterValue=[]

for index in range(len(lista)):
    names.append(lista[index].get('type'))   #Insert the distribution names from the dictionary into the names list 
    aParameters.append(lista[index].get('aParameter'))    #Insert the name of the first parameter of each distribution from the dictionary into the aParameters list   
        
    try:
        bParameters.append(lista[index].get('bParameter'))   #Insert the name of the second parameter of each distribution from the dictionary (if there are any->use of except) into the bParameters list   
    except:
        bParameters.append('')
    aParameterValue.append(lista[index].get('aParameterValue'))     #Insert the value of the first parameter of each distribution from the dictionary into the aParameterValue list 
    try:
        bParameterValue.append(lista[index].get('bParameterValue'))     #Insert the value of the second parameter of each distribution from the dictionary (if there are any->use of except) into the bParameterValue list
    except:
        bParameterValue.append('')   

#==================================== Output preparation: output the updated values in the CMSD information model of Topology10 ====================================================#

datafile=('CMSD_Topology10.xml')       #It defines the name or the directory of the XML file that is manually written the CMSD information model
tree = et.parse(datafile)                                               #This file will be parsed using the XML.ETREE Python library
       
root=tree.getroot()
process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
for process in process:
    process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
    if process_identifier=='A020':                                      #It checks using if...elif syntax if the process identifier is 'A020', so the process that uses the first machine
        OperationTime=process.get('OpeationTime')                       #It gets the element attribute OpearationTime inside the Process node
        Distribution=process.get('./OperationTime/Distribution')        #It gets the element attribute Distribution inside the OpearationTime node
        Name=process.find('./OperationTime/Distribution/Name')          #It finds the subelement Name inside the Distribution attribute
        Name.text=str(names[0])                                     #It changes the text between the Name element tags, putting the name of the distribution (e.g. in Normal distribution that will be Normal) 
        DistributionParameterA=process.get('./OperationTime/Distribution/DistributionParameterA')
        Name=process.find('./OperationTime/Distribution/DistributionParameterA/Name')
        Name.text=str(aParameters[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
        Value=process.find('./OperationTime/Distribution/DistributionParameterA/Value')
        Value.text=str(aParameterValue[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
        DistributionParameterB=process.get('./OperationTime/Distribution/DistributionParameterB')
        Name=process.find('./OperationTime/Distribution/DistributionParameterB/Name')
        Name.text=str(bParameters[0])                               #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
        Value=process.find('./OperationTime/Distribution/DistributionParameterB/Value')
        Value.text=str(bParameterValue[0])                          #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
    elif process_identifier=='A040':                                #It checks using if...elif syntax if the process identifier is 'A040', so the process that uses the second machine 
        OperationTime=process.get('OpeationTime')
        Distribution=process.get('./OperationTime/Distribution')
        Name=process.find('./OperationTime/Distribution/Name')
        Name.text=str(names[1])
        DistributionParameterA=process.get('./OperationTime/Distribution/DistributionParameterA')
        Name=process.find('./OperationTime/Distribution/DistributionParameterA/Name')
        Name.text=str(aParameters[1])
        Value=process.find('./OperationTime/Distribution/DistributionParameterA/Value')
        Value.text=str(aParameterValue[1])
        DistributionParameterB=process.get('./OperationTime/Distribution/DistributionParameterB')
        Name=process.find('./OperationTime/Distribution/DistributionParameterB/Name')
        Name.text=str(bParameters[1])
        Value=process.find('./OperationTime/Distribution/DistributionParameterB/Value')
        Value.text=str(bParameterValue[1])
    else:
        continue
    tree.write(datafile,encoding="utf8")                         #It writes the element tree to a specified file, using the 'utf8' output encoding

#================================= Output preparation: output the updated values in the JSON file of Topology10 =========================================================#
jsonFile= open('JSON_Topology10.json','r')      #It opens the Topology10 JSON file 
data = json.load(jsonFile)                                                              #It loads the file
jsonFile.close()
nodes=data.get('coreObject',[])                                                         #It creates a variable that holds the 'coreObject' list

for element in nodes:
    name=element.get('name')                                                            #It creates a variable that gets the element attribute 'name'
    processingTime=element.get('processingTime',{})                                     #It creates a variable that gets the element attribute 'processingTime'
        
    if name =='Machine1':                                                               #It checks using if...elif syntax if the name is 'Machine1', so the first machine in the Topology10
        processingTime['distributionType']=str(names[0])                                #It changes the attribute's ('distributionType') name, putting the name of the distribution (e.g. in Normal distribution that will be Normal) 
        processingTime[str(aParameters[0])]=str(aParameterValue[0])                     # It adds a new attribute in the JSON file with the name of the first argument in aParameter's list (e.g. in Normal that will be the mean), putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 7.0)
        processingTime[str(bParameters[0])]=str(bParameterValue[0])                     # It adds a new attribute in the JSON file with the name of the second argument in aParameter's list (e.g. in Normal that will be the standarddeviation), putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 7.0)
    elif name=='Machine2':
        processingTime['distributionType']=str(names[1])
        processingTime[str(aParameters[1])]=str(aParameterValue[1])
        processingTime[str(bParameters[1])]=str(bParameterValue[1])
    else:
        continue               
        
    jsonFile = open('JSON_Topology10.json',"w")     #It opens the JSON file
    jsonFile.write(json.dumps(data, indent=True))                                           #It writes the updated data to the JSON file 
    jsonFile.close()                                                                        #It closes the file
        
#================================ Calling the ExcelOutput object, outputs the outcomes of the statistical analysis in Excel files =============================================#
C=Output()
C.PrintDistributionFit(Machine1_OpearationTimes)   
C.PrintStatisticalMeasures(Machine1_OpearationTimes)

    