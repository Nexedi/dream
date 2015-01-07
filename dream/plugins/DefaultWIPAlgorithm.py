import json

def preprocess(data):
#     #with open('defaultWIPSampleInput.json', "r+") as jsonFile:
#     #jsondata = json.loads(jsonFile.read())
#     for key, value in data.iteritems() :
#         print key
    wipData=data['input']['wip_spreadsheet']
    node=data['graph']['node']
    wipData.pop(0)  # pop the column names
    for wipItem in wipData:
        partId=wipItem[0]
        # in case there is no id, do not process the element
        if not partId:
            continue
        stationId=wipItem[1]
        remainingProcessingTime=wipItem[2]
        wip=node[stationId].get('wip',[])
        if not wip:
            node[stationId]['wip']=[]
        node[stationId]['wip'].append({
                    "_class": "Dream.Part",
                    "id": partId, 
                    "name": partId,
                    "remainingProcessingTime":{"Fixed":{"mean":remainingProcessingTime}}
                    })
    return data