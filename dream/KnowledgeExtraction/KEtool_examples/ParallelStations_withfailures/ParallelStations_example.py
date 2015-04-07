'''
Created on 15 Jun 2014

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

from dream.KnowledgeExtraction.Transformations import BasicTransformations
from dream.KnowledgeExtraction.DistributionFitting import DistFittest
from dream.KnowledgeExtraction.DistributionFitting import Distributions
from dream.KnowledgeExtraction.ExcelOutput import Output
from dream.KnowledgeExtraction.JSONOutput import JSONOutput
from dream.KnowledgeExtraction.ImportDatabase import ConnectionData
from xml.etree import ElementTree as et
from dream.KnowledgeExtraction.CMSDOutput import CMSDOutput
import json
import os
#================================= Extract data from the database ==========================================#
def main(test=0, JSONFileName='JSON_example.json',
                CMSDFileName='CMSD_ParallelStations.xml',
                DBFilePath = 'C:\Users\Panos\Documents\KE tool_documentation',
                file_path=None,
                jsonFile=None, cmsdFile=None):
    if not file_path:
        cnxn=ConnectionData(seekName='ServerData', file_path=DBFilePath, implicitExt='txt', number_of_cursors=3)
        cursors=cnxn.getCursors()
    
    a = cursors[0].execute("""
            select prod_code, stat_code,emp_no, TIMEIN, TIMEOUT
            from production_status
                    """)
    MILL1=[]
    MILL2=[]
    for j in range(a.rowcount):
        #get the next line
        ind1=a.fetchone() 
        if ind1.stat_code == 'MILL1':
            procTime=[]
            procTime.insert(0,ind1.TIMEIN)
            procTime.insert(1,ind1.TIMEOUT)
            MILL1.append(procTime)
        elif ind1.stat_code == 'MILL2':
            procTime=[]
            procTime.insert(0,ind1.TIMEIN)
            procTime.insert(1,ind1.TIMEOUT)
            MILL2.append(procTime)
        else:
            continue
        
    transform = BasicTransformations()
    procTime_MILL1=[]
    for elem in MILL1:
        t1=[]
        t2=[]
        t1.append(((elem[0].hour)*60)*60 + (elem[0].minute)*60 + elem[0].second)
        t2.append(((elem[1].hour)*60)*60 + (elem[1].minute)*60 + elem[1].second)
        dt=transform.subtraction(t2, t1)
        procTime_MILL1.append(dt[0])
    
    procTime_MILL2=[]
    for elem in MILL2:
        t1=[]
        t2=[]
        t1.append(((elem[0].hour)*60)*60 + (elem[0].minute)*60 + elem[0].second)
        t2.append(((elem[1].hour)*60)*60 + (elem[1].minute)*60 + elem[1].second)
        dt=transform.subtraction(t2, t1)
        procTime_MILL2.append(dt[0])
    
    
    b = cursors[1].execute("""
            select stat_code, MTTF_hour
            from failures
                    """)
    
    c = cursors[2].execute("""
            select stat_code, MTTR_hour
            from repairs
                    """)         
    MTTF_MILL1=[]
    MTTF_MILL2=[]
    for j in range(b.rowcount):
        #get the next line
        ind2=b.fetchone() 
        if ind2.stat_code == 'MILL1':
            MTTF_MILL1.append(ind2.MTTF_hour)
        elif ind2.stat_code == 'MILL2':
            MTTF_MILL2.append(ind2.MTTF_hour)
        else:
            continue
    
    MTTR_MILL1=[]
    MTTR_MILL2=[]
    for j in range(c.rowcount):
        #get the next line
        ind3=c.fetchone() 
        if ind3.stat_code == 'MILL1':
            MTTR_MILL1.append(ind3.MTTR_hour)
        elif ind3.stat_code == 'MILL2':
            MTTR_MILL2.append(ind3.MTTR_hour)
        else:
            continue
    
    #======================= Fit data to statistical distributions ================================#
    dist_proctime = DistFittest()
    distProcTime_MILL1 = dist_proctime.ks_test(procTime_MILL1)
    distProcTime_MILL2 = dist_proctime.ks_test(procTime_MILL2)
    
    dist_MTTF = Distributions()
    dist_MTTR = Distributions()
    distMTTF_MILL1 = dist_MTTF.Weibull_distrfit(MTTF_MILL1)
    distMTTF_MILL2 = dist_MTTF.Weibull_distrfit(MTTF_MILL2)
    
    distMTTR_MILL1 = dist_MTTR.Poisson_distrfit(MTTR_MILL1)
    distMTTR_MILL2 = dist_MTTR.Poisson_distrfit(MTTR_MILL2)
    
    #======================== Output preparation: output the values prepared in the CMSD information model of this model ====================================================#
    if not cmsdFile:
        datafile=(os.path.join(os.path.dirname(os.path.realpath(__file__)), CMSDFileName))       #It defines the name or the directory of the XML file that is manually written the CMSD information model
        tree = et.parse(datafile)                                               #This file will be parsed using the XML.ETREE Python library
    
    exportCMSD=CMSDOutput()
    stationId1='M1'
    stationId2='M2'
    procTime1=exportCMSD.ProcessingTimes(tree, stationId1, distProcTime_MILL1) 
    procTime2=exportCMSD.ProcessingTimes(procTime1, stationId2, distProcTime_MILL2)
    
    TTF1=exportCMSD.TTF(procTime2, stationId1, distMTTF_MILL1)
    TTR1=exportCMSD.TTR(TTF1, stationId1, distMTTR_MILL1)
    
    TTF2=exportCMSD.TTF(TTR1, stationId2, distMTTF_MILL2)
    TTR2=exportCMSD.TTR(TTF2, stationId2, distMTTR_MILL2)
    
    TTR2.write('CMSD_ParallelStations_Output.xml',encoding="utf8")                         #It writes the element tree to a specified file, using the 'utf8' output encoding
    
    #======================= Output preparation: output the updated values in the JSON file of this example ================================#
    if not jsonFile:
        jsonFile = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), JSONFileName),'r')      #It opens the JSON file 
        data = json.load(jsonFile)             #It loads the file
        jsonFile.close()
    else:
        data = json.load(jsonFile) 
    
    exportJSON=JSONOutput()
    stationId1='M1'
    stationId2='M2'
    data1=exportJSON.ProcessingTimes(data, stationId1, distProcTime_MILL1)
    data2=exportJSON.ProcessingTimes(data1, stationId2, distProcTime_MILL2)
    
    data3=exportJSON.TTF(data2, stationId1, distMTTF_MILL1)
    data4=exportJSON.TTR(data3, stationId1, distMTTR_MILL1)
    
    data5=exportJSON.TTF(data4, stationId2, distMTTF_MILL2)
    data6=exportJSON.TTR(data5, stationId2, distMTTR_MILL2)
    
    # if we run from test return the data6
    if test:
        return data6
        
    jsonFile = open('JSON_ParallelStations_Output.json',"w")     #It opens the JSON file
    jsonFile.write(json.dumps(data6, indent=True))               #It writes the updated data to the JSON file 
    jsonFile.close()                                             #It closes the file
    
    #=================== Calling the ExcelOutput object, outputs the outcomes of the statistical analysis in xls files ==========================#
    export=Output()
    
    export.PrintStatisticalMeasures(procTime_MILL1,'procTimeMILL1_StatResults.xls')   
    export.PrintStatisticalMeasures(procTime_MILL2,'procTimeMILL2_StatResults.xls')
    export.PrintStatisticalMeasures(MTTF_MILL1,'MTTFMILL1_StatResults.xls')   
    export.PrintStatisticalMeasures(MTTF_MILL2,'MTTFMILL2_StatResults.xls')
    export.PrintStatisticalMeasures(MTTR_MILL1,'MTTRMILL1_StatResults.xls')   
    export.PrintStatisticalMeasures(MTTR_MILL2,'MTTRMILL2_StatResults.xls')
    
    export.PrintDistributionFit(procTime_MILL1,'procTimeMILL1_DistFitResults.xls')
    export.PrintDistributionFit(procTime_MILL2,'procTimeMILL2_DistFitResults.xls')
    export.PrintDistributionFit(MTTF_MILL1,'MTTFMILL1_DistFitResults.xls')
    export.PrintDistributionFit(MTTF_MILL2,'MTTFMILL2_DistFitResults.xls')
    export.PrintDistributionFit(MTTR_MILL1,'MTTRMILL1_DistFitResults.xls')
    export.PrintDistributionFit(MTTR_MILL2,'MTTRMILL2_DistFitResults.xls')

if __name__ == '__main__':
    main() 
