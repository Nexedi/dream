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
Created on 24 Nov 2014
@author: Anna
'''

from Globals import G
import xlrd
from copy import deepcopy

def withoutFormat(row,col,sheet,integer):
    
    output = sheet.cell_value(row,col)        
    if sheet.cell_type(row,col) != 2:        
        output=output.encode('ascii', 'ignore')
    elif integer:
        output = int(output)
    return output

def my_split(s, seps):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res

def ImportInput(input, algorithmAttributes):
    # general simulation input
    mime_type, attachement_data = input[len('data:'):].split(';base64,', 1)
    attachement_data = attachement_data.decode('base64')
    wbin = xlrd.open_workbook(file_contents=attachement_data)
    G.maxEarliness = algorithmAttributes.get('maxEarliness',None)
    G.maxLateness = algorithmAttributes.get('maxLateness',None)
    startWeek =  algorithmAttributes.get('CurrentWeek',None)
    
    # utilisation calculation
    G.minDeltaUt = algorithmAttributes.get('minDelta',None)
    
    # ACO parameters
    G.ACO = algorithmAttributes.get('ACO',None)
    G.popSize=algorithmAttributes.get('ACOpopulationSize',None)
    if (not G.popSize) and G.ACO:
        G.ACOdefault = 1    
    G.noGen=algorithmAttributes.get('ACOnumberOfGenerations',None)
    
    # optimisation weights for forecast IP method
    G.weightFactor[0] = algorithmAttributes.get('maxAssignedQty',None)
    G.weightFactor[1] = algorithmAttributes.get('minUtilisation',None)
    G.weightFactor[2] = algorithmAttributes.get('minDeltaTargetUtilisation',None)
    G.weightFactor[3] = algorithmAttributes.get('minTargetUtilisation',None)
    G.weightFactor[4] = algorithmAttributes.get('MAProportionality',None)

    # GA parameters
    G.GA= algorithmAttributes.get('GA',None)
    G.popSizeGA =algorithmAttributes.get('GApopulationSize',None)
    if (not G.popSizeGA) and G.GA:
        G.GAdefault = 1
    G.noGenGA =algorithmAttributes.get('GAnumberOfGenerations',None)
    G.probXover =algorithmAttributes.get('XOver',None)
    G.probMutation =algorithmAttributes.get('mutationProbability',None)
    
    # Import capacity information...capacity = {Resource: {week {'originalCapacity':, 'remainingCapacity', 'minUtilisation'}
    sh = wbin.sheet_by_name('BN_Capa')
    rows = sh.nrows
    
    
    Weeks = {}
    w = 2
    while w<sh.ncols and withoutFormat(1,w,sh,1) != startWeek:
        w += 1
        
    if w == sh.ncols:
        print "please enter a valid week value"
        return "stop"
    
    refCap = {}
    noTarget = []
    
    for week in range(w,sh.ncols):
        Weeks[week] = withoutFormat(1,week,sh,1)
        G.WeekList.append(withoutFormat(1,week,sh,1))
        refCap[Weeks[week]] = 1
    G.planningHorizon = len(G.WeekList)
    for row in range(2,rows,4):
        
        bn = withoutFormat(row,0,sh,0)
        G.Bottlenecks.append(bn)
        
        G.Capacity[bn] = {}#{'OriginalCapacity':{}, 'RemainingCapacity':{}, 'minUtilisation':{}, 'targetUtilisation':{}}
        G.CurrentCapacityDictOrig[bn] = {}
        
        for week in range(w,sh.ncols):
            G.Capacity[bn][Weeks[week]]={'OriginalCapacity':withoutFormat(row,week,sh,1), 'RemainingCapacity':withoutFormat(row+1,week,sh,1), 'minUtOrig':withoutFormat(row+2,week,sh,0), 'targetUtOrig':withoutFormat(row+3,week,sh,0)}
            if G.Capacity[bn][Weeks[week]]['minUtOrig'] == '':
                G.Capacity[bn][Weeks[week]]['minUtilisation'] = 0
            else:
                G.Capacity[bn][Weeks[week]]['minUtilisation'] = G.Capacity[bn][Weeks[week]]['minUtOrig']
            
            if G.Capacity[bn][Weeks[week]]['targetUtOrig'] == '':
                G.Capacity[bn][Weeks[week]]['targetUtilisation'] = 1
                noTarget.append([bn, Weeks[week]])
            else:
                G.Capacity[bn][Weeks[week]]['targetUtilisation'] = G.Capacity[bn][Weeks[week]]['targetUtOrig']
                if G.Capacity[bn][Weeks[week]]['targetUtOrig'] < refCap[Weeks[week]]:
                    refCap[Weeks[week]] = G.Capacity[bn][Weeks[week]]['targetUtOrig']
                    
                
            G.CurrentCapacityDictOrig[bn][Weeks[week]] = withoutFormat(row,week,sh,1)
            
    for coppie in noTarget:
        if refCap[coppie[1]] == 1:
            refCap[coppie[1]] = 0
        G.Capacity[coppie[0]][coppie[1]]['targetUtilisation'] = refCap[coppie[1]]
                
    
            
            
    # Import loading factors
    sh = wbin.sheet_by_name('BN_Load Factor')
    rows = sh.nrows

    w = 3
    while withoutFormat(1,w,sh,1) != startWeek:
        w += 1
    
    Weeks = {}
    for week in range(w,sh.ncols):
        Weeks[week] = withoutFormat(1,week,sh,1)
        
    for row in range(2,rows):
        
        # check if sp has changed
        if withoutFormat(row,0,sh,0) != '':
            sp = withoutFormat(row,0,sh,0)        
            G.SPlist[sp] = []
            G.SPs.append(sp)
        
        # check if MA has changed    
        if withoutFormat(row,1,sh,0) != '':
            ma = withoutFormat(row,1,sh,0)
            G.SPlist[sp].append(ma)
            G.RouteDict[ma] = {}
        
        bn = withoutFormat(row,2,sh,0)
        G.RouteDict[ma][bn] = {}
        for week in range(w,sh.ncols):
            G.RouteDict[ma][bn][Weeks[week]] = withoutFormat(row,week,sh,0)
            
    # Import batch size
    sh = wbin.sheet_by_name('BatchSize')
    rows = sh.nrows
    
    w = 2
    while withoutFormat(2,w,sh,1) != startWeek:
        w += 1
    
    Weeks = {}
    for week in range(w,sh.ncols):
        Weeks[week] = withoutFormat(2,week,sh,1)
    
    for row in range(3,rows):
        
        ma = withoutFormat(row,1,sh,0)
        if ma == '':
            continue
        
        G.BatchSize[ma]= {}
        G.incompleteBatches[ma] = 0
        for week in range(w,sh.ncols):
            G.BatchSize[ma][Weeks[week]] = withoutFormat(row,week,sh,0)
#            G.incompleteBatches[ma][Weeks[week]] = 0 
            
            
    # Import order 
    sh = wbin.sheet_by_name('OrderSummary')
    rows = sh.nrows
    
    G.priorityList['order'] = []
    G.sortedOrders['order'] = {}
    
    for row in range(1,rows):
        
        week = withoutFormat(row,3,sh,1)
        if week < startWeek:
            continue
        
        orderID = withoutFormat(row,2,sh,0)
        G.orders[orderID] = {}
        G.orders[orderID]['orderID'] = orderID 
        G.orders[orderID]['sp'] = withoutFormat(row,0,sh,0)
        maList = withoutFormat(row,1,sh,0)
        maList = my_split(maList, ['; ', ';'])
        print 'malist', maList
        maList.remove('')
        G.orders[orderID]['MAlist'] = maList
        
        G.orders[orderID]['Week'] = week
        G.orders[orderID]['Qty'] = withoutFormat(row, 4, sh, 0)
        priority = withoutFormat(row, 5, sh, 1)
        G.orders[orderID]['priority'] = priority
        if priority not in G.priorityList['order']:
            G.priorityList['order'].append(priority)
            G.sortedOrders['order'][priority] = {}
        G.orders[orderID]['type'] = 'order'
        if week not in G.sortedOrders['order'][priority]:
            G.sortedOrders['order'][priority][week] = []
        G.sortedOrders['order'][priority][week].append(G.orders[orderID])

    # Import forecast
    sh = wbin.sheet_by_name('FC_Summary')
    rows = sh.nrows
    G.priorityList['forecast'] = []
    G.sortedOrders['forecast'] = {}
    Weeks = {}
    
    w = 3
    while withoutFormat(1,w,sh,1) != startWeek:
        w += 1
    
    for week in range(3,sh.ncols):
        Weeks[week] = withoutFormat(1,week,sh,1)
    
    row = w
    while row < rows:
        
        newSp = withoutFormat(row,1,sh,0)
        if newSp != '':
            sp = newSp
            
        newPriority = withoutFormat(row,2,sh,1)
        if newPriority != '':
            priority = newPriority
#            G.spForecastOrder.append(sp)
        
        subRow = 0
        maSuggested = []
        while subRow+row < rows and withoutFormat(subRow+row,3,sh,0)!='Total':
            maSuggested.append(withoutFormat(subRow+row,3,sh,0))
            subRow += 1
        
        print 'ma sug', maSuggested, subRow
        oID = 1
        orderID = 'Forecast_'+str(oID)
        for week in range(4,sh.ncols):        
            qty = withoutFormat(row+subRow,week,sh,1)
            if qty:
                G.orders[orderID] = {}
                G.orders[orderID]['ppos'] = 0   
                G.orders[orderID]['sp'] = sp   
                G.orders[orderID]['orderID'] = orderID        
                G.orders[orderID]['MAlist'] = G.SPlist[sp]
                G.orders[orderID]['Week'] = Weeks[week]
                G.orders[orderID]['Customer'] = None
                G.orders[orderID]['Qty'] = qty
                G.orders[orderID]['priority'] = priority
                G.orders[orderID]['suggestedMA'] = {}
                for ma in range(subRow):
                    G.orders[orderID]['suggestedMA'][maSuggested[ma]] = withoutFormat(row+ma,week,sh,1)
                if priority not in G.priorityList['forecast']:
                    G.priorityList['forecast'].append(priority)      
                    G.sortedOrders['forecast'][priority] = {}     
                G.orders[orderID]['type'] = 'forecast'
                
                if Weeks[week] not in G.sortedOrders['forecast'][priority]:
                    G.sortedOrders['forecast'][priority][Weeks[week]] = []
                G.sortedOrders['forecast'][priority][Weeks[week]].append(G.orders[orderID])
                oID += 1
                orderID = 'Forecast_'+str(oID)
            
        row += subRow+1
    
    # set 
    for sp in G.SPlist.keys():
        G.globalMAAllocationIW[sp] = {}
        for week in G.WeekList:
            G.globalMAAllocationIW[sp][week] = {'order':{}, 'forecast':{}}
            for priority in G.priorityList['order']:
                G.globalMAAllocationIW[sp][week]['order'][priority] = 0
            for priority in G.priorityList['forecast']:
                G.globalMAAllocationIW[sp][week]['forecast'][priority] = 0
        for ma in G.SPlist[sp]:
            G.globalMAAllocation[ma] = {}
            G.globalMAAllocationIW[ma] = {}
            for week in G.WeekList:
                G.globalMAAllocation[ma][week] = {'order':{}}
                G.globalMAAllocationIW[ma][week] = {'order':{}}
                for priority in G.priorityList['order']:
                    G.globalMAAllocation[ma][week]['order'][priority] = 0 
                    G.globalMAAllocationIW[ma][week]['order'][priority] = 0
                G.globalMAAllocation[ma][week]['forecast'] = {}
                G.globalMAAllocationIW[ma][week]['forecast'] = {}
                for priority in G.priorityList['forecast']:
                    G.globalMAAllocation[ma][week]['forecast'][priority] = 0 
                    G.globalMAAllocationIW[ma][week]['forecast'][priority] = 0
                
    # set lateness and earliness results
    for week in G.WeekList:
        G.Lateness[week] = {}
        G.Earliness[week] = {}
        for sp in G.SPlist.keys():
            for ma in G.SPlist[sp]:
                G.Lateness[week][ma] = {'qty':[], 'lateness':[]}
                G.Earliness[week][ma] = {'qty':[], 'earliness':[]}

    # set excess results
    for sp in G.SPlist.keys():
        G.Excess[sp] = {}
        for week in G.WeekList:
            G.Excess[sp][week] = 0
            
    G.ordersOrig = deepcopy(G.orders)
    G.sortedOrdersOrig = deepcopy(G.sortedOrders)

if __name__ == '__main__':
    ImportInput()        
        
     