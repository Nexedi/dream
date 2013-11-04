from Globals import G

import xlwt
import xlrd

def outputTrace(fileNumber=1):
    G.traceFile.save('trace'+str(fileNumber)+'.xls')
    G.traceIndex=0    #index that shows in what row we are
    G.sheetIndex=1    #index that shows in what sheet we are
    G.traceFile = xlwt.Workbook()     #create excel file
    G.traceSheet = G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)  #create excel sheet 