'''
Created on 3 Dec 2014

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
from DistributionFitting import Distributions
import xlrd
from xml.etree import ElementTree as et
from Simul8XML import Simul8Output

#Read from the given directory the Excel document with the processing times data
workbook = xlrd.open_workbook('ProcData.xls')
worksheets = workbook.sheet_names()
worksheet_Proc = worksheets[0]     #Define the worksheet with the Processing time data

importData = Import_Excel()   #Call the Python object Import_Excel
procTimes = importData.Input_data(worksheet_Proc, workbook)   #Create the Processing times dictionary with key the M1 and values the processing time data

#Get from the above dictionaries the M1 key and the Source key and define the following lists with data
M1 = procTimes.get('M1',[])
      
distFitting = DistFittest()  #Call the DistFittest object
M1 = distFitting.ks_test(M1)

#Read from the given directory the Excel document with the inter-arrivals data
workbook = xlrd.open_workbook('InterarrivalsData.xls')
worksheets = workbook.sheet_names()
worksheet_Inter = worksheets[0]     #Define the worksheet with the Inter-arrivals time data

data = Import_Excel()
interTimes = data.Input_data(worksheet_Inter, workbook) #Create the Inter-arrival times dictionary with key the Source and values the inter-arrival time data

S1 = interTimes.get('Source',[])  

distMLE = Distributions() #Call the Distributions object
S1 = distMLE.Exponential_distrfit(S1)

datafile=('SingleServer.xml')  #define the input xml file
tree = et.parse(datafile) 
simul8 = Simul8Output()    #Call the Simul8Output object

title = 'KEtool_SingleServer'
interTimes = simul8.InterArrivalTime(tree,'Source', S1)
procTimes = simul8.ProcTimes(interTimes,'Activity 1', M1)
title = simul8.Title(procTimes,title)
#Output the XML file with the processed data
output= procTimes.write('KEtool_SingleServer.xml')



