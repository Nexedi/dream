'''
Created on 24 Aug 2015

@author: Panos
'''
import xlrd

# columns that are used (static)
CONTAINERNAME=0
STATIONNAME=16
WORKCELL=17

def findStation(dictStory):
    for key,value in dictStory.iteritems():
        if value[0]=="Proximal Balloon Attach-CREFW" and value[1]=="CRE FW FRONT END LINE 1":
            dictStory[key]="2_P_B_A_A"
        elif value[0]=="Proximal Balloon Attach-CREFW" and value[1]=="CRE FW FRONT END LINE 2":
            dictStory[key]="2_P_B_A_B"
        elif value[0]=="RO/Exit Marker-CREFW" and value[1]=="CRE FW FRONT END LINE 1":
            dictStory[key]="1_RO_E_M_A_A"
        elif value[0]=="RO/Exit Marker-CREFW" and value[1]=="CRE FW FRONT END LINE 2":
            dictStory[key]="1_RO_E_M_A_B"
        elif value[0]=="Distal Balloon Attach-CREFW" and value[1]=="CRE FW FRONT END LINE 1":
            dictStory[key]="3_D_B_A_A"
        elif value[0]=="Distal Balloon Attach-CREFW" and value[1]=="CRE FW FRONT END LINE 2":
            dictStory[key]="3_D_B_A_B"
        elif value[0]=="Carding Cell-CREFW":
            dictStory[key]="8_Carding"    
        elif value[0]=="Flag Label Attach-CREFW":
            dictStory[key]="6_Flag Labelling"
        elif value[0]=="Pressure Test-CREFW" and value[1]=="CRE FW BACK END LINE 2":
            dictStory[key]="7_Pressure B"
        elif value[0]=="Pressure Test-CREFW" and value[1]=="CRE FW BACK END LINE 1":
            dictStory[key]=[]
            dictStory[key]="7_Pressure A"
        elif value[0]=="Moulding Cell-CREFW":
            dictStory[key]="5_Moulding"
        elif value[0]=="Cut and Bend Corewire":
            dictStory[key]="4_Cut & Bend"
        elif value[0]=="Fixed Wire Pack Cell 1-CREFW" and value[1]=="CRE FW BACK END LINE 1":
            dictStory[key]="9_Packaging A"
        elif value[0]=="Fixed Wire Pack Cell 2-CRE" and value[1]=="CRE FW BACK END LINE 2":
            dictStory[key]="9_Packaging B"

    return dictStory

def main(input):
    #Read from the given directory the Excel document with the input data
    # workbook = xlrd.open_workbook('WIP_test report.xls')
    
    mime_type, attachement_data = input[len('data:'):].split(';base64,', 1)
    attachement_data = attachement_data.decode('base64')
    workbook = xlrd.open_workbook(file_contents=attachement_data)
    
    worksheets = workbook.sheet_names()
    main= workbook.sheet_by_name('WIP & Static Detail Section') 
    worksheet_WIP = worksheets[0]     #Define the worksheet with the production data      
        
    contIds=[]
    contDetails={}
    for sheet in workbook.sheets():
        if worksheet_WIP:
            for i in range(1,main.nrows):
                Id=main.cell(i,CONTAINERNAME).value
                if not Id in contIds:
                    contIds.append(Id) 
                contDetails[Id]=[] 
                statName=main.cell(i,STATIONNAME).value
                workcell=main.cell(i,WORKCELL).value
                contDetails[Id].append(statName)
                contDetails[Id].append(workcell)
            
    return findStation(contDetails)




               
        
        