'''
Created on 19 Feb 2014

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








