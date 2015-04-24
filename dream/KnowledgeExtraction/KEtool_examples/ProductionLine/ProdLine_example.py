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

from dream.KnowledgeExtraction.StatisticalMeasures import StatisticalMeasures
from dream.KnowledgeExtraction.DataManipulation import DataManipulation
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.DistributionFitting import Distributions
from CMSD_Output import CMSD_example
from JSON_Output import JSON_example
from dream.KnowledgeExtraction.ExcelOutput import ExcelOutput
from dream.KnowledgeExtraction.ReplaceMissingValues import ReplaceMissingValues
from dream.KnowledgeExtraction.ImportExceldata import ImportExceldata
import xlrd
#import ManPy main JSON script
import dream.simulation.LineGenerationJSON as ManPyMain 
#================= Main script of KE tool  =====================================#

#Read from the given directory the Excel document with the input data
workbook = xlrd.open_workbook('input_Data.xls')
worksheets = workbook.sheet_names()
worksheet_ProcessingTimes = worksheets[1]     #Define the worksheet with the Processing times data
worksheet_ScrapQuantity = worksheets[0]       #Define the worksheet with the Scrap Quantity data

A=ImportExceldata()                              #Call the Python object Import_Excel
ProcessingTimes= A.Input_data(worksheet_ProcessingTimes, workbook)   #Create the Processing Times dictionary with keys the different stations in the line and values the processing times of different batches in these stations
ScrapQuantity=A.Input_data(worksheet_ScrapQuantity, workbook)        #Create the Scrap Quantity dictionary with keys the different stations in the line and values the scrap quantity data of different batches in these stations

##Get from the Scrap Quantity dictionary the different keys and define the following lists with the scrap quantity data of the different stations in the topology
        
P1_Scrap= ScrapQuantity.get('P1',[])
P2_Scrap= ScrapQuantity.get('P2',[])
P3_Scrap= ScrapQuantity.get('P3',[])
P4_Scrap= ScrapQuantity.get('P4',[])
P5_Scrap= ScrapQuantity.get('P5',[])
P6_Scrap= ScrapQuantity.get('P6',[])
P7_Scrap= ScrapQuantity.get('P7',[]) 
P8_Scrap= ScrapQuantity.get('P8',[])
P9_Scrap= ScrapQuantity.get('P9',[])
P10_Scrap= ScrapQuantity.get('P10',[])
P11_Scrap= ScrapQuantity.get('P11',[])

##Get from the Processing times dictionary the different keys and define the following lists with the processing times data of the different stations in the topology 

P1_Proc= ProcessingTimes.get('P1',[])
P2_Proc= ProcessingTimes.get('P2',[])
P3_Proc= ProcessingTimes.get('P3',[])
P4_Proc= ProcessingTimes.get('P4',[])
P5_Proc= ProcessingTimes.get('P5',[])
P6_Proc= ProcessingTimes.get('P6',[])
P7_Proc= ProcessingTimes.get('P7',[])
P8_Proc= ProcessingTimes.get('P8',[])
P9_Proc= ProcessingTimes.get('P9',[])
P10_Proc= ProcessingTimes.get('P10',[])
P11_Proc= ProcessingTimes.get('P11',[])

#Call the HandleMissingValues object and replace with zero the missing values in the lists with the scrap quantity data 

B=ReplaceMissingValues()

P1_Scrap= B.ReplaceWithZero(P1_Scrap)
P2_Scrap= B.ReplaceWithZero(P2_Scrap)
P3_Scrap= B.ReplaceWithZero(P3_Scrap)
P4_Scrap= B.ReplaceWithZero(P4_Scrap)
P5_Scrap= B.ReplaceWithZero(P5_Scrap)
P6_Scrap= B.ReplaceWithZero(P6_Scrap)
P7_Scrap= B.ReplaceWithZero(P7_Scrap)
P8_Scrap= B.ReplaceWithZero(P8_Scrap)
P9_Scrap= B.ReplaceWithZero(P9_Scrap)
P10_Scrap= B.ReplaceWithZero(P10_Scrap)
P11_Scrap= B.ReplaceWithZero(P11_Scrap)

# #Call the BasicSatatisticalMeasures object 
C=StatisticalMeasures()
#Create a list with values the calculated mean value of scrap quantity on the different stations in the line
listScrap=[C.mean(P1_Scrap),C.mean(P2_Scrap),C.mean(P3_Scrap),C.mean(P4_Scrap),C.mean(P5_Scrap),C.mean(P6_Scrap),C.mean(P7_Scrap),C.mean(P8_Scrap),C.mean(P9_Scrap),C.mean(P10_Scrap), C.mean(P11_Scrap)] 
 
D= DataManipulation()
 
listScrap=D.round(listScrap)       #Round the mean values of the list so as to get integers

dictScrap={}
dictScrap['P1']= listScrap[0]
dictScrap['P2']= listScrap[1]
dictScrap['P3']= listScrap[2]
dictScrap['P4']= listScrap[3]
dictScrap['P5']= listScrap[4]
dictScrap['P6']= listScrap[5]
dictScrap['P7']= listScrap[6]
dictScrap['P8']= listScrap[7]
dictScrap['P9']= listScrap[8]
dictScrap['P10']= listScrap[9]
dictScrap['P11']= listScrap[10]

E= DistFittest()
dictProc={}
dictProc['P1']= E.ks_test(P1_Proc)
dictProc['P2']= E.ks_test(P2_Proc)
dictProc['P3']= E.ks_test(P3_Proc)
dictProc['P4']= E.ks_test(P4_Proc)
dictProc['P5']= E.ks_test(P5_Proc)
dictProc['P6']= E.ks_test(P6_Proc)
dictProc['P7']= E.ks_test(P7_Proc)
dictProc['P8']= E.ks_test(P8_Proc)
dictProc['P9']= E.ks_test(P9_Proc)
dictProc['P10']= E.ks_test(P10_Proc)
dictProc['P11']= E.ks_test(P11_Proc) 

F= ExcelOutput()
F.PrintDistributionFit(P2_Proc,"DistributionFittingResults_P2Proc.xls")
F.PrintStatisticalMeasures(P2_Proc, "StatisticalMeasuresResults_P2Proc.xls")

CMSD_example(dictProc,dictScrap)    #Print the CMSD document, calling the CMSD_example method with arguments the dictProc and dictScrap dictionaries
JSON_example(dictProc,dictScrap)    #Print the JSON file, calling the JSON_example method


#calls ManPy main script with the input
 
simulationOutput=ManPyMain.main(input_data=str((JSON_example(dictProc,dictScrap))))
# save the simulation output
jsonFile = open('ManPyOutput.json',"w")     #It opens the JSON file
jsonFile.write(simulationOutput)                                           #It writes the updated data to the JSON file 
jsonFile.close()                                                                        #It closes the file