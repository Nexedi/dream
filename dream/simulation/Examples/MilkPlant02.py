from dream.simulation.applications.MilkPlant.imports import *
from dream.simulation.imports import ExcelHandler, ExitJobShop
from dream.simulation.Globals import runSimulation
import time

start=time.time()
# how many liters is one milk pack
milkUnit=1.0

T1=MilkTank('T1','T1',capacity=3200/float(milkUnit))
T2=MilkTank('T2','T2',capacity=2600/float(milkUnit))
T3=MilkTank('T3','T3',capacity=7000/float(milkUnit))
TBM2=MilkTank('TBM2','Tank Before F',capacity=float('inf'))
TAM2=MilkTank('TAM2','Tank After F',capacity=float('inf'))
TBM3=MilkTank('TBM3','Tank Before W',capacity=float('inf'))
TAM3=MilkTank('TAM3','Tank After W',capacity=float('inf'))

Tr1=MilkTransport('Tr1','Tr1')
Tr2=MilkTransport('Tr2','Tr2')
Tr3=MilkTransport('Tr3','Tr3')
Tr4=MilkTransport('Tr4','Tr4')
Tr5=MilkTransport('Tr5','Tr5')

M2=MilkProcess('M2','F')
M3=MilkProcess('M3','W')

E=MilkExit('E','Exit')

route1=[{"stationIdsList": ["T1"]},
         {"stationIdsList": ["Tr1"],"processingTime":{'Fixed':{'mean':0.034682*milkUnit}}}]

route2=[{"stationIdsList": ["T3"]},
         {"stationIdsList": ["Tr3"],"processingTime":{'Fixed':{'mean':0.222222*milkUnit}}}]

commonRoute=[{"stationIdsList": ["T2"]},
         {"stationIdsList": ["Tr2"],"processingTime":{'Fixed':{'mean':0.03*milkUnit}},'volume':1000},
         {"stationIdsList": ["TBM2"]},
         {"stationIdsList": ["M2"],"processingTime":{'Fixed':{'mean':180}},'volume':1000},
         {"stationIdsList": ["TAM2"]},
         {"stationIdsList": ["Tr4"],"processingTime":{'Fixed':{'mean':0.06*milkUnit}},'volume':1000},
         {"stationIdsList": ["TBM3"]},
         {"stationIdsList": ["M3"],"processingTime":{'Fixed':{'mean':20}},'volume':1000},
         {"stationIdsList": ["E"]}]

MPList=[]       
for i in range(int(865/float(milkUnit))):
    MP=MilkPack('MT_A'+str(i),'MT_A'+str(i),route=route1+commonRoute,liters=milkUnit,fat=3.8*milkUnit,productId='Product X')
    MPList.append(MP)
     
for i in range(int(135/float(milkUnit))):
    MP=MilkPack('MT_B'+str(i),'MT_B'+str(i),route=route2+commonRoute,liters=milkUnit,fat=0.1*milkUnit,productId='Product X')
    MPList.append(MP)
        
runSimulation([T1,T2,T3,TBM2,TAM2,TBM3,TAM3,Tr1,Tr2,Tr3,Tr4,Tr5,M2,M3,E]+MPList, 1000,trace='Yes')
ExcelHandler.outputTrace('MilkPlant2')

for  productId in E.finishedProductDict:
    volume=E.finishedProductDict[productId]['volume']
    totalFat=E.finishedProductDict[productId]['totalFat']
    exitTime=E.finishedProductDict[productId]['exitTime']
    fat=totalFat/float(volume)
    print 'from', productId, volume, 'liters were produced of', fat, '% fat. Product ready at t=',exitTime
    
print 'Execution Time=',time.time()-start