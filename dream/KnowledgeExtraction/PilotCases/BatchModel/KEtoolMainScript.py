'''
Created on 17 Apr 2015

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

from __future__ import division
from dream.KnowledgeExtraction.StatisticalMeasures import StatisticalMeasures
from dream.KnowledgeExtraction.DistributionFitting import Distributions
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.ReplaceMissingValues import ReplaceMissingValues
from dream.KnowledgeExtraction.ImportDatabase import ConnectionData
from dream.KnowledgeExtraction.DetectOutliers import DetectOutliers
from JSONOutput import JSONOutput
from dream.KnowledgeExtraction.CMSDOutput import CMSDOutput
from xml.etree import ElementTree as et
# from WIP_Identifier import currentWIP
import xlrd
from dateutil.parser import *
import datetime
from time import mktime

cnxn=ConnectionData(seekName='ServerData', file_path='C:\Users\Panos\Documents\DB_Approach\BatchModel', implicitExt='txt', number_of_cursors=3)
cursors=cnxn.getCursors()

mesExtract=cursors[0].execute("""
            select CONTAINERNAME, PRODUCTNAME, PRODUCTDESCRIPTION, TASKDATE, TASKTYPENAME, STATIONNAME, CONTAINERQTYATTXN, EMPLOYEENAME
            from mes2
                    """)

# method that returns the processStory dictionary, which contains the production steps of the container ids
def contProcessStory(contId):
    processStory[contId]={}
    mesExtract=cursors[0].execute("""
            select CONTAINERNAME, PRODUCTNAME, PRODUCTDESCRIPTION, TASKDATE, TASKTYPENAME, STATIONNAME, CONTAINERQTYATTXN, EMPLOYEENAME
            from mes2
                    """)
    for i in range(mesExtract.rowcount):
        ind1=mesExtract.fetchone()
        a= cursors[1].execute("""
            select CONTAINERNAME,STATIONNAME, TASKDATE, TASKTYPENAME, STATIONNAME, CONTAINERQTYATTXN 
            from mes2
                    """)
        for i in range(a.rowcount):
            ind2=a.fetchone()
            if ind2.CONTAINERNAME==contId:
                stationName=ind2.STATIONNAME
                processStory[contId][stationName]=[]         
        b= cursors[2].execute("""
            select CONTAINERNAME,STATIONNAME, TASKDATE, TASKTYPENAME, STATIONNAME, CONTAINERQTYATTXN 
            from mes2
                    """)
        for i in range(b.rowcount):
            ind3=b.fetchone()
            if ind3.CONTAINERNAME==contId:
                taskType=ind3.TASKTYPENAME
                stationName=ind3.STATIONNAME
                time=ind3.TASKDATE
                contQuant=ind3.CONTAINERQTYATTXN
                try:
                    if taskType=='Start Station' or taskType=='Finish Station':
                        processStory[contId][stationName].append([time, contQuant])
                except KeyError:
                    continue
# method that returns the timestamps from the Excel document (real MES data) in a form that can be handled by the KE tool                                    
def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60 

processStory={} 
contDetails={}
contIds=[]
for i in range(mesExtract.rowcount):
    ind1=mesExtract.fetchone()
    Id=ind1.CONTAINERNAME
    if not Id in contIds:
        contIds.append(Id)
    contDetails[Id]=[]
    prodId=ind1.PRODUCTNAME
    prodDescName=ind1.PRODUCTDESCRIPTION
    time=ind1.TASKDATE
    statName=ind1.STATIONNAME
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
CB={}
CB['ScrapQuant']=[]
CB['ProcTime']=[]
MM={}
MM['ProcTime']=[]
MM['ScrapQuant']=[]
FL={}
FL['ProcTime']=[]
FL['ScrapQuant']=[]
PrA={}
PrA['ProcTime']=[]
PrA['ScrapQuant']=[]
PrB={}
PrB['ProcTime']=[]
PrB['ScrapQuant']=[]
PaA={}
PaA['ProcTime']=[]
PaA['ScrapQuant']=[]
Pb={}
Pb['ProcTime']=[]
Pb['ScrapQuant']=[]

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
        elif elem=='CB':
            try:
                t8= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr8=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                CB['ProcTime'].append(t8)
                CB['ScrapQuant'].append(scr8)
            except IndexError:
                continue
        elif elem=='MM':
            try:
                t9= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr9=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                MM['ProcTime'].append(t9)
                MM['ScrapQuant'].append(scr9)
            except IndexError:
                continue
        elif elem=='FL':
            try:
                t10= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr10=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                FL['ProcTime'].append(t10)
                FL['ScrapQuant'].append(scr10)
            except IndexError:
                continue  
        elif elem=='PrA':
            try:
                t11= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr11=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PrA['ProcTime'].append(t11)
                PrA['ScrapQuant'].append(scr11)
            except IndexError:
                continue
        elif elem=='PrB':
            try:
                t12= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr12=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PrB['ProcTime'].append(t12)
                PrB['ScrapQuant'].append(scr12)
            except IndexError:
                continue
        elif elem=='PaA':
            try:
                t13= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr13=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                PaA['ProcTime'].append(t13)
                PaA['ScrapQuant'].append(scr13)
            except IndexError:
                continue
        elif elem=='Pb':
            try:
                t14= (((mktime(processStory[key][elem][1][0].timetuple()) - mktime(processStory[key][elem][0][0].timetuple())) / batchSize) / 60)
                scr14=processStory[key][elem][0][1]-processStory[key][elem][1][1]
                Pb['ProcTime'].append(t14)
                Pb['ScrapQuant'].append(scr14)
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
M3B_Scrap= B.DeleteMissingValue(M3B.get('ScrapQuant',[]))
CB_Proc= B.DeleteMissingValue(CB.get('ProcTime',[]))
CB_Scrap= B.DeleteMissingValue(CB.get('ScrapQuant',[]))
MM_Scrap= B.DeleteMissingValue(MM.get('ScrapQuant',[]))
MM_Proc= B.DeleteMissingValue(MM.get('ProcTime',[]))
FL_Proc= B.DeleteMissingValue(FL.get('ProcTime',[]))
FL_Scrap= B.DeleteMissingValue(FL.get('ScrapQuant',[]))
PrA_Scrap= B.DeleteMissingValue(PrA.get('ScrapQuant',[]))
PrA_Proc= B.DeleteMissingValue(PrA.get('ProcTime',[]))
PrB_Scrap= B.DeleteMissingValue(PrB.get('ScrapQuant',[]))
PrB_Proc= B.DeleteMissingValue(PrB.get('ProcTime',[]))
PaA_Scrap= B.DeleteMissingValue(PaA.get('ScrapQuant',[]))
PaA_Proc= B.DeleteMissingValue(PaA.get('ProcTime',[]))
Pb_Scrap= B.DeleteMissingValue(Pb.get('ScrapQuant',[]))
Pb_Proc= B.DeleteMissingValue(Pb.get('ProcTime',[]))

#Call the HandleOutliers object and delete the outliers in the lists with the processing times data of each station
C= DetectOutliers()
MA_Proc= C.DeleteOutliers(MA_Proc)
M1A_Proc= C.DeleteOutliers(M1A_Proc)
M1B_Proc= C.DeleteOutliers(M1B_Proc)
M2A_Proc= C.DeleteOutliers(M2A_Proc)
M2B_Proc= C.DeleteOutliers(M2B_Proc)
M3A_Proc= C.DeleteOutliers(M3A_Proc)
M3B_Proc= C.DeleteOutliers(M3B_Proc)
CB_Proc= C.DeleteOutliers(CB_Proc)
FL_Proc= C.DeleteOutliers(FL_Proc)
M3B_Proc= C.DeleteOutliers(M3B_Proc)
PrA_Proc= C.DeleteOutliers(PrA_Proc)
PrB_Proc= C.DeleteOutliers(PrB_Proc)
PaA_Proc= C.DeleteOutliers(PaA_Proc)
Pb_Proc= C.DeleteOutliers(Pb_Proc)
    
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
dictProc['CB']= D.ks_test(CB_Proc)
dictProc['MM']= D.ks_test(MM_Proc)
dictProc['FL']= D.ks_test(FL_Proc)
dictProc['PrA']= D.ks_test(PrA_Proc)
dictProc['PrB']= D.ks_test(PrB_Proc)
dictProc['PaA']= D.ks_test(PaA_Proc)
dictProc['Pb']= D.ks_test(Pb_Proc)

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
dictScrap['CB']= D.Geometric_distrfit(CB_Scrap)
dictScrap['MM']= D.Geometric_distrfit(MM_Scrap)
dictScrap['FL']= D.Geometric_distrfit(FL_Scrap)
dictScrap['PrA']= D.Geometric_distrfit(PrA_Scrap)
dictScrap['PrB']= D.Geometric_distrfit(PrB_Scrap)
dictScrap['PaA']= D.Geometric_distrfit(PaA_Scrap)
dictScrap['Pb']= D.Geometric_distrfit(Pb_Scrap)









