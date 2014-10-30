'''
Created on 9 Oct 2014

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

import datetime
import operator

# This method that returns the actual WIP (Work-In-Process containers ids) either in stations or buffers of the production line
def currentWIP(processStory, stopTime):
    Stations={}
    LastStation={}
    for key in processStory.keys():
        Stations[key]=[]
        LastStation[key]=[]
        sorted_proc=sorted(processStory[key].iteritems(), key=operator.itemgetter(1))
        for i in range(len(sorted_proc)):
            Stations[key].append(sorted_proc[i])
        for key in Stations.keys():
            for elem in range(len(Stations[key])):
                try:
                    if Stations[key][elem][1][0][0] > stopTime and Stations[key][elem][1][1][0] > stopTime: 
                        del Stations[key][elem]
                    elif Stations[key][elem][1][1][0] > stopTime:
                        del Stations[key][elem][1][1]
                    elif Stations[key][elem][1][0][0] > stopTime:
                        del Stations[key][elem][1][0]    
                except IndexError:
                    continue
                try:
                    LastStation[key]=Stations[key][-1]
                except KeyError:
                    continue            
    for key in LastStation.keys():  
        try:
            if (LastStation[key][0]=='PaA' or LastStation[key][0]=='PaB') and (stopTime - LastStation[key][1][0][0] > datetime.timedelta(0,500)):
                del LastStation[key]
        except IndexError:
            continue           
    WIP={}
    for key in LastStation.keys():
        WIP[key]=[]
        try:
            if not LastStation[key][1][1]:
                continue
        except IndexError:
            WIP[key].append(LastStation[key][0])
            try:
                dif= stopTime - LastStation[key][1][0][0]
                WIP[key].append(dif)    
            except IndexError:
                continue
    for key in LastStation.keys():      
        try:
            if LastStation[key][0]=='MA' and LastStation[key][1][1]:
                WIP[key].append('QStart')
            elif LastStation[key][0]=='M1A' and LastStation[key][1][1]:
                WIP[key].append('Q2A')
            elif LastStation[key][0]=='M1B' and LastStation[key][1][1]:
                WIP[key].append('Q2B')
            elif LastStation[key][0]=='M2A' and LastStation[key][1][1]:
                WIP[key].append('Q3A')
            elif LastStation[key][0]=='M2B' and LastStation[key][1][1]:
                WIP[key].append('Q3B')
            elif (LastStation[key][0]=='M3A' or LastStation[key][0]=='M3B') and LastStation[key][1][1]:
                WIP[key].append('QM')
            elif LastStation[key][0]=='MM' and LastStation[key][1][1]:
                WIP[key].append('QPr')
            elif (LastStation[key][0]=='PrA' and LastStation[key][1][1]) or (LastStation[key][0]=='PrB' and LastStation[key][1][1]):
                WIP[key].append('QPa')
        except IndexError:
            continue
        return WIP          