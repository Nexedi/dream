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
'''
Created on 27 Apr 2013

@author: Anna, George
'''
'''
module that creates the future demand and appends it to buffers
'''

import xlrd
import json
from Globals import G
from JobMA import JobMA

class FutureDemandCreator(): 
        
    def run(self):
        
        #create new buffers
        G.Buffer.append([])
        G.ExcessFutureBuffer.append([])
        G.ExcessFutureMinBuffer.append([])
        G.ExcessPPOSBuffer.append([])
        G.ExcessPPOSminBuffer.append([])
        
        # create output lists
        G.AllocationFuture.append([])
        G.FutureLateness.append(0)
        G.FutureEarliness.append(0)
        G.AllocationPPOS.append([])
        G.PPOSLateness.append(0)
        G.PPOSEarliness.append(0)
        
        G.Capacity = []
        wbin = xlrd.open_workbook('GUI/inputs.xlsx')
        sh = wbin.sheet_by_name('Capacity')
        nCols = sh.ncols
        assert(nCols == G.planningHorizon+1)
        capacity=[]
        for i in range(1,nCols):
            capacity.append(sh.col_values(i,2))
        G.Capacity = capacity   
        
        G.currentCapacity = G.Capacity

        
        # PPOS initial disaggregation profile
        G.demandFile = 'GUI/DemandProfile.xlsx'
        wbin = xlrd.open_workbook(G.demandFile)
        
        MAData=json.loads(G.argumentDictString)['argumentDict']['MAList']
        for k in range(2):
            if k == 0:
                #sh = wbin.sheet_by_name('PPOS_Profile')
                sh = wbin.sheet_by_name('PPOS')
                fut = 0
                pProf = []
            else:
                #sh = wbin.sheet_by_name('Future_Profile')
                sh = wbin.sheet_by_name('Future'+str(G.replication+1))
                fut = 1
                fProf = []
                 
            nRows = sh.nrows
            for i in range(1,nRows):
                order = int(sh.cell_value(i,0)) - 1
                MA = sh.cell_value(i,1)      # -1 in order to start from 0
                orderQty = float(sh.cell_value(i,2))
                orderMinQty = float(sh.cell_value(i,3))
                week = int(sh.cell_value(i,4)) - 1  
                 
                if k == 0:                
                    pProf.append([order+1, MA, orderQty, orderMinQty, week+1])
                elif k == 1:
                    fProf.append([order+1, MA, orderQty, orderMinQty, week+1])
                
                SP = MAData[str(MA)]['SP']
                PPOS = MAData[str(MA)]['PPOS']
    
                # create item
                newItem = JobMA(orderID=order, MAid=MA, SPid=SP, PPOSid=PPOS, qty=orderQty, minQty=orderMinQty, origWeek=week, future=fut)
                G.Buffer[G.replication].append(newItem)
            
            if k == 0:
                G.PPOSprofile.append(pProf)
            else:
                G.FutureProfile.append(fProf)

