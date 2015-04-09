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

import json
import dream.KnowledgeExtraction.ImportDatabase as ImportDatabase 

def DataExtraction(DBFilePath):
    cnxn=ImportDatabase.ConnectionData(seekName='ServerData', file_path=DBFilePath,implicitExt='txt', number_of_cursors=6)
    cursor=cnxn.getCursors()
    
    #create a dictionary data
    data={}
    #create list inside data dictionary that holds generic order's attributes
    data['orders']=[]
    #create dictionary inside data dictionary that holds the WIP
    data['WIP']={}
    #create dictionary inside data dictionary that holds the available weekly operation capacity
#     data['operations']={}
    #SQL query that extracts info form operations table
    b=cursor[0].execute("""
            select OperationName, description
            from operations
                    """)
    # for every operation of the operations table
    for j in range(b.rowcount):
        #create a dictionary order
        order={}
        #get the next line
        ind1=b.fetchone() 
        process=ind1.OperationName
#         
    ###### Find the capacity ratio between SMF and WELD ######
    #SQL query in sequence table to extract the capacity required from each operation    
    f=cursor[2].execute("""
                select WP_id, Operation_Name, CapacityRequirement, EarliestStart
                from sequence
                        """)
    #create a list called capacity
    capacity=[]
    #for every line in sequence table 
    for j in range(f.rowcount):
        #get the next line
        ind4=f.fetchone()
        #insert in capacity list the capacity required by each operation
        capacity.append(ind4.CapacityRequirement)
    #create variable that holds the calculation of the capacity ratio between SMF and WELD    
    key= capacity[1]/float(capacity[0])
    
    #SQL query in orders table to extract generic info referring to each order    
    a=cursor[3].execute("""
                select Order_id, ProjectName, Customer, Order_date, Due_date, FloorSpaceRequired, Status
                from orders
                        """)
    #for every order in orders table   
    for i in range(a.rowcount):
        #create order disctionary
        order={}
        ind3=a.fetchone()
        status = ind3.Status
        #check order's status and move on if it's either 'accepted or 'in progress'
        if status == 'accepted' or status == 'in progress':
            #insert the following keys in order dictionary, keys referring to generic order's information
            order['orderName']=ind3.ProjectName
            order['orderID']=ind3.Order_id
            order['customer']=ind3.Customer
            order['orderDate']=str(ind3.Order_date)
            order['dueDate']=str(ind3.Due_date)
            order['floorSpaceRequired']=ind3.FloorSpaceRequired
            order['sequence']=[]
        #if order's status is 'finished', then continue to the next one    
        elif status == 'finished':
            continue
        #append order dictionary in data['orders'] list
        data['orders'].append(order)    
        #SQL query that extracts data from sequence table where order is ind3.Order_id - given by the last query  
        d=cursor[4].execute("""
                    select WP_id, Operation_Name, CapacityRequirement, EarliestStart
                    from sequence where Order_id=?
                            """, ind3.Order_id)        
        #for every line in sequence table
        
        for j in range(d.rowcount):
            #create step dictionary 
            step={}
            ind4=d.fetchone()
            process=ind4.Operation_Name
            orderID=ind3.Order_id
            task=ind4.WP_id
            #create another dictionary in step dictionary and insert the following attributes
            step[process]={}
            step[process]['task_id']=task
            step[process]['operation']=ind4.Operation_Name
            step[process]['requiredCapacity']=ind4.CapacityRequirement
            step[process]['earliestStart']=str(ind4.EarliestStart)
            order['sequence'].append(step)
            if status == 'accepted' or status =='in progress':
                if process == 'SMF':
                    data['WIP']['startBuffered.SMF_id' + orderID]={}
                    data['WIP']['startBuffered.SMF_id' + orderID]['operation']=process
                    data['WIP']['startBuffered.SMF_id' + orderID]['buffered']=ind4.CapacityRequirement
                    data['WIP']['startBuffered.SMF_id' + orderID]['order_id']=ind3.Order_id
                elif process == 'CNC':
                    data['WIP']['startBuffered.CNC_id' + orderID]={}
                    data['WIP']['startBuffered.CNC_id' + orderID]['operation']=process
                    data['WIP']['startBuffered.CNC_id' + orderID]['buffered']=ind4.CapacityRequirement
                    data['WIP']['startBuffered.CNC_id' + orderID]['order_id']=ind3.Order_id
                elif process == 'MCH':
                    data['WIP']['startBuffered.MCH_id' + orderID]={}
                    data['WIP']['startBuffered.MCH_id' + orderID]['operation']=process
                    data['WIP']['startBuffered.MCH_id' + orderID]['buffered']=ind4.CapacityRequirement
                    data['WIP']['startBuffered.MCH_id' + orderID]['order_id']=ind3.Order_id
                elif process == 'EEP':
                    data['WIP']['startBuffered.EEP_id' + orderID]={}
                    data['WIP']['startBuffered.EEP_id' + orderID]['operation']=process
                    data['WIP']['startBuffered.EEP_id' + orderID]['buffered']=ind4.CapacityRequirement
                    data['WIP']['startBuffered.EEP_id' + orderID]['order_id']=ind3.Order_id   
            else:
                continue
        
    #SQL query that extracts data from production_status table, joining the sequence and production_status table in WP_id attribute, in order to retrieve that WIP
    e= cursor[5].execute("""
                     select production_status.WP_id, sequence.WP_id, sequence.Order_id, sequence.CapacityRequirement, production_status.Capacity_left, production_status.START_DATE, production_status.END_DATE, production_status.Operation_Name
                     from production_status 
                     join sequence on sequence.WP_id = production_status.WP_id
                """)
    #create a list that holds the performed operations 
    appended=[]
    #initiate the following indicators
    weldfinishedCap=0
    cncfinishedCap=0
    mchfinishedCap=0
    wipList= e.fetchall()
    #for every line in production_status table
    for x in range(e.rowcount):    
        ind5=wipList[x]
        task=ind5.WP_id      
        orderID=ind5.Order_id
        #create a dictionary inside data['WIP'] with keys the task id
        data['WIP'][task]={}
        #insert the following attributes extracted from the database 
        data['WIP'][task]['operation']=ind5.Operation_Name
        data['WIP'][task]['Start date']=str(ind5.START_DATE)
        data['WIP'][task]['Total Capacity required']=ind5.CapacityRequirement
        data['WIP'][task]['Capacity required']=ind5.Capacity_left
        data['WIP'][task]['order_id']=ind5.Order_id
        data['WIP'][task]['End date']=str(ind5.END_DATE)
        #check operation's name and if is one of the three in the list; create the actually non-existing dictionary that holds the WIP - buffered just before the PPASB assembly operation 
        if data['WIP'][task]['operation'] in ['CNC','WELD','MCH']:
            try:
                data['WIP']['PPASB_id' +  orderID]={}
            except KeyError:
                continue
        #check operation's name and if is a not yet finished SMF; create another 'fake' dict that holds the WIP buffered just before WELD
        if data['WIP'][task]['operation']=='SMF':  
            try:
                data['WIP']['WELD_id' +  orderID]={}
            except KeyError:
                continue
        if data['WIP'][task]['operation']=='PPASB':  
            try:
                data['WIP']['PAINT_id' +  orderID]={}
            except KeyError:
                continue
        if data['WIP'][task]['operation']=='EEP':  
            try:
                data['WIP']['ASBTST_id' +  orderID]={}
            except KeyError:
                continue
        #check capacity required for each task - if it's 0 then delete this task from WIP
        if data['WIP'][task]['Capacity required'] == 0:
            del data['WIP'][task]
            if ind5.Operation_Name not in appended:
                appended.append(ind5.Operation_Name)
    #for every line in production_status table                        
    for x in range(e.rowcount):
        ind5=wipList[x]
        orderID=ind5.Order_id
        task=ind5.WP_id   
        operation=ind5.Operation_Name
        #check ii operation is a not finished SMF then using the calculate using the relationship ratio between SMF and WELD the available capacity can start in WELD 
        if operation=='SMF' and not ind5.END_DATE:
            finishedCap= ind5.CapacityRequirement - ind5.Capacity_left
            startWELD = float(key) * float(finishedCap)
            try: 
                data['WIP']['WELD_id' +  orderID]['operation']='WELD'
                data['WIP']['WELD_id' +  orderID]['buffered']=startWELD
                data['WIP']['WELD_id' +  orderID]['order_id']=orderID
            except KeyError:
                continue
        elif operation=='SMF' and ind5.END_DATE:
            try:
                del data['WIP']['startBuffered.SMF_id' + orderID]

            except KeyError:
                continue    
        #check and if operation is WELD calculate first the finished capacity and then based on the status of CNC and MCH operations, the capacity buffered before the assembly station PPASB  
        if operation=='WELD':
            try:
                del data['WIP']['WELD_id' +  orderID]
                weldfinishedCap= ind5.CapacityRequirement - ind5.Capacity_left
                data['WIP']['PPASB_id' +  orderID ]['operation']='PPASB'
                data['WIP']['PPASB_id' +  orderID ]['order_id']=orderID
                if not ind5.END_DATE:
                    data['WIP'][task]['Capacity required']= startWELD - weldfinishedCap
                if cncfinishedCap or mchfinishedCap:
                    FinishedCap= weldfinishedCap + cncfinishedCap + mchfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap   
                elif not mchfinishedCap:
                    FinishedCap= cncfinishedCap + weldfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
                elif not cncfinishedCap:
                    FinishedCap= weldfinishedCap + mchfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
                else:
                    FinishedCap=weldfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
            except KeyError:
                continue
        #check and if operation is CNC calculate first the finished capacity and then based on the status of WELD and MCH operations, the capacity buffered before the assembly station PPASB  
        if operation=='CNC':
            try:
                cncfinishedCap= ind5.CapacityRequirement - ind5.Capacity_left
                del data['WIP']['startBuffered.CNC_id' + orderID]
                data['WIP']['PPASB_id' +  orderID ]['operation']='PPASB'
                data['WIP']['PPASB_id' +  orderID ]['order_id']=orderID
                if weldfinishedCap or mchfinishedCap:
                    FinishedCap= weldfinishedCap + cncfinishedCap + mchfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap   
                elif not mchfinishedCap:
                    FinishedCap= cncfinishedCap + weldfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
                elif not weldfinishedCap:
                    FinishedCap= cncfinishedCap + mchfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
                else:
                    FinishedCap=cncfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
            except KeyError:
                continue
        #check and if operation is MCH calculate first the finished capacity and then based on the status of CNC and WELD operations, the capacity buffered before the assembly station PPASB  
        if operation=='MCH':
            try:
                mchfinishedCap= ind5.CapacityRequirement - ind5.Capacity_left
                del data['WIP']['startBuffered.MCH_id' + orderID]
                data['WIP']['PPASB_id' +  orderID ]['operation']='PPASB'
                data['WIP']['PPASB_id' +  orderID ]['order_id']=orderID
                if weldfinishedCap or cncfinishedCap:
                    FinishedCap= weldfinishedCap + cncfinishedCap + mchfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap   
                elif not cncfinishedCap:
                    FinishedCap= mchfinishedCap + weldfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
                elif not weldfinishedCap:
                    FinishedCap= mchfinishedCap + cncfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
                else:
                    FinishedCap = mchfinishedCap
                    data['WIP']['PPASB_id' +  orderID ]['buffered']=FinishedCap
            except KeyError:
                continue 
        if operation=='EEP':
            try:
                eepfinishedCap= ind5.CapacityRequirement - ind5.Capacity_left
                data['WIP']['ASBTST_id' +  orderID ]['operation']='ASBTST'
                data['WIP']['ASBTST_id' +  orderID ]['order_id']=orderID
                data['WIP']['ASBTST_id' +  orderID ]['buffered']=eepfinishedCap
                del data['WIP']['startBuffered.EEP_id' + orderID]
            except KeyError:
                continue 
        if operation=='PPASB' and not ind5.END_DATE:
            try:
                ppasbfinishedCap= ind5.CapacityRequirement - ind5.Capacity_left
                del data['WIP']['PPASB_id' +  orderID ]
                data['WIP']['PAINT_id' +  orderID ]['operation']='PAINT'
                data['WIP']['PAINT_id' +  orderID ]['order_id']=orderID
                data['WIP']['PAINT_id' +  orderID ]['buffered']=ppasbfinishedCap
            except KeyError:
                continue 
        if operation=='PAINT' and not ind5.END_DATE:
            try:
                del data['WIP']['PAINT_id' +  orderID]
            except KeyError:
                continue   
        if operation=='ASBTST' and not ind5.END_DATE:
            try:
                del data['WIP']['ASBTST_id' +  orderID]
            except KeyError:
                continue        
    return data