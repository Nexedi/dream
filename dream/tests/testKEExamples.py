# ===========================================================================
# Copyright 2014 Nexedi SA
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

from unittest import TestCase
import os
project_path = os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0]
import xlrd
import json

class KnowledgeExtractionExamples(TestCase):
    """
    Test KE examples
    """
    def testTwoParallelStations(self):
        from dream.KnowledgeExtraction.KEtool_examples.TwoParallelStations.TwoParallelStations_example import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtool_examples", 
                                                        "TwoParallelStations")
        workbook = xlrd.open_workbook(os.path.join(filepath, 'inputData.xls'))
        jsonFile = open(os.path.join(filepath, 'JSON_ParallelStations.json'))     
        result = main(test=1,workbook=workbook,jsonFile=jsonFile)
        result_data = json.loads(result)
        result_data=result_data['result']['result_list'][0]
        elementList=result_data.get('elementList',[])
        for element in elementList:
            if element['id']=='E1':
                self.assertEquals(element['results']['throughput'][0], 86)
            if element['id']=='St1':
                self.assertTrue(99.93<element['results']['working_ratio'][0]<99.94)
        jsonFile.close()
        
    def testTwoServers(self):
        from dream.KnowledgeExtraction.KEtool_examples.TwoServers.TwoServers_example import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtool_examples", 
                                                        "TwoServers")
        workbook = xlrd.open_workbook(os.path.join(filepath, 'inputsTwoServers.xls'))
        jsonFile = open(os.path.join(filepath, 'JSON_TwoServers.json'))     
        result = main(test=1,workbook=workbook,jsonFile=jsonFile)
        result_data = json.loads(result)
        
        result_data=result_data['result']['result_list'][0]
        elementList=result_data.get('elementList',[])
        for element in elementList:
            if element['id']=='E1':
                self.assertTrue(240<element['results']['throughput'][0]<250)
            if element['id']=='M2':
                self.assertTrue(11.00<element['results']['working_ratio'][0]<12.00)
            if element['id']=='M1':
                self.assertTrue(91.90<element['results']['working_ratio'][0]<92.90)
        jsonFile.close()
    
     
   