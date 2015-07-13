
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
Created on 22 Jun 2015

@author: Anna
'''

from AllocManagement_Hybrid import AllocManagement_Hybrid2, AllocManagement_Hybrid2_Forecast
from ImportInput import ImportInput
from outputResults import outputResults
from Globals import G, initialiseVar
import time
from numpy import mean, std, array, absolute
from operator import itemgetter

def main(input, algorithmAttributes):
  
    startTime = time.time()
    ver = ImportInput(input, algorithmAttributes)
    if ver == "stop":
        return   
    
    if G.ACO == "all":
        G.acoRange = [0,1]
        G.minRange = {0:[0,1],1:[0,1]}
    elif G.ACO == "1":
        G.acoRange = [1]
        G.minRange = {0:[0,1], 1:[G.minDeltaUt]}
    else:
        G.acoRange = [0]
        G.minRange = {0:[G.minDeltaUt]}

 
    for j in G.acoRange:
        for i in G.minRange[j]:            
            initialiseVar() 
            G.minDeltaUt = i
            G.ACO = j
            print 'start ACO', G.ACO, 'minDelta', G.minDeltaUt
            bestAnt = AllocManagement_Hybrid2(None)
            
            # salvare risultati
            G.Summary[(G.ACO,G.minDeltaUt)] = {'scenario':(G.ACO,G.minDeltaUt)}
            for key in G.LateMeasures.keys():
                if key == 'lateness' or key == 'earliness':
                    if len(G.LateMeasures[key]):
                        G.Summary[(G.ACO,G.minDeltaUt)][key] = mean(G.LateMeasures[key])
                    else:
                        G.Summary[(G.ACO,G.minDeltaUt)][key] = 0
                else:
                    G.Summary[(G.ACO,G.minDeltaUt)][key] = G.LateMeasures[key]
            utilisation = []
            targetUt = []
            for bottleneck in G.Bottlenecks:
                for week in G.WeekList:
                    utilisation.append(float(G.Capacity[bottleneck][week]['OriginalCapacity']-G.CurrentCapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity'])
                    if G.Capacity[bottleneck][week]['targetUtilisation']:
                        targetUt.append((G.Capacity[bottleneck][week]['targetUtilisation']-float(G.Capacity[bottleneck][week]['OriginalCapacity']-G.CurrentCapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity'])/G.Capacity[bottleneck][week]['targetUtilisation'])
                    else:
                        targetUt.append((G.Capacity[bottleneck][week]['targetUtilisation']-float(G.Capacity[bottleneck][week]['OriginalCapacity']-G.CurrentCapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity']))
            G.Summary[(G.ACO,G.minDeltaUt)]['utilisation'] = mean(array(utilisation))
            G.Summary[(G.ACO,G.minDeltaUt)]['targetM'] = mean(absolute(array(targetUt)))
            G.Summary[(G.ACO,G.minDeltaUt)]['targetStd'] = std(array(targetUt))
            if G.ACO:
                G.Summary[(G.ACO,G.minDeltaUt)]['ant'] = bestAnt
            else:
                G.Summary[(G.ACO,G.minDeltaUt)]['ant'] = None
            
            
    # selection
    listSummary = [G.Summary[item] for item in G.Summary.keys()]
    print 'list summary', listSummary
    listSummary = sorted(listSummary, key=itemgetter('exUnits', 'lateness', 'targetM', 'targetStd', 'utilisation',  'earliness'))
    
    bestScenario = listSummary[0]['scenario']
    aco = bestScenario[0]
    minDelta = bestScenario[1]
    G.Summary['orderedScenario'] = {}
    for i in range(len(listSummary)):        
        G.Summary['orderedScenario'][listSummary[i]['scenario']] = i+1 
    G.Summary['bestScenario'] = bestScenario
    if aco != G.ACO or minDelta != G.minDeltaUt:
        initialiseVar() 
        G.ACO = 0       # forces the simulation of the best ant (even though the best scenario is ACO
        G.minDeltaUt = minDelta
        AllocManagement_Hybrid2(G.Summary[(aco,minDelta)]['ant'])
        
    AllocManagement_Hybrid2_Forecast()
    
    outputResults()
    print 'calculation time', time.time()-startTime
    
if __name__ == '__main__':
    main()