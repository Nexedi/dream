'''
Created on 9 Oct 2014

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

import json
#Create an object that receives the three dictionaries from the KE tool main script, updates the JSON schema and returns it to the KE tool main script
class JSONOutput(object):
    
    def Distributions(self,data):
        data1={}
        dist=data['distributionType']
        del data['distributionType']
        data1[dist]=data
        data=data1
        return data
    
    def JSONOutput(self,list1,list2,list3):
        jsonFile= open('JSON_example.json', 'r') #open the JSON_example.json file
        data = json.load(jsonFile)
        jsonFile.close()
           
        nodes=data['graph']['node'] 
        batchWIP={}
        for (element_id,element) in nodes.iteritems():
            name=element.get('name')
            wip=element.get('wip',[])
            for key in list3.keys():    # conduct a loop statement in the keys of the list3, which actually is the WIP dict
                batchWIP['_class']='Dream.Batch' # static inputs to batchWIP dict
                batchWIP['numberOfUnits']="80"
                batchWIP['name']='Batch'
                if list3[key][0]== name:  # condition that checks if the element in the list3 dict is the same as the name of the element in JSON file  
                    batchWIP['id']=str(key) # input the container id of the WIP batch to the batchWIP dict
                    try:
                        if list3[key][2]: # a condition to check if the WIP is in a station and not in a buffer
                            batchWIP['unitsToProcess']=str(list3[key][2]) # input the unitsToProcess attribute to the batchWIP dict
                            wip.append(batchWIP) # append in the wip attribute in JSON the batchWIP dict
                            batchWIP={}       
                    except IndexError:
                        wip.append(batchWIP)  # in case the WIP is not in a station but it's in a buffer; append again the batchWIP dict (without the unitsToProcess this time)
                        batchWIP={} 
                else:
                    continue             
            if name in list1.keys():       # condition that checks if the element in the list1 is the same as the name of the element in JSON file  
                element['processingTime']= self.Distributions(list1[name])   # input the attributes of list1[name] to the JSON's element 'processingTime'
            else:
                continue
            if name in list2.keys():# condition that checks if the element in the list2 is the same as the name of the element in JSON file  
                element['scrapQuantity']= self.Distributions(list2[name])    # input the attributes of list2[name] to the JSON's element 'scrapQuantity'
            else:
                continue       
            jsonFile = open('JSON_exampleOutput.json',"w")
            jsonFile.write(json.dumps(data, indent=True))
            jsonFile.close()
        return json.dumps(data, indent=True)        