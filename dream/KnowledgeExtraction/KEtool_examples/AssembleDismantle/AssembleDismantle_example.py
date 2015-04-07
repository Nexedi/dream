'''
Created on 12 Jun 2014

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
from dream.KnowledgeExtraction.ReplaceMissingValues import HandleMissingValues
from dream.KnowledgeExtraction.DistributionFitting import Distributions
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.ExcelOutput import Output
from dream.KnowledgeExtraction.JSONOutput import JSONOutput
import dream.simulation.LineGenerationJSON as ManPyMain #import ManPy main JSON script
import xlrd
import json
import os

def main(test=0, ExcelFileName='inputData.xls',
                JSONFileName='JSON_AssembleDismantle.json',
                workbook=None,
                jsonFile=None):
    if not workbook:
        workbook = xlrd.open_workbook(os.path.join(os.path.dirname(os.path.realpath(__file__)), ExcelFileName))
    #Read from the given directory the Excel document with the input data
    worksheets = workbook.sheet_names()
    worksheet_ProcessingTimes = worksheets[0]     #Define the worksheet with the Processing times data
    worksheet_MTTF = worksheets[1]       #Define the worksheet with Time-to-Failure data
    worksheet_MTTR = worksheets[2]       #Define the worksheet with Time-to-Repair data
    
    A = Import_Excel()                              #Call the Python object Import_Excel
    ProcessingTimes = A.Input_data(worksheet_ProcessingTimes, workbook)   #Create the Processing Times dictionary with key the Machine 1 and values the processing time data
    MTTF=A.Input_data(worksheet_MTTF, workbook)        #Create the MTTF dictionary with key the Machine 1 and time-to-failure data 
    MTTR=A.Input_data(worksheet_MTTR, workbook)        #Create the MTTR Quantity dictionary with key the Machine 1 and time-to-repair data 
    
    ##Get from the above dictionaries the M1 key and define the following lists with data 
    ProcTime = ProcessingTimes.get('M1',[])         
    MTTF = MTTF.get('M1',[])
    MTTR = MTTR.get('M1',[])
    
    #Call the HandleMissingValues object and replace the missing values in the lists with the mean of the non-missing values
    B =HandleMissingValues()
    ProcTime = B.ReplaceWithMean(ProcTime)
    MTTF = B.ReplaceWithMean(MTTF)
    MTTR = B.ReplaceWithMean(MTTR)
    
    C = Distributions()      #Call the Distributions object
    D = DistFittest()      #Call the DistFittest object
    
    ProcTime_dist = D.ks_test(ProcTime)
    MTTF_dist = C.Exponential_distrfit(MTTF)
    MTTR_dist = C.Exponential_distrfit(MTTR)
    #================================= Output preparation: output the updated values in the JSON file of this example =========================================================#
    if not jsonFile:
        jsonFile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), JSONFileName),'r')      #It opens the JSON file 
        data = json.load(jsonFile)             #It loads the file
        jsonFile.close()
    else:
        data = json.load(jsonFile) 
    
    exportJSON=JSONOutput()
    stationId='M1'
    data=exportJSON.ProcessingTimes(data, stationId, ProcTime_dist)
    data1=exportJSON.TTF(data, stationId, MTTF_dist)
    data2=exportJSON.TTR(data1, stationId, MTTR_dist)
    
    #================================ Call ManPy and run the simulation model =============================================#
    #calls ManPy main script with the input
    simulationOutput=ManPyMain.main(input_data=json.dumps(data2))
    
    # if we run from test return the ManPy result
    if test:
        return simulationOutput
    
    #===================== Output the JSON file ========================================#
    jsonFile = open('JSON_AssembleDismantle_Output.json',"w")     #It opens the JSON file
    jsonFile.write(json.dumps(data2, indent=True))                                           #It writes the updated data to the JSON file 
    jsonFile.close()                                                                        #It closes the file
    #================================ Calling the ExcelOutput object, outputs the outcomes of the statistical analysis in xls files =============================================#
    C=Output()
    C.PrintStatisticalMeasures(ProcTime,'ProcTime_StatResults.xls')   
    C.PrintStatisticalMeasures(MTTR,'MTTR_StatResults.xls')
    C.PrintStatisticalMeasures(MTTF,'MTTF_StatResults.xls')   
    C.PrintDistributionFit(ProcTime,'ProcTime_DistFitResults.xls')
    C.PrintDistributionFit(MTTR,'MTTR_DistFitResults.xls')
    
    #================================ Call ManPy and run the simulation model =============================================#
    #calls ManPy main script with the input
    simulationOutput=ManPyMain.main(input_data=json.dumps(data))
    # save the simulation output
    jsonFile = open('ManPyOutput.json',"w")     #It opens the JSON file
    jsonFile.write(simulationOutput)           #It writes the updated data to the JSON file 
    jsonFile.close()                         #It closes the file
    
if __name__ == '__main__':
    main()