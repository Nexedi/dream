'''
Created on 4 Dec 2014

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

from dream.KnowledgeExtraction.DistributionFitting import Distributions
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from xml.etree import ElementTree as et
from dream.KnowledgeExtraction.Simul8XML import Simul8Output
from dream.KnowledgeExtraction.ImportCSVdata import Import_CSV
from dream.KnowledgeExtraction.ImportExceldata import Import_Excel
import xlrd
import os

def main(test=0, ExcelFileName='DataSet.xlsx',
                CSVFileName='ProcTimesData.csv',
                simul8XMLFileName='Topology1.xml',
                workbook=None, csvFile=None, simul8XMLFile=None):
#================================= Extract the required data from the data files ==========================================#
    if csvFile:
        CSVFileName = csvFile.name    
    filename = CSVFileName
    csv = Import_CSV()   #call the Import_CSV module and using its method Input_data import the data set from the CSV file to the tool
    Data = csv.Input_data(filename)
    
    Activity2_Proc = Data.get('Activity 2',[])       #get from the returned Python dictionary the two data sets
    Activity3_Proc = Data.get('Activity 3',[])
    
    #Read from the given directory the Excel document with the data
    if not workbook:
        workbook = xlrd.open_workbook(os.path.join(os.path.dirname(os.path.realpath(__file__)), ExcelFileName))
    worksheets = workbook.sheet_names()
    worksheet_Inter = worksheets[0]     #Define the worksheet with the Inter-arrivals time data
    
    data = Import_Excel()
    interTimes = data.Input_data(worksheet_Inter, workbook) #Create the Inter-arrival times dictionary with key the Source and values the inter-arrival time data
    
    S1 = interTimes.get('Source',[])  
    
    #Read from the given directory the Excel document with the data
    worksheets = workbook.sheet_names()
    worksheet_Fail = worksheets[1]     #Define the worksheet with the failures data (MTTF,MTTR)
    
    data = Import_Excel()
    failures = data.Input_data(worksheet_Fail, workbook) #Create the failures dictionary with key the MTTF and MTTR data points
    
    MTTF = failures.get('MTTF',[])  
    MTTR = failures.get('MTTR',[])
    
    #======================= Fit data to probability distributions ================================#
    #The Distributions and DistFittest objects are called to fit statistical distributions to the in scope data 
    dist = Distributions()
    act2Proc = dist.Weibull_distrfit(Activity2_Proc)
    act3Proc = dist.Weibull_distrfit(Activity3_Proc)
    
    s1Times = dist.Exponential_distrfit(S1)
    
    distFit = DistFittest()
    act1MTTF = distFit.ks_test(MTTF)
    act1MTTR = distFit.ks_test(MTTR)
    
    #======================= Output preparation: output the updated values in the XML file of this example ================================#
    
    if not simul8XMLFile:
        datafile=(os.path.join(os.path.dirname(os.path.realpath(__file__)), simul8XMLFileName))       #It defines the name or the directory of the XML file 
        tree = et.parse(datafile)    
    else:
        datafile=simul8XMLFile
        tree = et.parse(datafile)
        
    simul8 = Simul8Output()    #Call the Simul8Output object
    #Assign the statistical distribution calculated above in the XML file using methods of the Simul8Output object
    interTimes = simul8.InterArrivalTime(tree,'Source', s1Times)
    
    procTimes2 = simul8.ProcTimes(interTimes,'Activity 2', act2Proc)
    procTimes3 = simul8.ProcTimes(procTimes2,'Activity 3', act3Proc)
    
    #Again assign the MTTF and MTTR probability distributions calling the relevant methods from the Simul8Output object
    MTTF1 = simul8.MTBF(procTimes3,'Activity 1', act1MTTF)
    MTTR1 = simul8.MTTR(MTTF1,'Activity 1', act1MTTR)
    #Output the XML file with the processed data 
    output= MTTR1.write('KEtool_Topology1.xml')
    
    if test:
        output=et.parse('KEtool_Topology1.xml')
        return output 

if __name__ == '__main__':
    main() 



