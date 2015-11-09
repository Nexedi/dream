from dream.simulation.applications.MilkPlant.imports import *
from dream.simulation.imports import ExcelHandler, ExitJobShop
from dream.simulation.Globals import runSimulation


T1=MilkTank('T1','T1',capacity=640)
T2=MilkTank('T2','T2',capacity=520)
T3=MilkTank('T3','T3',capacity=140)

Tr1=MilkTransport('Tr1','Tr1')
Tr2=MilkTransport('Tr2','Tr2')
Tr3=MilkTransport('Tr3','Tr3')

E=ExitJobShop('E','Exit')

route1=[{"stationIdsList": ["T1"]},
         {"stationIdsList": ["Tr1"],"processingTime":{'Fixed':{'mean':0.17341}}},
         {"stationIdsList": ["T2"]},
         {"stationIdsList": ["Tr2"],"processingTime":{'Fixed':{'mean':0}},'volume':1000},
         {"stationIdsList": ["E"]}]

route2=[{"stationIdsList": ["T3"]},
         {"stationIdsList": ["Tr3"],"processingTime":{'Fixed':{'mean':1.11111}}},
         {"stationIdsList": ["T2"]},
         {"stationIdsList": ["Tr2"],"processingTime":{'Fixed':{'mean':0}},'volume':1000},
         {"stationIdsList": ["E"]}]

MPList=[]       
for i in range(173):
    MP=MilkPack('MT_A'+str(i),'MT_A'+str(i),route=list(route1),liters=5,fat=3.8,productId=1)
    MPList.append(MP)
     
for i in range(27):
    MP=MilkPack('MT_B'+str(i),'MT_B'+str(i),route=route2,currentStation=T3,liters=5,fat=0.1,productId=1)
    MPList.append(MP)
        
runSimulation([T1,T2,T3,Tr1,Tr2,Tr3,E]+MPList, 1000,trace='Yes')
ExcelHandler.outputTrace('MilkPlant')

print 1