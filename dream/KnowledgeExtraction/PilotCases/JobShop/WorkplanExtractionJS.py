'''
Created on 9 Apr 2015

@author: Panos
'''
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

import xlrd
import datetime
import os
import pyodbc   
#Static variables that hold the column's number in Workplan (Excel document - template)
WPColumn=14
OrderColumn=0
ProjectColumn=2
PartsNeeded=13
#Method created to extract the required data from the spreadsheet
def dataExtraction(File):
    # loop through all the sheets
    for sheet in xls_workbook.sheets():
        if sheet.name=='Workplan':
            orderId=sheet.cell(4,0).value
            customer=sheet.cell(4,1).value
            projectName=sheet.cell(4,2).value
            orderDate=datetime.datetime.utcfromtimestamp((sheet.cell(4,3).value - 25569) * 86400.0)
            dueDate=datetime.datetime.utcfromtimestamp((sheet.cell(4,4).value - 25569) * 86400.0)
            projectManager=sheet.cell(4,5).value
            #create a dictionary called workplan with key the order id 
            workplan[orderId]={}
            workplan[orderId][projectName]=[]
            workplan[orderId][projectName].insert(0, customer)
            workplan[orderId][projectName].insert(1, orderDate)
            workplan[orderId][projectName].insert(2, dueDate)
            workplan[orderId][projectName].insert(4, projectManager)
            #loop in the rows of the spreadsheet
            for i in range(4,sheet.nrows):
                if sheet.cell(i,14).value:
                    wpId=sheet.cell(i,14).value
                    partId=sheet.cell(i,6).value
                    partType=sheet.cell(i,7).value
                    operation=sheet.cell(i,8).value
                    step=sheet.cell(i,9).value
                    personnel=sheet.cell(i,10).value
                    quantity=sheet.cell(i,11).value
                    procTime=sheet.cell(i,12).value
                    partsNeeded=sheet.cell(i,13).value
                    
                    workplan[orderId][wpId]=[]
                    workplan[orderId][wpId].insert(0, partId)
                    workplan[orderId][wpId].insert(1, partType)
                    workplan[orderId][wpId].insert(2, operation)
                    workplan[orderId][wpId].insert(3, step)
                    workplan[orderId][wpId].insert(4, personnel)
                    workplan[orderId][wpId].insert(5, quantity)
                    workplan[orderId][wpId].insert(6, procTime)
                    workplan[orderId][wpId].insert(7, partsNeeded)

os.chdir("C:\Users\Panos\Documents\DB_Approach\JobShop\Workplans")
#create a list that hold the already inserted orders
alreadyInserted=[]
#use of the KE tool object to connect to database
cnxn=pyodbc.connect("Driver={MySQL ODBC 3.51 Driver};SERVER=localhost; PORT=3306;DATABASE=leo_database2;UID=root;PASSWORD=Pitheos10;")
cursor = cnxn.cursor()
#loop that searches the files in the given directory 
for fileName in os.listdir("."):
    print fileName
    #using the xlrd python library, we open the documents
    xls_workbook = xlrd.open_workbook(fileName)
    #define Main the first sheet - sheet with the name 'Workplan'
    Main= xls_workbook.sheet_by_name('Workplan')
    workplan={}
    #SQL query to extract data from orders table
    check_order= cursor.execute("""
                        select Order_id, ProjectName, Customer, Order_date, Due_date, ProjectManager, Status
                        from orders
                                """)
    #check if rowcount is 0, if it is move on - otherwise go to the else part
    if check_order.rowcount==0:
        #call the method giving as argument the document
        dataExtraction(fileName)                     
        for i in range(4,Main.nrows):
            orderId=Main.cell(4,OrderColumn).value 
            projectName=Main.cell(4,ProjectColumn).value
        #Another SQL query to input data this time in the database in orders table         
        add_order= ("INSERT INTO orders(`id`, `Order_id`, `ProjectName`, `Customer`, `Order_date`, `Due_date`, `ProjectManager`, `Status`)  VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
                    
        cursor.execute("SELECT @@IDENTITY AS ID")
                    
        row = cursor.fetchone()
        order_ref = row.ID
        status= 'accepted'
        #the following data inserted to the the database based on the structure of the query above             
        cursor.execute(add_order, (order_ref, orderId, projectName, workplan[orderId][projectName][0], workplan[orderId][projectName][1], workplan[orderId][projectName][2], workplan[orderId][projectName][3], status))
        cursor.commit()            
        #SQL query to input data in the database in sequence table            
        add_sequence= ("INSERT INTO sequence(`seq_id`, `WP_id`, `Order_id`, `PartCode`, `PartName`, `Operation_Name`, `ProcessingTime`, `step`, `PersonnelCode`, `Quantity`)  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ")
                    
        cursor.execute("SELECT MAX(seq_id)+1 AS ID from sequence")
        seq_ref = row.ID
        #loop used to insert the required data based on the structure of the above query            
        for i in range(4,Main.nrows):
            wpId=Main.cell(i,WPColumn).value
            cursor.execute(add_sequence, (seq_ref, wpId, orderId, workplan[orderId][wpId][0], workplan[orderId][wpId][1], workplan[orderId][wpId][2], workplan[orderId][wpId][6], workplan[orderId][wpId][3], workplan[orderId][wpId][4], workplan[orderId][wpId][5]))
            cursor.commit()
            seq_ref+=1
                        
        add_prerequisites=("INSERT INTO prerequisites(`pre_id`, `Order_id`, `WP_id`, `PartCode`, `PartsNeeded`)  VALUES (?, ?, ?, ?, ?) ")    
        cursor.execute("SELECT MAX(pre_id)+1 AS ID from prerequisites")
        pre_ref = row.ID
                     
        for i in range(4,Main.nrows):
            wpId=Main.cell(i,WPColumn).value
            cursor.execute(add_prerequisites, (pre_ref, orderId, wpId, workplan[orderId][wpId][0], workplan[orderId][wpId][7]))
            cursor.commit()               
    else:
        #follows the logic of the if part
        check_order= cursor.execute("""
                        select Order_id, ProjectName, Customer, Order_date, Due_date, ProjectManager, Status
                        from orders
                                """)
        for j in range(check_order.rowcount):
            #get the next line
            ind1=check_order.fetchone()
            dataExtraction(fileName)              
            for i in range(4,Main.nrows):
                orderId=Main.cell(4,OrderColumn).value 
                projectName=Main.cell(4,ProjectColumn).value
            #check the existence of orderId
            if not orderId in ind1.Order_id:
                add_order= ("INSERT INTO orders(`id`, `Order_id`, `ProjectName`, `Customer`, `Order_date`, `Due_date`, `ProjectManager`, `Status`)  VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
                    
                cursor.execute("SELECT MAX(id)+1 AS ID from orders")
                    
                row = cursor.fetchone()
                order_ref = row.ID
                status= 'accepted'
                cursor.execute(add_order, (order_ref, orderId, projectName, workplan[orderId][projectName][0], workplan[orderId][projectName][1], workplan[orderId][projectName][2], workplan[orderId][projectName][3], status))
                cursor.commit()    
                    
                add_sequence= ("INSERT INTO sequence(`seq_id`, `WP_id`, `Order_id`, `PartCode`, `PartName`, `Operation_Name`, `ProcessingTime`, `step`, `PersonnelCode`, `Quantity`)  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ")
                cursor.execute("SELECT MAX(seq_id)+1 AS ID from sequence")
                row = cursor.fetchone()
                seq_ref = row.ID
                    
                for i in range(4,Main.nrows):
                    wpId=Main.cell(i,WPColumn).value
                    cursor.execute(add_sequence, (seq_ref, wpId, orderId, workplan[orderId][wpId][0], workplan[orderId][wpId][1], workplan[orderId][wpId][2], workplan[orderId][wpId][6], workplan[orderId][wpId][3], workplan[orderId][wpId][4], workplan[orderId][wpId][5]))
                    cursor.commit()
                    seq_ref+=1
                        
                add_prerequisites=("INSERT INTO prerequisites(`pre_id`, `Order_id`, `WP_id`, `PartCode`, `PartsNeeded`)  VALUES (?, ?, ?, ?, ?) ")    
                cursor.execute("SELECT MAX(pre_id)+1 AS ID from prerequisites")
                row = cursor.fetchone()
                pre_ref = row.ID
                     
                for i in range(4,Main.nrows):
                    wpId=Main.cell(i,WPColumn).value
                    cursor.execute(add_prerequisites, (pre_ref, orderId, wpId, workplan[orderId][wpId][0],workplan[orderId][wpId][7]))
                    cursor.commit()
                    pre_ref +=1
            else:
                continue