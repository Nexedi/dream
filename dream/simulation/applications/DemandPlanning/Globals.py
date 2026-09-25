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
Created on 5 Sep 2013

@author: Anna
'''
import tablib
from copy import deepcopy

class G:
    Capacity = {}
    RouteDict = {}
    maxEarliness = 0        # max number of weeks for earliness
    maxLateness = 0         # max number of weeks for lateness
    planningHorizon =0      # for future demand purposes
#    demandFile = None
    CurrentCapacityDict = {}
    CurrentCapacityDictOrig = {}
    Bottlenecks = []
    SPlist = {}
    SPs = []
    BatchSize = {}
    orders = {}
    sortedOrders = {}
    ordersOrig = {}
    sortedOrdersOrig = {}
    #forecast = {}
    incompleteBatches = {}
    items ={}
    WeekList=[]
    priorityList = {}
    Earliness = {}
    Lateness = {}
    Excess = {}
    LateMeasures = {'noLateOrders':0, 'lateness':[], 'noEarlyOrders':0, 'earliness':[], 'noExcess':0, 'exUnits':0}
    Summary = {}
    
    weightFactor = [10.0,1.0,0,2,0.5]
    
    # ACO parameters
    ACO = 1
    noGen = 5
    popSize = 10
    ACOdefault = 0
    
    # GA parameters
    GA = 0          # suggests whether application of GA to forecast diseggragation is required
    noGenGA = 5
    popSizeGA = 8
    probXover = 0.6
    probMutation = 0.1
    elitistSelection = 1
    terminationGA = 4
    GAdefault = 0
    
    # utilisation calculation
    minDeltaUt = 0
    acoRange = []
    minRange = {}

    
    # output variables
    reportResults = tablib.Databook()
    OrderResults = tablib.Dataset(title='OrderSummary')
    OrderResults.headers = ('OrderID', 'SP_NUMBER', 'MA_LIST', 'REQUEST_DATE', 'ORDERQTY', 'PRIORITY', 'CHOSEN_MA','ORDERED_MA_LIST', 'LATENESS', 'EARLINESS', 'ALLOCATION')
    OrderResultsShort = tablib.Dataset(title='OrderResultsForDM')
    OrderResultsShort.headers = ('OrderID', 'MA_LIST')
    forecastResults = tablib.Dataset(title='ForecastSummary')
    forecastResults.headers = ('PPOS', 'SP_NUMBER', 'MA_LIST', 'REQUEST_DATE', 'ORDERQTY', 'PRIORITY', 'CHOSEN_MA', 'LATENESS', 'EARLINESS', 'ALLOCATION')
    globalMAAllocation = {}
    globalMAAllocationIW = {}
    spForecastOrder = []
    CapacityResults = None
    CapacityResults = tablib.Dataset(title = 'BN_Capa')
    allocationResults = tablib.Dataset(title = 'Demand_coverage')
    Utilisation = {}
    Butilisation = {}
    LPtime = 0
    capRep = None
    
#    filterItem = 0
#    filterWeek = 0
def initialiseVar():

    G.CurrentCapacityDict = deepcopy(G.CurrentCapacityDictOrig)
    G.orders = deepcopy(G.ordersOrig)
    G.sortedOrders = deepcopy(G.sortedOrdersOrig)
    #G.forecast = {}
#    G.items ={}

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
        for ma in G.SPlist[sp]:
            G.incompleteBatches[ma] = 0

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

    G.LateMeasures = {'noLateOrders':0, 'lateness':[], 'noEarlyOrders':0, 'earliness':[], 'noExcess':0, 'exUnits':0}
    
    # output variables
    G.reportResults = tablib.Databook()
    G.OrderResults = tablib.Dataset(title='OrderSummary')
    G.OrderResults.headers = ('OrderID', 'SP_NUMBER', 'MA_LIST', 'REQUEST_DATE', 'ORDERQTY', 'PRIORITY', 'CHOSEN_MA','ORDERED_MA_LIST', 'LATENESS', 'EARLINESS', 'ALLOCATION')
    G.OrderResultsShort = tablib.Dataset(title='OrderResultsForDM')
    G.OrderResultsShort.headers = ('OrderID', 'MA_LIST')
    G.forecastResults = tablib.Dataset(title='ForecastSummary')
    G.forecastResults.headers = ('PPOS', 'SP_NUMBER', 'MA_LIST', 'REQUEST_DATE', 'ORDERQTY', 'PRIORITY', 'CHOSEN_MA', 'LATENESS', 'EARLINESS', 'ALLOCATION')
    G.CapacityResults = None
    G.CapacityResults = tablib.Dataset(title = 'BN_Capa')
    G.allocationResults = tablib.Dataset(title = 'Demand_coverage')
    G.Utilisation = {}
    G.Butilisation = {}