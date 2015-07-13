# ===========================================================================
# Copyright 2015 Dublin City University
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
Created on 30 Jan 2015

@author: Anna
'''

from Globals import G
from numpy import array, mean, std, absolute

def utilisationCalc1(ACOcapacityDict, initialWeek, ind):
#==============================================   
# calculate min and target utilisation metrics
#==============================================

# min utilisation
# for weeks including the demand week and earlier weeks boolean variables are created for each bottleneck
# 1 if the min target has been reached 0 otherwise
# the boolean variables are averaged across the weeks for each bottleneck and the sum is returned    

# target utilisation
# for weeks including the demand week and earlier weeks 
# the quadratic distance from target utilisation is calculated and divided by the target utilisation 
# for each bottleneck the mean value is calculated (across weeks)
# the global mean (across bottlenecks) is returned

    minUtil = []
    targetUtil = []   
    for bottleneck in G.Bottlenecks:
        weekList = [initialWeek] + [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
        minU = []
        targetU = []
        for week in weekList:
            utilisation = float(G.Capacity[bottleneck][week]['OriginalCapacity']-ACOcapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity'] 
            minU.append(utilisation > G.Capacity[bottleneck][week]['minUtilisation'])
            if G.Capacity[bottleneck][week]['targetUtilisation']:
                targetU.append(float(utilisation - G.Capacity[bottleneck][week]['targetUtilisation'])/G.Capacity[bottleneck][week]['targetUtilisation'])
            else:
                targetU.append(float(utilisation - G.Capacity[bottleneck][week]['targetUtilisation']))
            
        minUtil.append(mean(array(minU)))
        targetUtil.append(mean(absolute(targetU)))
        
    ACOtargetUtil = mean(array(targetUtil))    #mean(array(targetUtil)) #FIXME: potrebbe essere std(array(targetUtil))
    ACOminUtil = mean(array(minUtil))*-1
    
    return ACOtargetUtil, ACOminUtil



def utilisationCalc2(ACOcapacityDict, initialWeek, ind):
#==============================================   
# calculate min and target utilisation metrics
#==============================================
# similar to chosenMA logic

    minUtil = []
    targetUtil = []   
    for bottleneck in G.Bottlenecks:
        weekList = [initialWeek] #+ [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
        for week in weekList:
            utilisation = float(G.Capacity[bottleneck][week]['OriginalCapacity']-ACOcapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity'] 
            minUtil.append(utilisation > G.Capacity[bottleneck][week]['minUtilisation'])
            if G.Capacity[bottleneck][week]['targetUtilisation']:
                targetUtil.append(float(utilisation - G.Capacity[bottleneck][week]['targetUtilisation'])/G.Capacity[bottleneck][week]['targetUtilisation'])
            else:                
                targetUtil.append(float(utilisation - G.Capacity[bottleneck][week]['targetUtilisation']))
            
    ACOtargetUtil = std(array(targetUtil))
    ACOminUtil = mean(array(minUtil))*-1
    
    return ACOtargetUtil, ACOminUtil


def utilisationCalc3(ACOcapacityDict, initialWeek, ind):
#==============================================   
# calculate min and target utilisation metrics
#==============================================
# targetUtil = max avg utilisation
# minUtil = avgUtilisation  

    minUtil = []
    targetUtil = []   
    for bottleneck in G.Bottlenecks:
        weekList = [initialWeek] #+ [G.WeekList[i] for i in range(ind-1, max(-1,ind-G.maxEarliness-1), -1)]
        minU = []
        targetU = []
        for week in weekList:
            utilisation = float(G.Capacity[bottleneck][week]['OriginalCapacity']-ACOcapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity'] 
            minU.append(utilisation)
            if G.Capacity[bottleneck][week]['targetUtilisation']:
                targetU.append(float(utilisation - G.Capacity[bottleneck][week]['targetUtilisation'])/G.Capacity[bottleneck][week]['targetUtilisation'])  
            else:
                targetU.append(float(utilisation - G.Capacity[bottleneck][week]['targetUtilisation']))  
            
        minUtil.append(mean(array(minU)))
        targetUtil.append(mean(array(max(minU))))
        
    ACOtargetUtil = max(targetUtil)
    ACOminUtil = mean(array(minUtil))   #FIXME: considerare piu settimane in weeklist e std(targetUtil)
    
    return ACOtargetUtil, ACOminUtil