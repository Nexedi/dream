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
Created on 4 Nov 2013

@author: George 
'''
'''
auxiliary script to handle excel related methods
'''


from Globals import G

import xlwt
import xlrd

def outputTrace(fileName='Trace'):
    G.traceFile.save(str(fileName)+'.xls')
    G.traceIndex=0    #index that shows in what row we are
    G.sheetIndex=1    #index that shows in what sheet we are
    G.traceFile = xlwt.Workbook()     #create excel file
    G.traceSheet = G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)  #create excel sheet 