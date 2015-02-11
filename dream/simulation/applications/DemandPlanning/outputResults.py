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
Created on 8 Dec 2014

@author: Anna
'''
from Globals import G
import tablib

def outputResults():
    import os
    if not os.path.exists('Results'): os.makedirs('Results')
    G.reportResults.add_sheet(G.OrderResults)
    G.reportResults.add_sheet(G.forecastResults)
    
    # report capacity results
    head = ['Resource_List', 'Values'] + G.WeekList
    head = tuple(head)
    G.CapacityResults.headers = head
    for bottleneck in G.Bottlenecks:
        initialCap = [G.Capacity[bottleneck][week]['OriginalCapacity'] for week in G.WeekList]
        G.CapacityResults.append([bottleneck, 'Capa Pegging Resource Capacity (UoM)',]+initialCap)
        G.CapacityResults.append(['', 'Capa Pegging Resource Total Load (UoM)',]+[G.Capacity[bottleneck][week]['OriginalCapacity']-G.CurrentCapacityDict[bottleneck][week] for week in G.WeekList])
        G.CapacityResults.append(['', 'Capa Pegging Resource Total Util (Percent)',]+[float(G.Capacity[bottleneck][week]['OriginalCapacity']-G.CurrentCapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity']*100 for week in G.WeekList])       

    # report allocation results
    head = ['PPOS', 'Demand_Items_Product_DCBNO - SP', 'Demand_Items_Product_DCBNO - MA', 'Demand_Type - Group', 'Priority','Values'] + G.WeekList
    G.allocationResults.headers = head
    for sp in G.SPs:
        newSp = sp
        spReqQty = {}
        spPlannedQty = {}
        countedForecastSP = {}
        for week in G.WeekList:
            spReqQty[week] = 0
            spPlannedQty[week] = 0
            countedForecastSP[week] = []
        
         
        for ma in G.SPlist[sp]:
            maReqQty = {}
            maPlannedQty = {}
            for week in G.WeekList:
                maReqQty[week] = 0
                maPlannedQty[week] = 0
        
        
            # add orders results
            for priority in G.priorityList['order']: 
                orderMA = []
                
                for week in G.WeekList:
                    temp = 0
                    if week in G.sortedOrders['order'][priority]:
                        for i in range(len(G.sortedOrders['order'][priority][week])):
                            if G.orders[G.sortedOrders['order'][priority][week][i]['orderID']]['chosenMA'] == ma:
                                temp+=G.sortedOrders['order'][priority][week][i]['Qty']
                    
                    orderMA.append(temp)
                    maReqQty[week] += temp
                    spReqQty[week] += temp
                if newSp != None:
                    G.allocationResults.append(['', sp, ma, 'ORDERS', priority, 'Demand Request Qty'] + orderMA )
                    newSp = None
                else:
                    G.allocationResults.append(['', '', ma, 'ORDERS', priority, 'Demand Request Qty'] + orderMA )
                G.allocationResults.append(['', '', '', '', priority, 'Demand Planned Qty'] + [G.globalMAAllocation[ma][week]['order'][priority] for week in G.WeekList])

            if len(G.priorityList['order']) == 0:
                if newSp != None:
                    G.allocationResults.append(['', sp, ma, 'ORDERS', 0, 'Demand Request Qty'] + [0 for i in range(len(G.WeekList))] )
                    newSp = None
                else:
                    G.allocationResults.append(['', '', ma, 'ORDERS', 0, 'Demand Request Qty'] + [0 for i in range(len(G.WeekList))] )
                G.allocationResults.append(['', '', '', '', 0, 'Demand Planned Qty'] + [0 for i in range(len(G.WeekList))])
                    
            # add forecast results
            if len(G.priorityList['forecast']) == 0:
                G.allocationResults.append(['', '', '', 'FORECAST', 0, 'Demand Request Qty'] + [0 for i in range(len(G.WeekList))] )
                G.allocationResults.append(['', '', '', '', 0, 'Demand Planned Qty'] +[0 for i in range(len(G.WeekList))])
                
            for priority in G.priorityList['forecast']:
                orderMA = []
                
                for week in G.WeekList:
                    temp = 0
                    if week in G.sortedOrders['forecast'][priority]:
                        for i in range(len(G.sortedOrders['forecast'][priority][week])):
                            if  ma in G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['suggestedMA']:
                                temp+=G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['suggestedMA'][ma]     
                            if G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['sp'] == sp and G.sortedOrders['forecast'][priority][week][i]['orderID'] not in countedForecastSP[week]:
                                spReqQty[week] += G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['Qty']
                                countedForecastSP[week].append(G.sortedOrders['forecast'][priority][week][i]['orderID'])
                            

                    orderMA.append(temp)
                    maReqQty[week] += temp
                
                G.allocationResults.append(['', '', '', 'FORECAST', priority, 'Demand Request Qty'] + orderMA )
                G.allocationResults.append(['', '', '', '', priority, 'Demand Planned Qty'] + [G.globalMAAllocation[ma][week]['forecast'][priority] for week in G.WeekList])
            
            orderMA = []
            plannedMA = []
            for week in G.WeekList:
                orderMA.append(maReqQty[week])
                for orderType in ['order', 'forecast']:
                    for priority in G.priorityList[orderType]:
                        maPlannedQty[week] += G.globalMAAllocation[ma][week][orderType][priority]
                plannedMA.append(maPlannedQty[week])
                spPlannedQty[week] += maPlannedQty[week]
                    
            G.allocationResults.append(['', '', ma+'Demand Request Qty', '', '', ''] + orderMA )
            G.allocationResults.append(['', '', ma+'Demand Planned Qty', '', '', ''] + plannedMA)
        
        orderSP = []
        plannedSP = []
        for week in G.WeekList:
            plannedSP.append(spPlannedQty[week])
            orderSP.append(spReqQty[week])
        
        G.allocationResults.append(['', sp+'Demand Request Qty', '', '', '', ''] + orderSP )
        G.allocationResults.append(['', sp+'Demand Planned Qty', '', '', '', ''] + plannedSP)
         
    G.reportResults.add_sheet(G.allocationResults)
    
    G.reportResults.add_sheet(G.CapacityResults)
    
    # report lateness results
    latenessResults = tablib.Dataset(title='Lateness')
    head = tuple(['Demand Request Days Late Weighted'] + G.WeekList)
    latenessResults.headers = (head)
    
    weightedLateSP = {}
    for week in G.WeekList:
        weightedLateSP[week] = {}
        for sp in G.SPlist.keys():
            weightedLateSP[week][sp] = {'qty':[], 'lateness':[]}
            for ma in G.SPlist[sp]:
                if len(G.Lateness[week][ma]['qty']):
                    qty = sum(G.Lateness[week][ma]['qty'])
                    weightedLateMA = sum([G.Lateness[week][ma]['qty'][i]*G.Lateness[week][ma]['lateness'][i] for i in range(len(G.Lateness[week][ma]['qty']))])/qty                    
                else:
                    qty = 0
                    weightedLateMA = 0
                G.Lateness[week][ma]['result'] = weightedLateMA
                weightedLateSP[week][sp]['qty'].append(qty)
                weightedLateSP[week][sp]['lateness'].append(weightedLateMA)
            qtySP = sum(weightedLateSP[week][sp]['qty'])
            if qtySP:
                weightedLateSP[week][sp]['result'] = sum([weightedLateSP[week][sp]['qty'][i]*weightedLateSP[week][sp]['lateness'][i] for i in range(len(weightedLateSP[week][sp]['qty']))])/qtySP
            else:
                weightedLateSP[week][sp]['result'] = 0
                
    for sp in G.SPs:
        latenessResults.append([sp]+[weightedLateSP[week][sp]['result'] for week in G.WeekList])
        for ma in G.SPlist[sp]:
            latenessResults.append([ma]+[G.Lateness[week][ma]['result'] for week in G.WeekList])
        latenessResults.append(['' for i in range(len(G.WeekList)+1)])
    
    G.reportResults.add_sheet(latenessResults)
    
    # report earliness results
    earlinessResults = tablib.Dataset(title='Earliness')
    head = tuple(['Demand Request Days Early Weighted'] + G.WeekList)
    earlinessResults.headers = (head)
    
    weightedLateSP = {}
    for week in G.WeekList:
        weightedLateSP[week] = {}
        for sp in G.SPlist.keys():
            weightedLateSP[week][sp] = {'qty':[], 'earliness':[]}
            for ma in G.SPlist[sp]:
                if len(G.Earliness[week][ma]['qty']):
                    qty = sum(G.Earliness[week][ma]['qty'])
                    weightedLateMA = sum([G.Earliness[week][ma]['qty'][i]*G.Earliness[week][ma]['earliness'][i] for i in range(len(G.Earliness[week][ma]['qty']))])/qty                    
                else:
                    qty = 0
                    weightedLateMA = 0
                G.Earliness[week][ma]['result'] = weightedLateMA
                weightedLateSP[week][sp]['qty'].append(qty)
                weightedLateSP[week][sp]['earliness'].append(weightedLateMA)
            qtySP = sum(weightedLateSP[week][sp]['qty'])
            if qtySP:
                weightedLateSP[week][sp]['result'] = sum([weightedLateSP[week][sp]['qty'][i]*weightedLateSP[week][sp]['earliness'][i] for i in range(len(weightedLateSP[week][sp]['qty']))])/qtySP
            else:
                weightedLateSP[week][sp]['result'] = 0
                
    for sp in G.SPs:
        earlinessResults.append([sp]+[weightedLateSP[week][sp]['result'] for week in G.WeekList])
        for ma in G.SPlist[sp]:
            earlinessResults.append([ma]+[G.Earliness[week][ma]['result'] for week in G.WeekList])
        earlinessResults.append(['' for i in range(len(G.WeekList)+1)])
    
    G.reportResults.add_sheet(earlinessResults)
    
    excessResults = tablib.Dataset(title='Excess')
    head = tuple(['Demand Request Excess'] + G.WeekList)
    excessResults.headers = (head)
    for sp in G.SPs:
        excessResults.append([sp]+[G.Excess[sp][week] for week in G.WeekList])
    G.reportResults.add_sheet(excessResults)
    

    with open(os.path.join('Results', 'rTable.html'), 'wb') as h: #completion time, cycle time and delay info in html format
        h.write(G.reportResults.html)
    with open(os.path.join('Results', 'allocation.xlsx'), 'wb') as f: #time level schedule info
        f.write(G.reportResults.xlsx)


