'''
Created on 23 Sep 2014

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

#================= Main script of KE tool  =====================================#
from __future__ import division
from dream.KnowledgeExtraction.StatisticalMeasures import StatisticalMeasures
from dream.KnowledgeExtraction.DistributionFitting import Distributions
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.ReplaceMissingValues import ReplaceMissingValues
from dream.KnowledgeExtraction.ImportExceldata import ImportExceldata
from dream.KnowledgeExtraction.DetectOutliers import DetectOutliers
from JSONOutput import JSONOutput
from dream.KnowledgeExtraction.CMSDOutput import CMSDOutput
from xml.etree import ElementTree as et
from WIP_Identifier import currentWIP
import xlrd
from dateutil.parser import *
import datetime
from time import mktime
import dream.simulation.LineGenerationJSON as ManPyMain
# import dream.simulation.LineGenerationCMSD1 as ManPyMain
import json

#Read from the given directory the Excel document with the input data
workbook = xlrd.open_workbook('prod_data.xls')
worksheets = workbook.sheet_names()
main= workbook.sheet_by_name('Export Worksheet') 
worksheet_ProdData = worksheets[0]     #Define the worksheet with the production data

A=ImportExceldata()                              #Call the Python object Import_Excel
ProdData= A.Input_data(worksheet_ProdData, workbook)   #Create the Production data dictionary with keys the labels of Excel's different columns 

##Get from the ProdData dictionary the different keys and define the following lists 
contIds = ProdData.get('CONTAINERNAME',[])         
prodName = ProdData.get('PRODUCTNAME',[])
prodDesc= ProdData.get('PRODUCTDESCRIPTION',[])
taskdate= ProdData.get('TASKDATE',[])
taskName= ProdData.get('TASKTYPENAME',[])
statName= ProdData.get('STATIONNAME',[])
contQuant= ProdData.get('CONTAINERQTYATTXN',[])

# columns that are used (static)
CONTAINERNAME=0
PRODUCTNAME=1
PRODUCTDESCRIPTION=2
TASKDATE=3
STATIONNAME=5

# method that returns the processStory dictionary, which contains the production steps of the container ids
def contProcessStory(contId):
    processStory[contId]={}
    for sheet in workbook.sheets():
        if worksheet_ProdData:
            for i in range(1,main.nrows):
                if sheet.cell(i,0).value==contId:
                    stationName=sheet.cell(i,5).value
                    processStory[contId][stationName]=[]         
            for i in range(1,main.nrows):
                if sheet.cell(i,0).value==contId:
                    taskType=sheet.cell(i,4).value
                    stationName=sheet.cell(i,5).value
                    time=parse(sheet.cell(i,3).value)
                    contQuant=sheet.cell(i,6).value
                    if taskType=='Start Station' or taskType=='Finish Station':
                        processStory[contId][stationName].append([time, contQuant])
# method that returns the timestamps from the Excel document (real MES data) in a form that can be handled by the KE tool                                    
def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60  

# Creation of two dictionaries (processStory,contDetails ) and one list (contIds) 
processStory={} 
contDetails={}
contIds=[]
 
for sheet in workbook.sheets():
    if worksheet_ProdData:
        for i in range(1,main.nrows):
            Id=main.cell(i,CONTAINERNAME).value
            if not Id in contIds:
                contIds.append(Id)
            contDetails[Id]=[]
            prodId=main.cell(i,PRODUCTNAME).value
            prodDescName=main.cell(i,PRODUCTDESCRIPTION).value
            time=main.cell(i,TASKDATE).value
            statName=main.cell(i,STATIONNAME).value
            contDetails[Id].append(prodId)
            contDetails[Id].append(prodDescName)
            contDetails[Id].append(statName)
              
for elem in contIds:
    contProcessStory(elem)          
#Creation and initialization of dictionaries, one for each station with keys the static 'ProcTime' and 'ScrapQuant'
MA={}
MA['ProcTime']=[]
MA['ScrapQuant']=[]
M1A={}
M1A['ProcTime']=[]
M1A['ScrapQuant']=[]
M1B={}
M1B['ProcTime']=[]
M1B['ScrapQuant']=[]
M2A={}
M2A['ProcTime']=[]
M2A['ScrapQuant']=[]
M2B={}
M2B['ProcTime']=[]
M2B['ScrapQuant']=[]
M3A={}
M3A['ProcTime']=[]
M3A['ScrapQuant']=[]
M3B={}
M3B['ScrapQuant']=[]
M3B['ProcTime']=[]
MM={}
MM['ProcTime']=[]
MM['ScrapQuant']=[]
PrA={}
PrA['ProcTime']=[]
PrA['ScrapQuant']=[]
PrB={}
PrB['ProcTime']=[]
PrB['ScrapQuant']=[]
PaA={}
PaA['ProcTime']=[]
PaA['ScrapQuant']=[]
PaB={}
PaB['ProcTime']=[]
PaB['ScrapQuant']=[]

#Define the number of units for each batch
batchSize= 80
#With the following loop statement, the lists inside the dictionaries with the processing times and the scrap quantity for each station are created
for key in processStory.keys():
    for elem in processStory[key].keys():
        if elem=='MA':
            try: 
                t1= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr1=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                MA['ProcTime'].append(t1)
                MA['ScrapQuant'].append(scr1)
            except IndexError:
                continue
        elif elem=='M1A':
            try:
                t2= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr2=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                M1A['ProcTime'].append(t2)
                M1A['ScrapQuant'].append(scr2)
            except IndexError:
                continue
        elif elem=='M1B':
            try:
                t3= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr3=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                M1B['ProcTime'].append(t3)
                M1B['ScrapQuant'].append(scr3)
            except IndexError:
                continue
        elif elem=='M2A':
            try:
                t4= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr4=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                M2A['ProcTime'].append(t4)
                M2A['ScrapQuant'].append(scr4)
            except IndexError:
                continue
        elif elem=='M2B':
            try:
                t5= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr5=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                M2B['ProcTime'].append(t5)
                M2B['ScrapQuant'].append(scr5)
            except IndexError:
                continue
        elif elem=='M3A':
            try:
                t6= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr6=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                M3A['ProcTime'].append(t6)
                M3A['ScrapQuant'].append(scr6)
            except IndexError:
                continue
        elif elem=='M3B':
            try:
                t7= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr7=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                M3B['ProcTime'].append(t7)
                M3B['ScrapQuant'].append(scr7)
            except IndexError:
                continue
        elif elem=='MM':
            try:
                t8= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr8=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                MM['ProcTime'].append(t8)
                MM['ScrapQuant'].append(scr8)
            except IndexError:
                continue   
        elif elem=='PrA':
            try:
                t10= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr10=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PrA['ProcTime'].append(t10)
                PrA['ScrapQuant'].append(scr10)
            except IndexError:
                continue
        elif elem=='PrB':
            try:
                t11= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr11=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PrB['ProcTime'].append(t11)
                PrB['ScrapQuant'].append(scr11)
            except IndexError:
                continue
        elif elem=='PaA':
            try:
                t12= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr12=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PaA['ProcTime'].append(t12)
                PaA['ScrapQuant'].append(scr12)
            except IndexError:
                continue
        elif elem=='PaB':
            try:
                t13= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr13=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PaB['ProcTime'].append(t13)
                PaB['ScrapQuant'].append(scr13)
            except IndexError:
                continue

#Call the HandleMissingValues object and delete the missing values in the lists with the scrap quantity and processing times data 
B= ReplaceMissingValues()
MA_Scrap= B.DeleteMissingValue(MA.get('ScrapQuant',[]))
MA_Proc= B.DeleteMissingValue(MA.get('ProcTime',[]))
M1A_Scrap= B.DeleteMissingValue(M1A.get('ScrapQuant',[]))
M1A_Proc= B.DeleteMissingValue(M1A.get('ProcTime',[]))
M1B_Scrap= B.DeleteMissingValue(M1B.get('ScrapQuant',[]))
M1B_Proc= B.DeleteMissingValue(M1B.get('ProcTime',[]))
M2A_Scrap= B.DeleteMissingValue(M2A.get('ScrapQuant',[]))
M2A_Proc= B.DeleteMissingValue(M2A.get('ProcTime',[]))
M2B_Scrap= B.DeleteMissingValue(M2B.get('ScrapQuant',[]))
M2B_Proc= B.DeleteMissingValue(M2B.get('ProcTime',[]))
M3A_Scrap= B.DeleteMissingValue(M3A.get('ScrapQuant',[]))
M3A_Proc= B.DeleteMissingValue(M3A.get('ProcTime',[]))
M3B_Scrap= B.DeleteMissingValue(M3B.get('ScrapQuant',[]))
M3B_Proc= B.DeleteMissingValue(M3B.get('ProcTime',[]))
MM_Scrap= B.DeleteMissingValue(MM.get('ScrapQuant',[]))
MM_Proc= B.DeleteMissingValue(MM.get('ProcTime',[]))
PrA_Scrap= B.DeleteMissingValue(PrA.get('ScrapQuant',[]))
PrA_Proc= B.DeleteMissingValue(PrA.get('ProcTime',[]))
PrB_Scrap= B.DeleteMissingValue(PrB.get('ScrapQuant',[]))
PrB_Proc= B.DeleteMissingValue(PrB.get('ProcTime',[]))
PaA_Scrap= B.DeleteMissingValue(PaA.get('ScrapQuant',[]))
PaA_Proc= B.DeleteMissingValue(PaA.get('ProcTime',[]))
PaB_Scrap= B.DeleteMissingValue(PaB.get('ScrapQuant',[]))
PaB_Proc= B.DeleteMissingValue(PaB.get('ProcTime',[]))

#Call the HandleOutliers object and delete the outliers in the lists with the processing times data of each station
C= DetectOutliers()
MA_Proc= C.DeleteOutliers(MA_Proc)
M1A_Proc= C.DeleteOutliers(M1A_Proc)
M1B_Proc= C.DeleteOutliers(M1B_Proc)
M2A_Proc= C.DeleteOutliers(M2A_Proc)
M2B_Proc= C.DeleteOutliers(M2B_Proc)
M3A_Proc= C.DeleteOutliers(M3A_Proc)
M3B_Proc= C.DeleteOutliers(M3B_Proc)
MM_Proc= C.DeleteOutliers(MM_Proc)
PrA_Proc= C.DeleteOutliers(PrA_Proc)
PrB_Proc= C.DeleteOutliers(PrB_Proc)
PaA_Proc= C.DeleteOutliers(PaA_Proc)
PaB_Proc= C.DeleteOutliers(PaB_Proc)

#Call the BasicStatisticalMeasures object and calculate the mean value of the processing times for each station 
E= StatisticalMeasures()
meanMA_Proc= E.mean(MA_Proc)
meanM1A_Proc= E.mean(M1A_Proc)
meanM2A_Proc= E.mean(M2A_Proc)
meanM3A_Proc= E.mean(M3A_Proc)
meanM1B_Proc= E.mean(M1B_Proc)
meanM2B_Proc= E.mean(M2B_Proc)
meanM3B_Proc= E.mean(M3B_Proc)
meanMM_Proc= E.mean(MM_Proc)
meanPrA_Proc= E.mean(PrA_Proc)
meanPrB_Proc= E.mean(PrB_Proc)
meanPaA_Proc= E.mean(PaA_Proc)
meanPaB_Proc= E.mean(PaB_Proc)

stopTime= datetime.datetime(2014,3,27,8,40,00)   #Give the stop time, based on this the WIP levels in the assembly line are identified calling the WIP method 
WIP=currentWIP(processStory, stopTime) #Call the currentWIP method, giving as attributes the processStory dict and the stopTime
#With the loop statement in the outcome of the currentWIP method, which is a dictionary with the name WIP, with a series of calculations the units to be processed are calculated by the WIP batches in the stations   
for key in WIP.keys():
    try:
        if WIP[key][0]=='MA':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanMA_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='M1A':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanM1A_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='M2A':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanM2A_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='M3A':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanM3A_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='M1B':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanM1B_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='M2B':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanM2B_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='M3B':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanM3B_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='MM':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanMM_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='PrA':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanPrA_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='PrB':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanPrB_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='PaA':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanPaA_Proc))
            WIP[key].append(unitsToProcess)
        elif WIP[key][0]=='PaB':
            secs = WIP[key][1].total_seconds()
            minutes= int(secs / 60)
            unitsToProcess= round(batchSize - (minutes / meanPaB_Proc))
            WIP[key].append(unitsToProcess)
    except IndexError:
        continue

# Call the DistFittest object and conduct Kolmogorov-Smirnov distribution fitting test in the processing times lists of each station
D=DistFittest()
dictProc={} #Create a dictionary that holds the statistical distributions of the processing times of each station
dictProc['MA']= D.ks_test(MA_Proc)
dictProc['M1A']= D.ks_test(M1A_Proc)
dictProc['M1B']= D.ks_test(M1B_Proc)
dictProc['M2A']= D.ks_test(M2A_Proc)
dictProc['M2B']= D.ks_test(M2B_Proc)
dictProc['M3A']= D.ks_test(M3A_Proc)
dictProc['M3B']= D.ks_test(M3B_Proc)
dictProc['MM']= D.ks_test(MM_Proc)
dictProc['PrA']= D.ks_test(PrA_Proc)
dictProc['PrB']= D.ks_test(PrB_Proc)
dictProc['PaA']= D.ks_test(PaA_Proc)
dictProc['PaB']= D.ks_test(PaB_Proc)
#Call the Distributions object and fit (using the Maximum Likelihood Estimation) the lists with the scrap quantity into a discrete statistical distribution, i.e. Geometric distribution 
D=Distributions()
dictScrap={} #Create a dictionary that holds the Geometric, which is a discrete statistical distribution of the processing times of each station
dictScrap['MA']= D.Geometric_distrfit(MA_Scrap)
dictScrap['M1A']= D.Geometric_distrfit(M1A_Scrap)
dictScrap['M1B']= D.Geometric_distrfit(M1B_Scrap)
dictScrap['M2A']= D.Geometric_distrfit(M2A_Scrap)
dictScrap['M2B']= D.Geometric_distrfit(M2B_Scrap)
dictScrap['M3A']= D.Geometric_distrfit(M3A_Scrap)
dictScrap['M3B']= D.Geometric_distrfit(M3B_Scrap)
dictScrap['MM']= D.Geometric_distrfit(MM_Scrap)
dictScrap['PrA']= D.Geometric_distrfit(PrA_Scrap)
dictScrap['PrB']= D.Geometric_distrfit(PrB_Scrap)
dictScrap['PaA']= D.Geometric_distrfit(PaA_Scrap)
dictScrap['PaB']= D.Geometric_distrfit(PaB_Scrap)

#Call the CMSDOutput object giving as attributes the dictionaries with the processing times distributions and the scrap quantities distributions
tree = et.parse("CMSD_example.xml")                                               #This file will be parsed using the XML.ETREE Python library
exportCMSD=CMSDOutput()

procTime1=exportCMSD.ProcessingTimes(tree, 'P1', dictProc['M1A']) 
procTime2=exportCMSD.ProcessingTimes(procTime1, 'P4', dictProc['M1B'])
procTime3=exportCMSD.ProcessingTimes(procTime2, 'P2', dictProc['M2A'])
procTime4=exportCMSD.ProcessingTimes(procTime3, 'P5', dictProc['M2B'])
procTime5=exportCMSD.ProcessingTimes(procTime4, 'P3', dictProc['M3A'])
procTime6=exportCMSD.ProcessingTimes(procTime5, 'P6', dictProc['M3B'])
procTime7=exportCMSD.ProcessingTimes(procTime6, 'P7', dictProc['MM'])
procTime8=exportCMSD.ProcessingTimes(procTime7, 'P8', dictProc['PrA'])
procTime9=exportCMSD.ProcessingTimes(procTime8, 'P9', dictProc['PrB'])
procTime10=exportCMSD.ProcessingTimes(procTime9, 'P10', dictProc['PaA'])
procTime11=exportCMSD.ProcessingTimes(procTime10, 'P11', dictProc['PaB'])

scrapQuant1=exportCMSD.ScrapQuantity(procTime11, 'P1', dictScrap['M1A'])
scrapQuant2=exportCMSD.ScrapQuantity(scrapQuant1, 'P4', dictScrap['M1B'])
scrapQuant3=exportCMSD.ScrapQuantity(scrapQuant2, 'P2', dictScrap['M2A'])
scrapQuant4=exportCMSD.ScrapQuantity(scrapQuant3, 'P5', dictScrap['M2B'])
scrapQuant5=exportCMSD.ScrapQuantity(scrapQuant4, 'P3', dictScrap['M3A'])
scrapQuant6=exportCMSD.ScrapQuantity(scrapQuant5, 'P6', dictScrap['M3B'])
scrapQuant7=exportCMSD.ScrapQuantity(scrapQuant6, 'P7', dictScrap['MM'])
scrapQuant8=exportCMSD.ScrapQuantity(scrapQuant7, 'P8', dictScrap['PrA'])
scrapQuant9=exportCMSD.ScrapQuantity(scrapQuant8, 'P9', dictScrap['PrB'])
scrapQuant10=exportCMSD.ScrapQuantity(scrapQuant9, 'P10', dictScrap['PaA'])
scrapQuant11=exportCMSD.ScrapQuantity(scrapQuant10, 'P11', dictScrap['PaA'])

scrapQuant11.write('CMSD_example_Output.xml',encoding="utf8")

data1 = open('CMSD_example_Output.xml','r')
#Call the JSONOutput object giving as attributes the dictionaries with the processing times distributions and the scrap quantities distributions and the WIP levels in the assembly line
exportJSON=JSONOutput()
data2 = exportJSON.JSONOutput(dictProc,dictScrap,WIP)

simulationOutput=ManPyMain.main(input_data=str(data2))
# simulationOutput=ManPyMain.main(input_data=data1)
    # save the simulation output
jsonFile = open('ManPyOutput.json',"w")     #It opens the JSON file
jsonFile.write(simulationOutput)           #It writes the updated data to the JSON file 
jsonFile.close()                         #It closes the file