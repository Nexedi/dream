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
Created on 12 Dec 2014

@author: Anna
'''

from Globals import G
from pulp import *
from os import remove 
from glob import glob
from time import time

def Allocation_IP(item, week, previousAss, capacity, weightFactor):
    
    startLP = time()
    MAlist = item['MAlist']
    
    # calculate number of units to be allocated
    allQty = item['Qty']
    for ma in previousAss.keys():
        allQty -= previousAss[ma]
    assert(allQty>0)        
            
    
    # define LP problem    
    prob = LpProblem("disaggregation", LpMaximize)

    # declare variables (first set of variables: MA qty)
    MA_var = LpVariable.dicts("MA",MAlist,0,cat='Integer')        
#    print 'ma ver', MA_var

    #============================
    # multi - objective function
    #============================
    
    #___________________________________________________
    # first objective: max SP units allocated to a week
    
    BS = [float(G.BatchSize[ma][week]) for ma in MAlist]
    if weightFactor[0]:
        h1=[MA_var[ma]*(weightFactor[0]*min(BS)/allQty) for ma in MAlist]
#    print 'h1', h1, allQty

    #_________________________________________________
    # second objective: balance bottleneck utilisation
            
    # second set of variables (Delta_TargetUt represents the delta utilisation wrt target utilisation
    Delta_targetUt = LpVariable.dicts("target",G.Bottlenecks)   
    Util = LpVariable.dicts("utilisation",G.Bottlenecks) 
    
    # remaining capacity and utilisation calculation
    capDict_obj = {}       #reports the remaining capacity corresponding with MA allocation
    utilisation = {}        # reports bottleneck utilisation
    
    requiredCapacity={}
    for bottleneck in G.Bottlenecks:

        requiredCapacity[bottleneck] = []
        for ma in MAlist:
            if bottleneck in G.RouteDict[ma]:
                requiredCapacity[bottleneck].append(G.RouteDict[ma][bottleneck][week] * MA_var[ma] * G.BatchSize[ma][week])

        capDict_obj[bottleneck] = lpSum([-1*capacity[bottleneck][week]]+[requiredCapacity[bottleneck]]+[G.Capacity[bottleneck][week]['OriginalCapacity']])

        utilisation[bottleneck] = 1.0/float(G.Capacity[bottleneck][week]['OriginalCapacity']) *capDict_obj[bottleneck] 
        Util[bottleneck] = utilisation[bottleneck]*-1
        
        # delta target utilisation calculation (through definition of constraints)
        prob += lpSum([(utilisation[bottleneck] - G.Capacity[bottleneck][week]['targetUtilisation'])/float(G.Capacity[bottleneck][week]['targetUtilisation'])]) >= Delta_targetUt[bottleneck]
        prob += lpSum([(G.Capacity[bottleneck][week]['targetUtilisation'] - utilisation[bottleneck])/float(G.Capacity[bottleneck][week]['targetUtilisation'])]) >= Delta_targetUt[bottleneck]
    
    if weightFactor[1]:
        h1+=[Util[bottleneck]*weightFactor[1] for bottleneck in G.Bottlenecks]
    if weightFactor[2]:
        h1+=[Delta_targetUt[bottleneck]*weightFactor[2] for bottleneck in G.Bottlenecks]
    
    # aggregate objective
    if weightFactor[3]:
        # third set of variables (Delta_Ut represents the delta between target utilisation
        Delta_Ut = LpVariable.dicts("DeltaTarget",[(b1,b2) for i1, b1 in enumerate(G.Bottlenecks) for b2 in G.Bottlenecks[i1+1:]])   
        
        for i1, b1 in enumerate(G.Bottlenecks):
            for b2 in G.Bottlenecks[i1+1:]:
                prob += lpSum([Util[b1],-1*Util[b2]]) >= Delta_Ut[(b1,b2)]
                prob += lpSum([Util[b2],-1*Util[b1]]) >= Delta_Ut[(b1,b2)]
                #prob += lpSum([Delta_targetUt[b1],-1*Delta_targetUt[b2]]) >= Delta_Ut[(b1,b2)]
                #prob += lpSum([Delta_targetUt[b2], -1*Delta_targetUt[b1]]) >= Delta_Ut[(b1,b2)]
            
        h1+=[Delta_Ut[(b1,b2)]*weightFactor[3] for i1, b1 in enumerate(G.Bottlenecks) for b2 in G.Bottlenecks[i1+1:]]


    #___________________________________________________________________________________
    # third objective: support proportional disaggregation of SP into corresponding MAs            
    
    if weightFactor[4]:
        # create set of variables reporting the delta assignment across the MAs belonging to a SP
        Delta_MA = LpVariable.dicts("SPdistribution",MAlist)
        
        # calculate the delta assignment of MAs corresponding to SPs (through constraints)
        for ma in MAlist:
            if ma in item['suggestedMA']:
                prob += lpSum((previousAss[ma] + MA_var[ma] * G.BatchSize[ma][week] - item['suggestedMA'][ma])/ item['Qty']) >= Delta_MA[ma]
                prob += lpSum((item['suggestedMA'][ma] - previousAss[ma] - MA_var[ma] * G.BatchSize[ma][week])/ item['Qty']) >= Delta_MA[ma]
        
        h1+=[Delta_MA[ma]*weightFactor[4] for ma in MAlist]                
        
    #_____________________________
    # aggregate and set objectives      
    prob += lpSum(h1)
    
    
    #=================
    # set constraints
    #=================
    
#    print 'batch size', G.BatchSize[ma][week], 'qty', allQty
    # production constraints
    for ma in MAlist:
        prob += lpSum([MA_var[ma2]*G.BatchSize[ma2][week] for ma2 in MAlist]) <= allQty+G.BatchSize[ma][week]-1
        
            
    # capacity constraints
    for bottleneck in G.Bottlenecks:                
        prob += lpSum([MA_var[ma]*G.RouteDict[ma][bottleneck][week]*G.BatchSize[ma][week] for ma in MAlist if bottleneck in G.RouteDict[ma]]) <= capacity[bottleneck][week]- 0.1
    
    #_______________________________________    
    # write the problem data to an .lp file.
    prob.writeLP("IPifx.lp") 
    prob.solve()
    
    print 'lp results', item['sp'], allQty, LpStatus[prob.status], sum(MA_var[ma].varValue* G.BatchSize[ma][week] for ma in MAlist)
    allocation = {}
    for ma in MAlist:
        allocation[ma] = MA_var[ma].varValue * G.BatchSize[ma][week]
#        print ma, MA_var[ma].varValue
        
        
    if LpStatus[prob.status] != 'Optimal':
        print 'WARNING: LP solution ', LpStatus[prob.status]
        
    # remove lp files
    files = glob('*.mps')
    for f in files:
        remove(f)
        
    files = glob('*.lp')
    for f in files:
        remove(f)
    
    G.LPtime += startLP
    return allocation, LpStatus[prob.status]
