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

import Tkinter as tk
from Tkinter import *
import pyodbc
import tkMessageBox
from datetime import datetime
 
class Demo1( Frame ):
    def __init__( self ):
        tk.Frame.__init__(self)
        self.pack()
        self.master.title("JobShop Interface")
        
        self.labelText = StringVar()
        self.labelText.set('Please select one of the following options. \n Select TIME IN if you want to record the input time or TIME OUT if you want to record the exit time')
        self.label1 = Label(self, textvariable=self.labelText, height=2)
        self.label1.pack()
        
        self.Option = StringVar()
        self.Option.set(None)
        options = ['TIME IN', 'TIME OUT']
        self.OptionDropDown = OptionMenu(self, self.Option, *options).pack()
       
        self.button = Button(self, text="Click here to continue", command=self.optionClicked).pack()

    def optionClicked(self):
        if self.Option.get()=='TIME IN':
            self.new_window()
            
        elif self.Option.get()=='TIME OUT':
            self.new_window2()
            
    
    def new_window(self):
        self.newWindow = TIMEIN()
        
    
    def new_window2(self):
        self.newWindow = TIMEOUT()
        
    
    def close_window(self):
        self.destroy()

class TIMEIN(Frame):     
    def __init__(self):
        app = tk.Frame.__init__(self)
        app = Toplevel(self)
        app.title('JobShop Interface TIME IN')
        app.geometry('650x450+200+200')
        
        if not self.checkInsertedWP():
            self.labelText = StringVar()
            self.labelText.set('There is no new order inserted in the system, please insert one and try again')
            label5 = Label(app, textvariable=self.labelText, height=5)
            label5.pack()
        else:

            self.labelText = StringVar()
            self.labelText.set('Please follow the instructions to update the system. \n In case of administrative work, select your employee code and click below to record the START TIME')
            label1 = Label(app, textvariable=self.labelText, height=2)
            label1.pack()
    
            self.labelText = StringVar()
            self.labelText.set('1. Please select WP-ID')
            label2 = Label(app, textvariable=self.labelText, height=2)
            label2.pack()
            
            self.WPOption = StringVar()
            self.WPOption.set(None)
            options = self.checkInsertedWP()
            self.WPDropDown = OptionMenu(app, self.WPOption, *options).pack()
            
            self.labelText = StringVar()
            self.labelText.set('2. Please select your employee code')
            label3 = Label(app, textvariable=self.labelText, height=3)
            label3.pack()
            
            self.personnelOption = StringVar()
            self.personnelOption.set(None)
            options = ['W1-MB', 'W2-CV', 'W3-FS', 'W4-TD', 'W5-MG', 'W6-AA', 'W7-WK', 'Automatic']
            self.personnelDropDown = OptionMenu(app, self.personnelOption, *options).pack()
            
            
            self.labelText = StringVar()
            self.labelText.set('3. Please select the machine')
            label4 = Label(app, textvariable=self.labelText, height=4)
            label4.pack()
            
            self.machineOption = StringVar()
            self.machineOption.set(None)
            options = ['CAD1 - SolidWorks Pro', 'CAD2 - SolidWorks Base', 'CAD3 - CATIA V5', 'CAM1 - WorkNC 5axis', 'CAM2 - WorkNC 3axis', 'MILL1 - DMU50 eVo', 'MILL2 - HSC20 linear', 'TURN1 - EMCO', 'DRILL1 - FLOTT SB', 'EDM1- AGIE Form 20', 'WORK1 - Workbench 1', 'WORK2 - Workbench 2', 'WORK3 - Workbench 3', 'WORK4 - Workbench 4', 'INJM1 - SYSTEC 35', 'INJM2 - SYSTEC 120']
            self.machineDropDown = OptionMenu(app, self.machineOption, *options).pack()
            
            self.checkBoxVal = IntVar()
            checkBox1 = Checkbutton(app, variable=self.checkBoxVal, text='Click to record the TIME IN', height=3, command=self.recordTimeIn)
            checkBox1.pack()
            
            self.checkBoxVal = IntVar()
            checkBox1 = Checkbutton(app, variable=self.checkBoxVal, text='Click to record the START TIME of administrative work', height=2, command=self.recordStartTime)
            checkBox1.pack()
            
            self.labelText = StringVar()
            self.labelText.set('4. Please click here')
            label4 = Label(app, textvariable=self.labelText, height=2)
            label4.pack()
            
            self.button4 = Button(app, text='Update the system', width=20, command=self.updateDatabase)
            self.button4.pack()
            
    
    def recordTimeIn(self):
        self.timeIN = str(datetime.now())
        print self.timeIN
        return   

    def recordStartTime(self):
        self.startTime = str(datetime.now())
        print self.startTime
        return
    
    def checkInsertedWP(self):
        cnxn=pyodbc.connect("Driver={MySQL ODBC 3.51 Driver};SERVER=localhost; PORT=3306;DATABASE=leo_database2;UID=root;PASSWORD=Pitheos10;")
        cursor = cnxn.cursor()
        
        a=cursor.execute("""
                select WP_id, PartCode
                from sequence
                        """)
        
        availableWP=[]
        for j in range(a.rowcount):
            #get the next line
            ind1=a.fetchone() 
            #and create a dictionary order
            
            availableWP.append(ind1.WP_id)
        b=cursor.execute("""
                select WP_id
                from prod_status
                        """)
        lista=[]
        for j in range(b.rowcount):
            #get the next line
            ind1=b.fetchone() 
            #and create a dictionary order
            lista.append(ind1.WP_id)
            
        for elem in lista:
            if elem in availableWP:
                ind=availableWP.index(elem)
                del availableWP[ind]
            else:
                continue
        return availableWP

    def updateDatabase(self):
        cnxn=pyodbc.connect("Driver={MySQL ODBC 3.51 Driver};SERVER=localhost; PORT=3306;DATABASE=bal_database;UID=root;PASSWORD=Pitheos10;")
        cursor = cnxn.cursor()
        update_order= ("INSERT INTO prod_status(`status_id`, `WP_id`, `PersonnelCode`, `MachineName`, `TIMEIN`)  VALUES (?, ?, ?, ?, ?)")
        cursor.execute("SELECT @@IDENTITY AS ID")
        a = cursor.execute("""
        select WP_id, Order_id
        from sequence where WP_id=?
                """, self.WPOption.get())
        order = a.fetchone()
        print order
        row = cursor.fetchone()
        order_ref = row.ID
        status1 = 'in progress'
        cursor.execute(update_order, (order_ref, self.WPOption.get(), self.personnelOption.get(), self.machineOption.get(), str(datetime.now())))
        cursor.execute("UPDATE orders SET `Status`=? WHERE Order_id=? ", status1, order) 
        cursor.commit()
        self.close_window()
        return
    
    def close_window(self):
        self.destroy()


class TIMEOUT(Frame):
    def __init__(self):
        app = tk.Frame.__init__(self)
        app = Toplevel(self)
        app.title('JobShop Interface TIME OUT')
        app.geometry('550x400+200+200')
        
        if not self.checkInsertedWP():
            self.labelText = StringVar()
            self.labelText.set('There is no WP-id inserted in the system, \n please use first the TIMEIN window to insert one and then try again')
            label3 = Label(app, textvariable=self.labelText, height=5)
            label3.pack()
        else:
            self.labelText = StringVar()
            self.labelText.set('Please follow the instructions to update the system. \n In case of administrative work, select your employee code and click below to record the FINISH TIME')
            label1 = Label(app, textvariable=self.labelText, height=2)
            label1.pack()
            
            self.labelText = StringVar()
            self.labelText.set('1. Please select WP-ID')
            label2 = Label(app, textvariable=self.labelText, height=2)
            label2.pack()
            
            self.WPOption = StringVar()
            self.WPOption.set(None)
            options = self.checkInsertedWP()
            self.WPDropDown = OptionMenu(app, self.WPOption, *options).pack()
                    
            self.checkBoxVal = IntVar()
            checkBox1 = Checkbutton(app, variable=self.checkBoxVal, text='Click to record the TIME OUT', height=3, command=self.recordTimeIn)
            checkBox1.pack()
            
            self.labelText = StringVar()
            self.labelText.set('4. Please select WP-ID status')
            label4 = Label(app, textvariable=self.labelText, height=2)
            label4.pack()
            
            self.statusOption = StringVar()
            self.statusOption.set(None)
            options = ['in progress', 'auto-complete -->', 'auto-complete', 'complete for next step -->', 'complete']
            self.statusDropDown = OptionMenu(app, self.statusOption, *options).pack()
            
            self.checkBoxVal = IntVar()
            checkBox1 = Checkbutton(app, variable=self.checkBoxVal, text='Click to record the FINISH TIME of administrative work', height=2, command=self.recordStartTime)
            checkBox1.pack()
            
            self.labelText = StringVar()
            self.labelText.set('5. Please insert any comments')
            label2 = Label(app, textvariable=self.labelText, height=2)
            label2.pack()
            
            self.remark = StringVar(None)
            self.comments = Entry(app, textvariable=self.remark)
            self.comments.pack()
            
            self.labelText = StringVar()
            self.labelText.set('6. Please click here once')
            label4 = Label(app, textvariable=self.labelText, height=2)
            label4.pack()
            
            self.button1 = Button(app, text='Update the system', width=20, command=self.updateDatabase)
            self.button1.pack()

    def recordTimeIn(self):
        self.timeIN = str(datetime.now())
        print self.timeIN
        return   
    
    def recordStartTime(self):
        self.startTime = str(datetime.now())
        print self.startTime
        return
    
    def checkInsertedWP(self):
        cnxn=pyodbc.connect("Driver={MySQL ODBC 3.51 Driver};SERVER=localhost; PORT=3306;DATABASE=bal_database;UID=root;PASSWORD=Pitheos10;")
        cursor = cnxn.cursor()
        
        b=cursor.execute("""
                select WP_id
                from prod_status
                        """)
        insertedWP=[]
        for j in range(b.rowcount):
            #get the next line
            ind1=b.fetchone() 
            #and create a dictionary order
            insertedWP.append(ind1.WP_id)
        
        finishedWP=[]
        
        c=cursor.execute("""
            select WP_id, TIMEIN, TIMEOUT
            from prod_status
                    """)
        for j in range(c.rowcount):
            #get the next line
            ind2=c.fetchone() 
            #and create a dictionary order
            if ind2.TIMEOUT:
                finishedWP.append(ind2.WP_id)
            else:
                continue
        
        for elem in finishedWP:
            if elem in insertedWP:
                ind=insertedWP.index(elem)
                del insertedWP[ind]
            else:
                continue
        return insertedWP
    
    def updateDatabase(self):
        cnxn=pyodbc.connect("Driver={MySQL ODBC 3.51 Driver};SERVER=localhost; PORT=3306;DATABASE=bal_database;UID=root;PASSWORD=Pitheos10;")
        cursor = cnxn.cursor()
        a = cursor.execute("""
        select WP_id, Order_id
        from sequence where WP_id=?
                """, self.WPOption.get())
        order = a.fetchone()[1]
        b = cursor.execute("""
        select WP_id, Order_id, PartName
        from sequence where Order_id=?
                """, order)
        for j in range(b.rowcount):
            ind1=b.fetchone() 
        lastWP = ind1.WP_id
        status2 = 'finished'
        completed='TRUE'
        cursor.execute("UPDATE sequence SET `Completed`=? WHERE WP_id=? ", completed , self.WPOption.get() )
        cursor.execute("UPDATE prod_status SET `TIMEOUT`=? ,  `statusName`=? , `Remarks`=? WHERE WP_id=? ", str(datetime.now()), self.statusOption.get(), self.comments.get(), self.WPOption.get() )
        if self.WPOption.get() == lastWP:
            cursor.execute("UPDATE orders SET `Status`=? WHERE Order_id=? ", status2, order)    
        cursor.commit()
        self.close_window()
        return
    
    def close_window(self):
        self.destroy()


def main(): 
    Demo1().mainloop()

if __name__ == '__main__':
    main()