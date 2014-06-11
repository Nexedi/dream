import json


def JSON_example(list1,list2):
    
    jsonFile= open('JSON_example.json','r')
    data = json.load(jsonFile)
    jsonFile.close()
       
    nodes=data.get('nodes',{})        
    for (element_id,element) in nodes.iteritems():
        name=element.get('name')
        scrapQuantity=element.get('scrapQuantity',{})
        processingTime=element.get('processingTime',{})

        if name =='P1':
            scrapQuantity['mean']=str(list2['P1'])
            processingTime['distributionType']=str(list1['P1']['distributionType'])
            processingTime['mean']=str(list1['P1']['mean'])
            processingTime['stdev']=str(list1['P1']['stdev'])
        elif name=='P4':
            scrapQuantity['mean']=str(list2['P4'])
            processingTime['distributionType']=str(list1['P4']['distributionType'])
            processingTime['mean']=str(list1['P4']['mean'])
            processingTime['stdev']=str(list1['P4']['stdev'])
        elif name=='P2':
            scrapQuantity['mean']=str(list2['P2'])
            processingTime['distributionType']=str(list1['P2']['distributionType'])
            processingTime['mean']=str(list1['P2']['mean'])
            processingTime['stdev']=str(list1['P2']['stdev'])
        elif name=='P5':
            scrapQuantity['mean']=str(list2['P5'])
            processingTime['distributionType']=str(list1['P5']['distributionType'])
            processingTime['mean']=str(list1['P5']['mean'])
            processingTime['stdev']=str(list1['P5']['stdev'])
        elif name=='P3':
            scrapQuantity['mean']=str(list2['P3'])
            processingTime['distributionType']=str(list1['P3']['distributionType'])
            processingTime['mean']=str(list1['P3']['mean'])
            processingTime['stdev']=str(list1['P3']['stdev'])
        elif name=='P6':
            scrapQuantity['mean']=str(list2['P6'])
            processingTime['distributionType']=str(list1['P6']['distributionType'])
            processingTime['mean']=str(list1['P6']['mean'])
            processingTime['stdev']=str(list1['P6']['stdev'])
        elif name=='P7':
            scrapQuantity['mean']=str(list2['P7'])
            processingTime['distributionType']=str(list1['P7']['distributionType'])
            processingTime['mean']=str(list1['P7']['mean'])
            processingTime['stdev']=str(list1['P7']['stdev'])
        elif name=='P8':
            scrapQuantity['mean']=str(list2['P8'])
            processingTime['distributionType']=str(list1['P8']['distributionType'])
            processingTime['mean']=str(list1['P8']['mean'])
            processingTime['stdev']=str(list1['P8']['stdev'])
        elif name=='P9':
            scrapQuantity['mean']=str(list2['P9'])
            processingTime['distributionType']=str(list1['P9']['distributionType'])
            processingTime['mean']=str(list1['P9']['mean'])
            processingTime['stdev']=str(list1['P9']['stdev'])
        elif name=='P10':
            scrapQuantity['mean']=str(list2['P10'])
            processingTime['distributionType']=str(list1['P10']['distributionType'])
            processingTime['mean']=str(list1['P10']['mean'])
            processingTime['stdev']=str(list1['P10']['stdev'])
        elif name=='P11':
            scrapQuantity['mean']=str(list2['P11'])
            processingTime['distributionType']=str(list1['P11']['distributionType'])
            processingTime['mean']=str(list1['P11']['mean'])
            processingTime['stdev']=str(list1['P11']['stdev'])   
        else:
            continue            
           
        jsonFile = open('JSON_exampleOutput.json',"w")
        jsonFile.write(json.dumps(data, indent=True))
        jsonFile.close()








