'''
Created on 4 Jun 2014

@author: Panos
'''
'''
    XXX managers provided in the dictionary must agree with the operators provided in the UI
    XXX station name should be split, only the first part is of interest to us
'''

MACHINE_ID_SET=set(["CAD1","CAD2","CAD3","CAM1","CAM2","MILL1","MILL2","TURN1","DRILL1","EDM1","WORK1","WORK2","WORK3","WORK4","INJM1","INJM2"])
MANAGER_ID_SET=set(["PM1","PM2","PM3","PM4"])

import pyodbc
import ConnectionData
import datetime
'''the system time'''
now = datetime.datetime.utcnow()

def getTimeDiff(arg_time):
    '''get the time difference between the current clock and the argument provided in seconds'''
    time_in=arg_time
    if time_in.__class__.__name__=='date':
        time_in=datetime.datetime(year=time_in.year, month=time_in.month, day=time_in.day,)
    if time_in.__class__.__name__!='datetime' and not time_in==None:
        time_in=datetime.datetime.strptime(time_in,'%Y-%m-%d %H:%M:%S.%f')
    # XXX time difference must be a number. Though a typical value must be chosen in case the order is not finished yet
    time_diff=''
    if time_in:
        time_diff=((time_in-now)).total_seconds()
    return time_diff

def getID(arg_name, set):
    '''get the ID part of a string provided as argument in the form of <ID - NAME>'''
    name_in=arg_name
    name_parts=name_in.split(' - ')
    if len(name_parts)==1:
        name_parts=name_in.split('-')
    id=next(str(x) for x in name_parts if x in set)
    return id

def connectDB():
    try:
        db_info=ConnectionData.getConnectionInfo()
        cnxn=pyodbc.connect("DRIVER="+db_info[0]+";SERVER="+db_info[1]+";PORT="+db_info[2]+";DATABASE="+db_info[3]+";UID="+db_info[4]+";PASSWORD="+db_info[5]+"; ")
        cursor1 = cnxn.cursor()         # cursor that searches orders 
        cursor2 = cnxn.cursor()         # cursor that searches sequence for parts that have the same orderID
        cursor3 = cnxn.cursor()         # cursor that searches in sequence for rows with the same partID
        cursor4 = cnxn.cursor()         # cursor that searches in the join of prod_status and sequence having the same taskID for rows that have the same partID
        cursor5 = cnxn.cursor()         # cursor that searches sequence, prerequisites having the same taskID for rows of the same partID
        cursor6 = cnxn.cursor()         # cursor that searches the machines table
        
        data={}                         # dictionary that holds the Stations, the Wip, and the Orders
        data['orders']=[]               # Orders list
        data['WIP']={}                  # WIP dictionary
        data['stations']=[]             # stations list
        
        # Find the machines in the system
        mach_cur=cursor6.execute("""
                select MachineName, description
                from machines""")
        # for every order of the orders table
        for j in range(mach_cur.rowcount):
            #get the next line
            ind3=mach_cur.fetchone()
            data['stations'].append(getID(ind3.MachineName, MACHINE_ID_SET))
        
        order_cur=cursor1.execute("""
                select Order_id, ProjectName, Customer, Order_date, Due_date, ProjectManager
                from orders""")
        
        # for every order of the orders table
        for j in range(order_cur.rowcount):
            #get the next line
            ind0=order_cur.fetchone() 
            #and create a dictionary order
            order={}                    # each Order dictionary
            
            order['orderName']=str(ind0.ProjectName.encode('utf-8'))
            order['orderID']=str(ind0.Order_id)
            order['manager']=getID(ind0.ProjectManager,MANAGER_ID_SET)#str(ind0.ProjectManager)
            order['orderDate']=getTimeDiff(ind0.Order_date) #getTimeDiff(ind0.Order_date)
            order['dueDate']=getTimeDiff(ind0.Due_date)#getTimeDiff(ind0.Due_date)
            order['componentsList']=[]
            
            seq_cur=cursor2.execute("""
                        select Order_id, PartCode, PartName, Operation_Name, ProcessingTime, PersonnelCode, Quantity, step
                        from sequence where Order_id=?
                        """, ind0.Order_id)
            
            appended=[] # list that holds the already added components
            # for all the lines of c (every component)
            for i in range(seq_cur.rowcount):
                # create a comopnent dict
                component={}
                # and get the next row
                ind1=seq_cur.fetchone()
                code=ind1.PartCode
                component['componentID']=str(code)
                name=ind1.PartName
                component['componentName']=str(code+' '+name)
                quantity=ind1.Quantity
                component['quantity']=str(quantity)
                component['route']=[]
                
                step_cur=cursor3.execute("""
                        select  PartCode, PartName, Operation_Name, ProcessingTime, PersonnelCode, Quantity, step
                        from sequence
                        where PartCode=?
                        """, code)
                
                
                need_cur=cursor5.execute("""
                        select  sequence.WP_id, sequence.PartCode,  prerequisites.PartsNeeded
                        from sequence, prerequisites 
                        where sequence.WP_id=prerequisites.WP_id
                        AND sequence.PartCode=?
                        """, code)
                
                for line in range(step_cur.rowcount):
                    step={}
                    ind2=step_cur.fetchone()
                    step['technology']=str(ind2.Operation_Name)
                    step['sequence']=ind2.step
                    ind3=need_cur.fetchone()
                    step['parts_needed']=str(ind3.PartsNeeded)
                    step['processingTime']={}
                    step['processingTime']['distributionType']='Fixed' # Hard coded value, not extracted from the database
                    step['processingTime']['mean']=float(ind2.ProcessingTime)
                    component['route'].append(step)
                
                
                if not component['componentID'] in appended:
                    order['componentsList'].append(component)
                    appended.append(component['componentID'])
                    
                    wip_cur= cursor4.execute("""
                        select prod_status.WP_id, sequence.WP_id, MachineName, TIMEIN, TIMEOUT
                        from prod_status 
                        join sequence on sequence.WP_id = prod_status.WP_id
                        where sequence.PartCode=?
                        """, code)
                     
                    for x in range(wip_cur.rowcount):
                        ind2=wip_cur.fetchone()
                        for t in appended: 
                            data['WIP'][str(code)]={}
                            data['WIP'][str(code)]['station']=getID(ind2.MachineName,MACHINE_ID_SET)#str(ind2.MachineName)
                            data['WIP'][str(code)]['entry']=getTimeDiff(ind2.TIMEIN)
                            data['WIP'][str(code)]['exit']=getTimeDiff(ind2.TIMEOUT)
                                           
            data['orders'].append(order)
#         print data
        return data
    except:
        return False
# connectDB()