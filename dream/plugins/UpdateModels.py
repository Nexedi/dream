'''
Created on 3 Feb 2015

@author: GDang
'''
import json

newInstance=open('NewInstance.json', "r") 
modelOldInstance=open('ModelOldInstance.json', "r") 

newInstanceData=newInstance.read() 
modelOldInstanceData=modelOldInstance.read() 

newInstanceJSON=json.loads(newInstanceData)  
modelOldInstanceJSON=json.loads(modelOldInstanceData) 

modelGraph=modelOldInstanceJSON['graph']
modelInput=modelOldInstanceJSON['input']
modelGeneral=modelOldInstanceJSON['general']

updatedModelJSON=newInstanceJSON
updatedModelJSON['graph']=modelGraph
updatedModelJSON['input']=modelInput
updatedModelJSON['general']=modelGeneral
updatedModelJSON['result']={"result_list": []}
updatedModelJSONString=json.dumps(updatedModelJSON, indent=5)
updatedModel=open('UpdatedModel.json', mode='w')
updatedModel.write(updatedModelJSONString)