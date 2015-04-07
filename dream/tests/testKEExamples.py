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
                self.assertTrue(240<element['results']['throughput'][0]<260)
            if element['id']=='M2':
                self.assertTrue(10.00<element['results']['working_ratio'][0]<13.00)
            if element['id']=='M1':
                self.assertTrue(91.90<element['results']['working_ratio'][0]<92.90)
        jsonFile.close()
    
    def testAssembleDismantle(self):
        from dream.KnowledgeExtraction.KEtool_examples.AssembleDismantle.AssembleDismantle_example import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtool_examples", 
                                                        "AssembleDismantle")
        workbook = xlrd.open_workbook(os.path.join(filepath, 'inputData.xls'))
        jsonFile = open(os.path.join(filepath, 'JSON_AssembleDismantle.json'))     
        result = main(test=1,workbook=workbook,jsonFile=jsonFile)
        result_data = json.loads(result)
        result_data=result_data['result']['result_list'][0]
        elementList=result_data.get('elementList',[])
        for element in elementList:
            if element['id']=='M1':
                self.assertTrue(96.1<element['results']['failure_ratio'][0]<97.1)
            if element['id']=='M1':
                self.assertTrue(0.02<element['results']['working_ratio'][0]<0.09)
        jsonFile.close()
     
    def testConveyerLine(self):
        from dream.KnowledgeExtraction.KEtool_examples.ConveyerLine.KEtool_MainScript import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtool_examples", 
                                                        "ConveyerLine")
        csvFile1= open(os.path.join(filepath, 'InterArrivalData.csv')) 
        csvFile2= open(os.path.join(filepath, 'DataSet.csv'))
        jsonFile = open(os.path.join(filepath, 'JSON_ConveyerLine.json'))     
        result = main(test=1,csvFile1=csvFile1,csvFile2=csvFile2,jsonFile=jsonFile)
        result_data = result
        result_data=result_data['graph']
        nodes=result_data.get('node',{})
        for element_id,element in nodes.iteritems():
            if element_id=='M1':
                self.assertEquals(element['processingTime'].keys()[0],'Logistic')
            if element_id=='M2':
                self.assertEquals(element['processingTime'].keys()[0],'Logistic')
            if element_id=='S1':
                self.assertEquals(element['interarrivalTime'].keys()[0],'Exp')
        jsonFile.close()
    
    def testConfidenceIntervals(self):
        from dream.KnowledgeExtraction.KEtool_examples.ConfidenceIntervals.ConfidenceIntervals_example import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtool_examples", 
                                                        "ConfidenceIntervals")
        csvFile= open(os.path.join(filepath, 'DataSet.csv'))    
        result1,result2,result3 = main(test=1,csvFile=csvFile)
        self.assertEquals(result1[0],0.0)
        self.assertEquals(result1[1],1.0)
        self.assertEquals(result2[0],0.4719902587261917)
        self.assertEquals(result2[1],0.5545222108338084)
        self.assertEquals(result3[0],1.0)
        self.assertEquals(result3[1],1.0)
        
    def testSingleServer(self):
        from dream.KnowledgeExtraction.KEtoolSimul8_examples.SingleServer.SingleServer import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtoolSimul8_examples", 
                                                        "SingleServer")
        workbook1 = xlrd.open_workbook(os.path.join(filepath, 'InterarrivalsData.xls'))
        workbook2 = xlrd.open_workbook(os.path.join(filepath, 'ProcData.xls'))
        simul8XMLFile = open(os.path.join(filepath, 'SingleServer.xml'))     
        result = main(test=1,workbook1=workbook1,workbook2=workbook2,simul8XMLFile=simul8XMLFile)
        root=result.getroot()
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Entry Point' and objects.attrib['Name'] == 'Source':
                procDist = objects.find('./InterArrivalTimeSampleData/DistribType')
                procPar1 = objects.find('./InterArrivalTimeSampleData/DistParam1')
                self.assertEquals(procDist.text,'7')
                self.assertEquals(procPar1.text,'3.72710330863')
            if objects.attrib['Type'] == 'Work Center' and objects.attrib['Name'] == "Activity 1":
                procDist = objects.find('./OperationTimeSampleData/DistribType')
                procPar1 = objects.find('./OperationTimeSampleData/DistParam1')
                procPar2 = objects.find('./OperationTimeSampleData/DistParam2')
                self.assertEquals(procDist.text,'10')
                self.assertEquals(procPar1.text,'14.4634502422')
                self.assertEquals(procPar2.text,'1.03221368006')
    
    def testTopology1(self):
        from dream.KnowledgeExtraction.KEtoolSimul8_examples.Topology1.Topology1 import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtoolSimul8_examples", 
                                                        "Topology1")
        workbook = xlrd.open_workbook(os.path.join(filepath, 'DataSet.xlsx'))
        csvFile= open(os.path.join(filepath, 'ProcTimesData.csv'))
        simul8XMLFile = open(os.path.join(filepath, 'Topology1.xml'))     
        result = main(test=1,workbook=workbook,csvFile=csvFile,simul8XMLFile=simul8XMLFile)
        root=result.getroot()
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Entry Point' and objects.attrib['Name'] == 'Source':
                procDist = objects.find('./InterArrivalTimeSampleData/DistribType')
                procPar1 = objects.find('./InterArrivalTimeSampleData/DistParam1')
                self.assertEquals(procDist.text,'7')
                self.assertEquals(procPar1.text,'3.81461051661')
            if objects.attrib['Type'] == 'Work Center' and objects.attrib['Name'] == "Activity 1":
                procDist = objects.find('./BreakDowns/MTBFSampleData/DistribType')
                procPar1 = objects.find('./BreakDowns/MTBFSampleData/DistParam1')
                procPar2 = objects.find('./BreakDowns/MTBFSampleData/DistParam2')
                self.assertEquals(procDist.text,'3')
                self.assertEquals(procPar1.text,'60.241674662')
                self.assertEquals(procPar2.text,'13.6343562616')
                
                procDist = objects.find('./BreakDowns/MTTRSampleData/DistribType')
                procPar1 = objects.find('./BreakDowns/MTTRSampleData/DistParam1')
                procPar2 = objects.find('./BreakDowns/MTTRSampleData/DistParam2')
                self.assertEquals(procDist.text,'9')
                self.assertEquals(procPar1.text,'2.49625391491')
                self.assertEquals(procPar2.text,'0.0808226713028')
            
    def testParallelStations(self):
        from dream.KnowledgeExtraction.KEtool_examples.ParallelStations_withfailures.ParallelStations_example import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtool_examples", 
                                                        "ParallelStations_withfailures")
        DBFilePath = ("C:\Users\Panos\Documents\KE tool_documentation")
        jsonFile = open(os.path.join(filepath, 'JSON_example.json'))     
        result = main(test=1,DBFilePath=DBFilePath,jsonFile=jsonFile)
        result_data = result
        
        result_data=result_data['graph']
        nodes=result_data.get('node',{})
        for element_id,element in nodes.iteritems():
            if element_id=='M1':
                self.assertEquals(element['processingTime'].keys()[0],'Logistic')
                self.assertEquals(element['processingTime'].values()[0]['scale'],5.943555041732533)
                self.assertEquals(element['processingTime'].values()[0]['location'],51.57623425532299)
                
                self.assertEquals(element['interruptions']['failure']['TTR'].keys()[0],'Poisson')
                self.assertEquals(element['interruptions']['failure']['TTR'].values()[0]['lambda'],0.1053658536585366)
                
                self.assertEquals(element['interruptions']['failure']['TTF'].keys()[0],'Weibull')
                self.assertEquals(element['interruptions']['failure']['TTF'].values()[0]['shape'],3.1671825421393747)
                self.assertEquals(element['interruptions']['failure']['TTF'].values()[0]['scale'],0.7571939493062068)  
            
            if element_id=='M2':
                self.assertEquals(element['processingTime'].keys()[0],'Cauchy')
                self.assertEquals(element['processingTime'].values()[0]['scale'],1.7219415441266923)
                self.assertEquals(element['processingTime'].values()[0]['location'],49.732494067271205)
                
                self.assertEquals(element['interruptions']['failure']['TTR'].keys()[0],'Poisson')
                self.assertEquals(element['interruptions']['failure']['TTR'].values()[0]['lambda'],0.1423076923076923)
                
                self.assertEquals(element['interruptions']['failure']['TTF'].keys()[0],'Weibull')
                self.assertEquals(element['interruptions']['failure']['TTF'].values()[0]['shape'],3.1975046230623905)
                self.assertEquals(element['interruptions']['failure']['TTF'].values()[0]['scale'],0.6805471087485552)        
        jsonFile.close()
    
    def testParallelStationsFailures(self):
        from dream.KnowledgeExtraction.KEtoolSimul8_examples.ParallelStationsFailures.ParallelStationsFailures import main 
        filepath=os.path.join(project_path, "dream", "KnowledgeExtraction", "KEtoolSimul8_examples", 
                                                        "ParallelStationsFailures")
        
        DBFilePath = ("C:\Users\Panos\Documents\KE tool_documentation")       
        simul8XMLFile = open(os.path.join(filepath, 'ParallelStations.xml'))     
        result = main(test=1,DBFilePath=DBFilePath,simul8XMLFile=simul8XMLFile)
        root=result.getroot()
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Center' and objects.attrib['Name'] == "MILL1":
                procDist = objects.find('./BreakDowns/MTBFSampleData/DistribType')
                procPar1 = objects.find('./BreakDowns/MTBFSampleData/DistParam1')
                procPar2 = objects.find('./BreakDowns/MTBFSampleData/DistParam2')
                self.assertEquals(procDist.text,'7')
                self.assertEquals(procPar1.text,'1.47747747748')
                
                procDist = objects.find('./BreakDowns/MTTRSampleData/DistribType')
                procPar1 = objects.find('./BreakDowns/MTTRSampleData/DistParam1')
                procPar2 = objects.find('./BreakDowns/MTTRSampleData/DistParam2')
                self.assertEquals(procDist.text,'3')
                self.assertEquals(procPar1.text,'0.105365853659')
                self.assertEquals(procPar2.text,'0.0566050743643')
        
              
    
    
     
   