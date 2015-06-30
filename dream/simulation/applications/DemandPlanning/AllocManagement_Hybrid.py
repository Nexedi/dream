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
Created on 15 Dec 2014

@author: Anna
'''

from AllocationRoutine_Final2 import AllocationRoutine_Final
from AllocationRoutine_Forecast import AllocationRoutine_Forecast
from Allocation_GA import Allocation_GA
from Allocation_ACO import Allocation_ACO
from Globals import G
import tablib
from copy import deepcopy

def AllocManagement_Hybrid(): 
    
    # allocate items based on type and priority level
    
    print G.priorityList 
    
    for priority in G.priorityList['order']:
        
        ACOresults = tablib.Dataset(title='ACO_'+'order'+'_'+str(priority))
        ACOresults.headers = ('Week', 'generation', 'replication', 'antID', 'excess', 'lateness', 'earliness', 'targetUtil', 'minUtil')

        # starting from first week in planning horizon, complete the allocation of all orders within the same priority group
        for week in G.WeekList:  
            
            if week in G.sortedOrders['order'][priority]:
                print 'order week', week 
                ACOresults = Allocation_ACO(week, G.sortedOrders['order'][priority][week],'order',ACOresults)          
        
        G.reportResults.add_sheet(ACOresults)
    
    print 'prio forecast', G.priorityList['forecast']
    for priority in G.priorityList['forecast']:
        
        print 'weeks', G.sortedOrders['forecast'][priority]
        for week in G.WeekList:    
            
            if  week in G.sortedOrders['forecast'][priority]:
                print 'forecast week', week               
                AllocationRoutine_Forecast(week, G.sortedOrders['forecast'][priority][week],'forecast')
            
                
        
def AllocManagement_Hybrid2(bestAnt): 
    
    # allocate items based on type and priority level
    
    for priority in G.priorityList['order']:
        
        ACOresults = tablib.Dataset(title='ACO_'+'order'+'_'+str(priority))
        ACOresults.headers = ('Week', 'generation', 'replication', 'antID', 'excess', 'lateness', 'earliness', 'targetUtil', 'minUtil')
        resAnt = {}
        # starting from first week in planning horizon, complete the allocation of all orders within the same priority group
        for week in G.WeekList:  
            
            if week in G.sortedOrders['order'][priority]:
                print 'order week', week 
                if G.ACO:
                    if G.ACOdefault:
                        G.popSize = int(0.75*len(G.sortedOrders['order'][priority][week]) - 0.75*len(G.sortedOrders['order'][priority][week])%2)
                        G.noGen = 20*G.popSize
                    ACOresults, anting = Allocation_ACO(week, G.sortedOrders['order'][priority][week],'order',ACOresults)  
                    z=resAnt.copy()
                    z.update(anting)
                    resAnt = deepcopy(z)
                else:
                    if bestAnt!=None:
                        AllocationRoutine_Final(week, G.sortedOrders['order'][priority][week],'order',bestAnt)        
                    else:
                        AllocationRoutine_Final(week, G.sortedOrders['order'][priority][week],'order',0)   
        
        if G.ACO:
            G.reportResults.add_sheet(ACOresults)        
            return resAnt
    
        else:
            return None


def AllocManagement_Hybrid2_Forecast():     
    
    print 'start forecast allocation'
    for priority in G.priorityList['forecast']:
        
        GAresults = tablib.Dataset(title='GA_'+'order'+'_'+str(priority))
        GAresults.headers = ('Week', 'generation', 'replication', 'antID', 'excess', 'lateness', 'earliness', 'targetUtil', 'minUtil','sequence')

        for week in G.WeekList:    
            
            if  week in G.sortedOrders['forecast'][priority]:
                print 'forecast week', week   
                
                itemList = G.sortedOrders['forecast'][priority][week]
                
                # if GA is required perform order sequence optimisation combined with internal LP optimisation
                if G.GA:
                    if G.GAdefault:
                        G.popSizeGA = int(0.75*len(G.sortedOrders['forecast'][priority][week]) - 0.75*len(G.sortedOrders['forecast'][priority][week])%2)
                        G.noGenGA = 20*G.popSizeGA
                        
                    GAresults = Allocation_GA(week,itemList,'forecast',GAresults)
                    
                # if GA is not require perform allocation with internal LP optimisation
                else: 
                    
                    # get the list of orders ID
                    orderList = {}
                    orderIDlist = []
                    for item in itemList:
                        orderList[item['orderID']]=item        
                        orderIDlist.append(item['orderID']) 

                    AllocationRoutine_Forecast(week,orderList,'forecast',{'seq':orderIDlist})
            
