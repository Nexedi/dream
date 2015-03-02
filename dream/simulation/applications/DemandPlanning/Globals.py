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

class G:
    Capacity = {}
    RouteDict = {}
    maxEarliness = 0        # max number of weeks for earliness
    maxLateness = 0         # max number of weeks for lateness
    planningHorizon =0      # for future demand purposes
#    demandFile = None
    CurrentCapacityDict = {}
    Bottlenecks = []
    SPlist = {}
    SPs = []
    BatchSize = {}
    orders = {}
    sortedOrders = {}
    forecast = {}
    incompleteBatches = {}
    items ={}
    WeekList=[]
    priorityList = {}
    Earliness = {}
    Lateness = {}
    Excess = {}
    weightFactor = [10.0,1.0,0,2,0.5]
    Utilisation={}
    
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
    
    
    # output variables
    reportResults = tablib.Databook()
    OrderResults = tablib.Dataset(title='OrderSummary')
    OrderResults.headers = ('PPOS', 'SP_NUMBER', 'MA_LIST', 'REQUEST_DATE', 'DFSELLER', 'ORDERQTY', 'PRIORITY', 'CHOSEN_MA', 'LATENESS', 'EARLINESS', 'ALLOCATION')
    forecastResults = tablib.Dataset(title='ForecastSummary')
    forecastResults.headers = ('PPOS', 'SP_NUMBER', 'MA_LIST', 'REQUEST_DATE', 'ORDERQTY', 'PRIORITY', 'CHOSEN_MA', 'LATENESS', 'EARLINESS', 'ALLOCATION')
    globalMAAllocation = {}
    spForecastOrder = []
    CapacityResults = tablib.Dataset(title = 'BN_Capa')
    allocationResults = tablib.Dataset(title = 'Demand_coverage')
    
    
#    filterItem = 0
#    filterWeek = 0