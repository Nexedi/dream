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

from Transformations import BasicTransformations
from DistributionFitting import Distributions
import ImportDatabase
from xml.etree import ElementTree as et
from Simul8XML import Simul8Output

#================================= Extract data from the database ==========================================#
#The Import Database object is used to import the data, the user has to specify the path to the file containing the connection data 
cnxn=ImportDatabase.ConnectionData(seekName='ServerData', implicitExt='txt', number_of_cursors=3)
cursors=cnxn.getCursors()
#Database queries used to extract the required data, in this example the processing times are given subtracting the TIME IN data point from the TIME OUT data point
a = cursors[0].execute("""
        select prod_code, stat_code,emp_no, TIMEIN, TIMEOUT
        from production_status
                """)
MILL1=[] #Initialization of MILL1 list
MILL2=[] #Initialization of MILL2 list
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
#The  BasicTransformations object is called to conduct some data transformations     
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
#Database queries used again to extract the MTTF and MTTR data points
b = cursors[1].execute("""
        select stat_code, MTTF_hour
        from failures
                """)

c = cursors[2].execute("""
        select stat_code, MTTR_hour
        from repairs
                """)         
MTTF_MILL1=[] #Initialization of the list that will contain the MTTF data points for MILL1  
MTTF_MILL2=[] #Initialization of the list that will contain the MTTF data points for MILL2
for j in range(b.rowcount):
    #get the next line
    ind2=b.fetchone() 
    if ind2.stat_code == 'MILL1':
        MTTF_MILL1.append(ind2.MTTF_hour)
    elif ind2.stat_code == 'MILL2':
        MTTF_MILL2.append(ind2.MTTF_hour)
    else:
        continue

MTTR_MILL1=[] #Initialization of the list that will contain the MTTR data points for MILL1 
MTTR_MILL2=[] #Initialization of the list that will contain the MTTR data points for MILL1 
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
#The Distributions object is called to fit statistical distributions to the in scope data
dist_proctime = Distributions() 
distProcTime_MILL1 = dist_proctime.Lognormal_distrfit(procTime_MILL1)
distProcTime_MILL2 = dist_proctime.Weibull_distrfit(procTime_MILL2)

dist_MTTF = Distributions()
dist_MTTR = Distributions()
distMTTF_MILL1 = dist_MTTF.Exponential_distrfit(MTTF_MILL1)
distMTTF_MILL2 = dist_MTTF.Exponential_distrfit(MTTF_MILL2)

distMTTR_MILL1 = dist_MTTR.Normal_distrfit(MTTR_MILL1)
distMTTR_MILL2 = dist_MTTR.Normal_distrfit(MTTR_MILL2) 

#======================= Output preparation: output the updated values in the XML file of this example ================================#

datafile = ('ParallelStations.xml')  #define the input xml file
tree = et.parse(datafile) 
simul8 = Simul8Output()    #Call the Simul8Output object
#Assign the statistical distribution found above in the XML file using methods of the Simul8Output object
procTimes1 = simul8.ProcTimes(tree,'MILL1',distProcTime_MILL1)
procTimes2 = simul8.ProcTimes(procTimes1,'MILL2',distProcTime_MILL2)
#Again assign the MTTF and MTTR probability distributions calling the relevant methods from the Simul8Output object
MTTF1 = simul8.MTBF(procTimes2,'MILL1',distMTTF_MILL1)
MTTR1 = simul8.MTTR(MTTF1,'MILL1',distMTTR_MILL1)

MTTF2 = simul8.MTBF(MTTR1,'MILL2',distMTTF_MILL2)
MTTR2 = simul8.MTTR(MTTF2,'MILL2',distMTTR_MILL2)
#Output the XML file with the processed data 
output= MTTR2.write('KEtool_ParallelStations.xml')  


