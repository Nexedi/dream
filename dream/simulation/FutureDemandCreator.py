'''
Created on 3 Oct 2013

@author: Anna
'''

import xlrd
import json
from Globals import G

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
                print SP, PPOS
    
                # create item
                newItem = Job(orderID=order, MAid=MA, SPid=SP, PPOSid=PPOS, qty=orderQty, minQty=orderMinQty, origWeek=week, future=fut)
                G.Buffer[G.replication].append(newItem)
            
            if k == 0:
                G.PPOSprofile.append(pProf)
            else:
                G.FutureProfile.append(fProf)

