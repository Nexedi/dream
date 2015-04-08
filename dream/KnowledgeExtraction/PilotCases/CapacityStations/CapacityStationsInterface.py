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
Created on 20 March 2015

@author: Panos
'''

import Tkinter as tk
from Tkinter import *
from dream.KnowledgeExtraction.ImportDatabase import ConnectionData
import tkMessageBox
from datetime import datetime 

class Demo1(Frame):     
    def __init__(self):
        tk.Frame.__init__(self)
        self.pack()
        self.master.title("CapacityStations Interface")
        
        if not self.checkInsertedProject():
            self.labelText = StringVar()
            self.labelText.set('There is no new order inserted in the system, please insert one and try again')
            label5 = Label(self, textvariable=self.labelText, height=5)
            label5.pack()
        else:
            self.labelText = StringVar()
            self.labelText.set('Please follow the instructions to update the system.')
            label1 = Label(self, textvariable=self.labelText, height=2)
            label1.pack()
    
            self.labelText = StringVar()
            self.labelText.set('1. Please select order')
            label2 = Label(self, textvariable=self.labelText, height=2)
            label2.pack()
            
            self.OrderOption = StringVar()
            self.OrderOption.set(None)
            options = self.checkInsertedProject()
            self.ProjectDropDown = OptionMenu(self, self.OrderOption, *options).pack()
                
            self.labelText = StringVar()
            self.labelText.set('2. Please select the operation')
            label4 = Label(self, textvariable=self.labelText, height=2)
            label4.pack()
            
            self.operationOption = StringVar()
            self.operationOption.set(None)
            options = ['SMF', 'WELD', 'CNC', 'MCH', 'EEP', 'PPASB', 'PAINT', 'ASBTST']
            self.operationDropDown = OptionMenu(self, self.operationOption, *options).pack()
             
            self.labelText = StringVar()
            self.labelText.set('3. Please click below only once, when you insert a WP_id. \n If you have already clicked, please go to next step no 4')
            label6 = Label(self, textvariable=self.labelText, height=2)
            label6.pack()
            
            self.checkBoxVal1 = IntVar()
            checkBox1 = Checkbutton(self, variable=self.checkBoxVal1, text='Click to record the START DATE', height=3, command=self.recordStartDate)
            checkBox1.pack()
            self.labelText = StringVar()
            
            self.labelText.set('4. Please insert estimated capacity left, to be completed')
            label6 = Label(self, textvariable=self.labelText, height=2)
            label6.pack()
            
            self.capleft = StringVar(None)
            self.capacity = Entry(self, textvariable=self.capleft)
            self.capacity.pack()
            
            self.labelText = StringVar()
            self.labelText.set('5. Please insert any comments')
            label2 = Label(self, textvariable=self.labelText, height=2)
            label2.pack()
            
            self.remark = StringVar(None)
            self.comments = Entry(self, textvariable=self.remark)
            self.comments.pack()
            
            self.labelText = StringVar()
            self.labelText.set('6. Please click below only when the operation finished')
            label6 = Label(self, textvariable=self.labelText, height=2)
            label6.pack()
            
            self.checkBoxVal2 = IntVar()
            checkBox = Checkbutton(self, variable=self.checkBoxVal2, text='Click to record the END DATE', height=3, command=self.recordEndDate)
            checkBox.pack()
            
            self.labelText = StringVar()
            self.labelText.set('7. Please update the system clicking the button below')
            label6 = Label(self, textvariable=self.labelText, height=2)
            label6.pack()
            
            self.button4 = Button(self, text='Update the system', width=20, command=self.updateDatabase)
            self.button4.pack()
        
    def recordStartDate(self):
        self.startdate = str(datetime.now())
        print self.startdate
        return
    
    def recordEndDate(self):
        self.endDate = str(datetime.now())
        print self.endDate
        return   
       
    def checkInsertedProject(self):
        cnxn=ConnectionData(seekName='ServerData', file_path='C:\Users\Panos\Documents\DB_Approach\CapacityStations', implicitExt='txt', number_of_cursors=6)
        cursor=cnxn.getCursors()
        
        a=cursor[0].execute("""
                select Order_id, ProjectName, Status
                from orders
                        """)
        
        availableProject=[]
        for j in range(a.rowcount):
            #get the next line
            ind1=a.fetchone() 
            #and create a dictionary order
            if ind1.Status == 'in progress' or ind1.Status =='accepted':
                availableProject.append(ind1.Order_id)
        return availableProject
    
    def alreadyInsertedWP(self):
        cnxn=ConnectionData(seekName='ServerData', file_path='C:\Users\Panos\Documents\DB_Approach\CapacityStations', implicitExt='txt', number_of_cursors=6)
        cursor=cnxn.getCursors()
        
        c=cursor[0].execute("""
                select WP_id, END_DATE
                from production_status
                        """)
        listb=[]
        for i in range(c.rowcount):
            ind=c.fetchone()
            if ind.WP_id:
                listb.append(ind.WP_id)
            else:
                continue
        return    
    

    def updateDatabase(self):
        cnxn=ConnectionData(seekName='ServerData', file_path='C:\Users\Panos\Documents\DB_Approach\CapacityStations', implicitExt='txt', number_of_cursors=13)
        cursor=cnxn.getCursors()
        
        if self.checkBoxVal2.get():
            update_order= ("INSERT INTO production_status(`status_id`, `WP_id`, `Operation_Name`, `START_DATE`, `Capacity_left`, `Remarks`,`END_DATE`)  VALUES ( ?, ?, ?, ?, ?, ?, ?)") 
            cursor[0].execute("SELECT @@IDENTITY AS ID")
            order = self.OrderOption.get()
            a = cursor[1].execute("""
                        select WP_id, Order_id
                        from sequence where Order_id=?
                                """, order)
            for j in range(a.rowcount):
                ind2=a.fetchone() 
            lastWP =ind2.WP_id
            b = cursor[2].execute("""
                                select WP_id
                                 from sequence where Operation_Name=? and Order_id=?
                                """, self.operationOption.get(),order)
            ind4=b.fetchone()
            status2 = 'finished'
            row = cursor[0].fetchone()
            WP=ind4[0]
            order_ref = row.ID
            status1 = 'in progress'
            cursor[4].execute(update_order, (order_ref, WP, self.operationOption.get(), str(datetime.now()), self.capacity.get(), self.comments.get(),str(datetime.now()) ))
            if WP == lastWP:
                cursor[5].execute("UPDATE orders SET `Status`=? WHERE Order_id=? ", status2, order)
            cursor[6].commit()
            self.close_window() 
        else: 
            update_order= ("INSERT INTO production_status(`status_id`, `WP_id`, `Operation_Name`, `START_DATE`, `Capacity_left`, `Remarks`)  VALUES ( ?, ?, ?, ?, ?, ?)") 
        
            cursor[7].execute("SELECT @@IDENTITY AS ID")
            order = self.OrderOption.get()
            a = cursor[8].execute("""
                                select sequence.WP_id, sequence.Order_id, sequence.Operation_Name
                                 from sequence where Order_id=? and Operation_Name=?
                                """, order, self.operationOption.get())
            ind3=a.fetchone()
            WP=ind3.WP_id 
            row = cursor[7].fetchone()
            order_ref = row.ID
            status1 = 'in progress'
            cursor[10].execute(update_order, (order_ref, WP, self.operationOption.get(), str(datetime.now()), self.capacity.get(), self.comments.get()))
            cursor[11].execute("UPDATE orders SET `Status`=? WHERE Order_id=? ", status1, order)
            cursor[12].commit()
            self.close_window()
        return
    
    def close_window(self):
        self.destroy()

def main(): 
    Demo1().mainloop()

if __name__ == '__main__':
    main()
    