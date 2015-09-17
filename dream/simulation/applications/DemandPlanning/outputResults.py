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
from numpy import mean

def outputResults():
    import os
    if not os.path.exists('Results'): os.makedirs('Results')
    
    # report multi-analysis results
    
#    head = (['', 'Heur0', 'Heur1', 'ACO0', 'ACO1'])
    dictHead = {0:'Heur',1:'ACO'}
    head = ['', ]
    for aco in G.acoRange:
        for minDelta in G.minRange[aco]:
            head.append(dictHead[aco]+str(minDelta))
    resultsOverview = tablib.Dataset(title='Overview')
    resultsOverview.headers = (head)
    print G.Summary.keys(), G.acoRange[0], G.minRange[G.acoRange[0]]
    oMetric = ['noExcess', 'exUnits', 'noLateOrders', 'lateness', 'noEarlyOrders', 'earliness', 'targetM', 'targetStd', 'utilisation']
    for metric in oMetric:
        if metric!='scenario' and metric != 'ant':
            r = []
            for aco in G.acoRange:
                for minDelta in G.minRange[aco]:
                    r.append(G.Summary[(aco,minDelta)][metric])
            resultsOverview.append([metric]+r)
    
    resultsOverview.append(['' for i in range(len(head))])
    r = []
    for aco in G.acoRange:
        for minDelta in G.minRange[aco]:
            r.append(G.Summary['orderedScenario'][(aco,minDelta)])
    resultsOverview.append(['ordered scenarios']+r)
    resultsOverview.append(['selected scenario', G.Summary['bestScenario']]+['' for i in range(len(head)-2)])
    
    G.reportResults.add_sheet(resultsOverview)      
    G.reportResults.add_sheet(G.OrderResults)
    G.reportResults.add_sheet(G.OrderResultsShort)
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
        G.CapacityResults.append(['', 'Capa Pegging Resource Min Util (Percent)',]+[G.Capacity[bottleneck][week]['minUtOrig']*100 for week in G.WeekList])       
        G.CapacityResults.append(['', 'Capa Pegging Resource Target Util (Percent)',]+[G.Capacity[bottleneck][week]['targetUtilisation']*100 for week in G.WeekList])       
        
    # utilisation results
    for bottleneck in G.Bottlenecks:
        G.Utilisation[bottleneck] = {}
        G.Butilisation[bottleneck] = {}
        for week in G.WeekList:
            G.Utilisation[bottleneck][week] = {}
            G.Utilisation[bottleneck][week]['averageUtilization'] = float(G.Capacity[bottleneck][week]['OriginalCapacity']-G.CurrentCapacityDict[bottleneck][week])/G.Capacity[bottleneck][week]['OriginalCapacity']
            G.Utilisation[bottleneck][week]['minUtilization'] = G.Capacity[bottleneck][week]['minUtilisation']
            G.Utilisation[bottleneck][week]['maxUtilization'] = G.Capacity[bottleneck][week]['targetUtilisation']
            
        
    # report allocation results
    head = ['PPOS', 'Demand_Items_Product_DCBNO - SP', 'Demand_Items_Product_DCBNO - MA', 'Demand_Type - Group', 'Priority','Values'] + G.WeekList
    G.allocationResults.headers = head
    spReqQty = {}
    spPlannedQty = {}
    maReqQty = {}
    for sp in G.SPs:
        newSp = sp
        spReqQty[sp] = {}
        spPlannedQty[sp] = {}
        countedForecastSP = {}
        for week in G.WeekList:
            spReqQty[sp][week] = 0
            spPlannedQty[sp][week] = 0
            countedForecastSP[week] = []
        
         
        for ma in G.SPlist[sp]:
            maReqQty[ma] = {}
            maPlannedQty = {}
            for week in G.WeekList:
                maReqQty[ma][week] = 0
                maPlannedQty[week] = 0
            for bot in G.Bottlenecks:
                G.Butilisation[bot][ma] = {}
                for week in G.WeekList:
                    G.Butilisation[bot][ma][week] = 0
        
        
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
                    maReqQty[ma][week] += temp
                    spReqQty[sp][week] += temp
                    
                    for bot in G.RouteDict[ma]:
                        G.Butilisation[bot][ma][week] += G.RouteDict[ma][bot][week]*G.globalMAAllocation[ma][week]['order'][priority]/G.Capacity[bot][week]['OriginalCapacity']*100
                    
                if newSp != None:
                    G.allocationResults.append(['', sp, ma, 'ORDERS', priority, 'Demand Request Qty'] + orderMA )
                    newSp = None
                else:
                    G.allocationResults.append(['', '', ma, 'ORDERS', priority, 'Demand Request Qty'] + orderMA )
                G.allocationResults.append(['', '', '', 'ORDERS', priority, 'Demand Planned Qty'] + [G.globalMAAllocation[ma][week]['order'][priority] for week in G.WeekList])

            if len(G.priorityList['order']) == 0:
                if newSp != None:
                    G.allocationResults.append(['', sp, ma, 'ORDERS', 0, 'Demand Request Qty'] + [0 for i in range(len(G.WeekList))] )
                    newSp = None
                else:
                    G.allocationResults.append(['', '', ma, 'ORDERS', 0, 'Demand Request Qty'] + [0 for i in range(len(G.WeekList))] )
                G.allocationResults.append(['', '', '', 'ORDERS', 0, 'Demand Planned Qty'] + [0 for i in range(len(G.WeekList))])
                    
            # add forecast results
            if len(G.priorityList['forecast']) == 0:
                G.allocationResults.append(['', '', '', 'FORECAST', 0, 'Demand Request Qty'] + [0 for i in range(len(G.WeekList))] )
                G.allocationResults.append(['', '', '', 'FORECAST', 0, 'Demand Planned Qty'] +[0 for i in range(len(G.WeekList))])
                
            for priority in G.priorityList['forecast']:
                orderMA = []
                
                for week in G.WeekList:
                    temp = 0
                    if week in G.sortedOrders['forecast'][priority]:
                        for i in range(len(G.sortedOrders['forecast'][priority][week])):
                            if  ma in G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['suggestedMA']:
                                temp+=G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['suggestedMA'][ma]     
                            if G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['sp'] == sp and G.sortedOrders['forecast'][priority][week][i]['orderID'] not in countedForecastSP[week]:
                                spReqQty[sp][week] += G.orders[G.sortedOrders['forecast'][priority][week][i]['orderID']]['Qty']
                                countedForecastSP[week].append(G.sortedOrders['forecast'][priority][week][i]['orderID'])
                            

                    orderMA.append(temp)
                    maReqQty[ma][week] += temp
                    
                    for bot in G.RouteDict[ma]:
                        G.Butilisation[bot][ma][week] += G.RouteDict[ma][bot][week]*G.globalMAAllocation[ma][week]['order'][priority]/G.Capacity[bot][week]['OriginalCapacity']*100
                
                G.allocationResults.append(['', '', '', 'FORECAST', priority, 'Demand Request Qty'] + orderMA )
                G.allocationResults.append(['', '', '', 'FORECAST', priority, 'Demand Planned Qty'] + [G.globalMAAllocation[ma][week]['forecast'][priority] for week in G.WeekList])
            
            orderMA = []
            plannedMA = []
            for week in G.WeekList:
                orderMA.append(maReqQty[ma][week])
                for orderType in ['order', 'forecast']:
                    for priority in G.priorityList[orderType]:
                        maPlannedQty[week] += G.globalMAAllocation[ma][week][orderType][priority]
                plannedMA.append(maPlannedQty[week])
                spPlannedQty[sp][week] += maPlannedQty[week]
                    
            G.allocationResults.append(['', '', ma+'Demand Request Qty', '', '', ''] + orderMA )
            G.allocationResults.append(['', '', ma+'Demand Planned Qty', '', '', ''] + plannedMA)
        
        orderSP = []
        plannedSP = []
        for week in G.WeekList:
            plannedSP.append(spPlannedQty[sp][week])
            orderSP.append(spReqQty[sp][week])
        
        G.allocationResults.append(['', sp+'Demand Request Qty', '', '', '', ''] + orderSP )
        G.allocationResults.append(['', sp+'Demand Planned Qty', '', '', '', ''] + plannedSP)
         
    G.reportResults.add_sheet(G.allocationResults)
    
    G.reportResults.add_sheet(G.CapacityResults)
    
    # report lateness results
    latenessResults = tablib.Dataset(title='Lateness')
    head = tuple(['Demand Request Days Late Weighted'] + G.WeekList)
    latenessResults.headers = (head)
    
    weightedLateSP = {}
    qtyRif = {}
    for week in G.WeekList:
        weightedLateSP[week] = {}
        qtyRif[week]={}
        for sp in G.SPlist.keys():
            qtyRif[week][sp] = {'tot':0}
            for typeOrder in ['order','forecast']:
                for priority in G.priorityList[typeOrder]:
                    qtyRif[week][sp]['tot'] += G.globalMAAllocationIW[sp][week][typeOrder][priority]
            weightedLateSP[week][sp] = 0
            
            for ma in G.SPlist[sp]:
                qtyRif[week][sp][ma] = 0
                if len(G.Lateness[week][ma]['qty']):
                    G.Lateness[week][ma]['result'] =  sum(G.Lateness[week][ma]['lateness'])*100
                else:
                    G.Lateness[week][ma]['result'] = 0
                for typeOrder in ['order','forecast']:
                    for priority in G.priorityList[typeOrder]:
                        qtyRif[week][sp]['tot'] += G.globalMAAllocationIW[ma][week][typeOrder][priority]
                        qtyRif[week][sp][ma] += G.globalMAAllocationIW[ma][week][typeOrder][priority]
            
            for ma in G.SPlist[sp]:
                if qtyRif[week][sp]['tot']:
                    weightedLateSP[week][sp] += (G.Lateness[week][ma]['result']*float(qtyRif[week][sp][ma]))/qtyRif[week][sp]['tot']                
                
    for sp in G.SPs:
        latenessResults.append([sp]+[weightedLateSP[week][sp] for week in G.WeekList])
        for ma in G.SPlist[sp]:
            latenessResults.append([ma]+[G.Lateness[week][ma]['result'] for week in G.WeekList])
        latenessResults.append(['' for i in range(len(G.WeekList)+1)])
    
    G.reportResults.add_sheet(latenessResults)
    
    
    # report earliness results
    earlinessResults = tablib.Dataset(title='Earliness')
    head = tuple(['Demand Request Days Early Weighted'] + G.WeekList)
    earlinessResults.headers = (head)
    
    weightedEarlySP = {}
    for week in G.WeekList:
        weightedEarlySP[week] = {}
        for sp in G.SPlist.keys():
            weightedEarlySP[week][sp] = 0
            
            for ma in G.SPlist[sp]:
                if len(G.Earliness[week][ma]['qty']):
                    G.Earliness[week][ma]['result'] =  sum(G.Earliness[week][ma]['earliness'])*100
                else:
                    G.Earliness[week][ma]['result'] = 0
            
            for ma in G.SPlist[sp]:
                if qtyRif[week][sp]['tot']:
                    weightedEarlySP[week][sp] += (G.Earliness[week][ma]['result']*float(qtyRif[week][sp][ma]))/qtyRif[week][sp]['tot']
                

    for sp in G.SPs:
        earlinessResults.append([sp]+[weightedEarlySP[week][sp] for week in G.WeekList])
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
    
    excessStats = tablib.Dataset(title='Stats')
    head = tuple(['','no Orders', 'avg Value [%]'])
    excessStats.headers = (head)
    excessStats.append(['Lateness',G.LateMeasures['noLateOrders'],mean(G.LateMeasures['lateness'])*100])
    excessStats.append(['Earliness',G.LateMeasures['noEarlyOrders'],mean(G.LateMeasures['earliness'])*100])
    excessStats.append(['Excess',G.LateMeasures['noExcess'],G.LateMeasures['exUnits']])
    G.reportResults.add_sheet(excessStats)

    incomBatches = tablib.Dataset(title='InBatch')
    for sp in G.SPs:
        for ma in G.SPlist[sp]:
            incomBatches.append([ma,G.incompleteBatches[ma]])
    G.reportResults.add_sheet(incomBatches)
    
    
    # report bottleneck utilisation results ordered per MA
    c = 1
    for bottleneck in G.Bottlenecks:
        BottUtilisation = tablib.Dataset(title = 'B'+str(c))
        head = ['Full Name Bottleneck','MA']+G.WeekList
        BottUtilisation.headers = (head)
#        BottUtilisation.append([bottleneck,'']+['' for i in G.WeekList])
        new = 1
        for sp in G.SPs:
            for ma in G.SPlist[sp]:
                if new:
                    BottUtilisation.append([bottleneck,ma]+[G.Butilisation[bottleneck][ma][week] for week in G.WeekList])
                    new = 0
                else:
                    BottUtilisation.append(['',ma]+[G.Butilisation[bottleneck][ma][week] for week in G.WeekList])
        G.reportResults.add_sheet(BottUtilisation)
        c += 1

    
    with open('Results\\rTable.html', 'wb') as h: #completion time, cycle time and delay info in html format
        h.write(G.reportResults.html)
    if G.capRep == None:
        with open('Results\\allocation.xlsx', 'wb') as f: #time level schedule info
            f.write(G.reportResults.xlsx)
    else:
        with open('Results\\allocation.xlsx', 'wb') as f: #time level schedule info
            f.write(G.reportResults.xlsx)
        
        
'''    weightedLateSP = {}
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
        
    weightedEarlySP = {}
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
                '''    
    