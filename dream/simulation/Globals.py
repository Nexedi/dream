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
Created on 8 Nov 2012

@author: George
'''
'''
carries some global variables
'''

from SimPy.Simulation import *
from Machine import Machine
from Queue import Queue
from Repairman import Repairman
import xlwt
import xlrd
from random import Random, expovariate, gammavariate, normalvariate

# globals
class G:   
    seed=1450    #the seed of the random number generator
    Rnd = Random(seed)  #random number generator
    

    ObjList=[]          #a list that holds all the simulation objects 
    
    numberOfReplications=1  #the number of replications default=1
    confidenceLevel=0.9       #the confidence level default=90%
    Base=1                  #the Base time unit. Default =1 minute
    maxSimTime=0            #the total simulation time
    
    #data for the trace output in excel
    trace=""        #this is written from input. If it is "Yes" then you write to trace, else we do not
    traceIndex=0    #index that shows in what row we are
    sheetIndex=1    #index that shows in what sheet we are
    traceFile = xlwt.Workbook()     #create excel file
    traceSheet = traceFile.add_sheet('sheet '+str(sheetIndex), cell_overwrite_ok=True)  #create excel sheet    
    
    
    #variables for excel output
    outputIndex=0    #index that shows in what row we are
    sheetIndex=1    #index that shows in what sheet we are
    outputFile = xlwt.Workbook()     #create excel file
    outputSheet = outputFile.add_sheet('sheet '+str(sheetIndex), cell_overwrite_ok=True)  #create excel sheet
    
    #variables for json output
    outputJSON={}
    outputJSONFile=None
    
