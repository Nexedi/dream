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

from dream.KnowledgeExtraction.ImportExceldata import ImportExceldata
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.ExcelOutput import ExcelOutput
from dream.KnowledgeExtraction.JSONOutput import JSONOutput
from dream.KnowledgeExtraction.ReplaceMissingValues import ReplaceMissingValues
import dream.simulation.LineGenerationJSON as ManPyMain #import ManPy main JSON script
from xml.etree import ElementTree as et
from dream.KnowledgeExtraction.CMSDOutput import CMSDOutput
import xlrd
import json
import os

#================================================ This script is a simple example of the Knowledge extraction tool ===============================================================#

#The following is the Main script, that calls two Python objects in order to conduct the three main components of the Knowledge extraction tool
#In the following example the operation times of the topology's two machines are given in an Excel document. 
#Import_Excel object imports data from the Excel document to the tool and DistFittest object fits the data to a statistical distribution using Kolmogorov-Smirnov test
    
def main(test=0, ExcelFileName='inputsTwoServers.xls',
                JSONFileName='JSON_TwoServers.json',
                CMSDFileName='CMSD_TwoServers.xml',
                workbook=None,
                jsonFile=None, cmsdFile=None):
    if not workbook:
        workbook = xlrd.open_workbook(os.path.join(os.path.dirname(os.path.realpath(__file__)), ExcelFileName))      #Using xlrd library opens the Excel document with the input data      
    worksheets = workbook.sheet_names()
    worksheet_OperationTime = worksheets[0]             #It creates a variable that holds the first Excel worksheet 
     
    X=ImportExceldata()                                    #Call the import_Excel object
    OperationTimes= X.Input_data(worksheet_OperationTime,workbook)      #It defines a Python dictionary, giving as name OpearationTimes and as value the returned dictionary from the import_Excel object 
    Machine1_OpearationTimes = OperationTimes.get('Machine1',[])        #Two lists are defined (Machine1_OpearationTimes, Machine2_OpearationTimes) with the operation times data of each machine
    Machine2_OpearationTimes = OperationTimes.get('Machine2',[])
    
    A=ReplaceMissingValues()                                     #Call the HandleMissingValues object
    Machine1_OpearationTimes= A.DeleteMissingValue(Machine1_OpearationTimes)        #It deletes the missing values in the lists with the operation times data
    Machine2_OpearationTimes= A.DeleteMissingValue(Machine2_OpearationTimes)
    
    Dict={}
    B=DistFittest()                                     #It calls the DistFittest object
    Dict['M1']=B.ks_test(Machine1_OpearationTimes)                 #It conducts the Kolmogorov-Smirnov test in the list with the operation times data 
    Dict['M2']=B.ks_test(Machine2_OpearationTimes)
    M1=Dict.get('M1')
    M2=Dict.get('M2')
        
    #==================================== Output preparation: output the updated values in the CMSD information model ====================================================#
    if not cmsdFile:
        datafile=(os.path.join(os.path.dirname(os.path.realpath(__file__)), CMSDFileName))       #It defines the name or the directory of the XML file that is manually written the CMSD information model
        tree = et.parse(datafile)                                               #This file will be parsed using the XML.ETREE Python library
    
    exportCMSD=CMSDOutput()
    stationId1='A020'
    stationId2='A040'
    procTime1=exportCMSD.ProcessingTimes(tree, stationId1, M1) 
    procTime2=exportCMSD.ProcessingTimes(procTime1, stationId2, M2)
    
    procTime2.write('CMSD_TwoServers_Output.xml',encoding="utf8")                         #It writes the element tree to a specified file, using the 'utf8' output encoding
    #================================= Output preparation: output the updated values in the JSON file of Topology10 =========================================================#
    if not jsonFile:
        jsonFile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), JSONFileName),'r')      #It opens the JSON file 
        data = json.load(jsonFile)             #It loads the file
        jsonFile.close()
    else:
        data = json.load(jsonFile) 
    
    exportJSON=JSONOutput()
    stationId1='M1'
    stationId2='M2'
    data=exportJSON.ProcessingTimes(data, stationId1, M1)                           
    data1=exportJSON.ProcessingTimes(data, stationId2, M2)         
    
    #================================ Call ManPy and run the simulation model =============================================#
    #calls ManPy main script with the input
    simulationOutput=ManPyMain.main(input_data=json.dumps(data1))
    
    # if we run from test return the ManPy result
    if test:
        return simulationOutput
    
    #=================== Ouput the JSON file ==========================#
    jsonFile = open('JSON_TwoServers_Output.json',"w")     #It opens the JSON file
    jsonFile.write(json.dumps(data1, indent=True))                                           #It writes the updated data to the JSON file 
    jsonFile.close()                                                                        #It closes the file
        
    #================================ Calling the ExcelOutput object, outputs the outcomes of the statistical analysis in Excel files =============================================#
    C=ExcelOutput()
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

if __name__ == '__main__':
    main()    