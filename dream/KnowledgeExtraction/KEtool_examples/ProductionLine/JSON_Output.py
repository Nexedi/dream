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

def JSON_example(list1,list2):
    
    jsonFile= open('JSON_example.json','r')
    data = json.load(jsonFile)
    jsonFile.close()
       
    nodes=data.get('nodes',{})        
    for (element_id,element) in nodes.iteritems():
        name=element.get('name')
        scrapQuantity=element.get('scrapQuantity',{})
        processingTime=element.get('processingTime',{})
        
        if name in list1.keys(): 
            element['processingTime']= list1[name]
        else:
            continue
        if name in list2.keys():
            element['scrapQuantity']= list2[name]
        else:
            continue
        jsonFile = open('JSON_exampleOutput.json',"w")
        jsonFile.write(json.dumps(data, indent=True))
        jsonFile.close()
    return json.dumps(data, indent=True)