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

class SimulationExamples(TestCase):
    """
    Test topology files. The simulation is launched with files Topology01.json,
    Topology02.json, etc, and every time we look if the result is like we expect.
    
    If the result format or content change, it is required to dump again all
    result files. But this is easy to do :
    
    dump=1 python setup.py test
    
    This will regenerate all dump files in dream/tests/dump/.
    Then you can check carefully if all outputs are correct. You could use git
    diff to check what is different. Once you are sure that your new dumps are
    correct, you could commit, your new dumps will be used as new reference.
    """
    def testTwoServers(self):
      from dream.simulation.Examples.TwoServers import main
      result = main(test=1)
      self.assertEquals(result['parts'], 732)
      self.assertTrue(78.17 < result["blockage_ratio"] < 78.18)
      self.assertTrue(26.73 < result["working_ratio"] < 27.74)
     
    def testAssemblyLine(self):
      from dream.simulation.Examples.AssemblyLine import main
      result = main(test=1)
      self.assertEquals(result['frames'], 664)
      self.assertTrue(92.36 < result["working_ratio"] < 93.37)
     	
    def testSingleServer(self):
      from dream.simulation.Examples.SingleServer import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2880)
      self.assertTrue(49.99 < result["working_ratio"] < 50.01)
     	
    def testClearBatchLines(self):
      from dream.simulation.Examples.ClearBatchLines import main
      result = main(test=1)
      self.assertEquals(result['batches'], 89)
      self.assertTrue(0.069 < result["waiting_ratio_M1"] < 0.07)
      self.assertTrue(0.104 < result["waiting_ratio_M2"] < 0.105)
      self.assertTrue(93.81 < result["waiting_ratio_M3"] < 93.82)
     	
    def testDecompositionOfBatches(self):
      from dream.simulation.Examples.DecompositionOfBatches import main
      result = main(test=1)
      self.assertEquals(result['subbatches'], 2302)
      self.assertTrue(79.96 < result["working_ratio"] < 79.97)
      self.assertEquals(result["blockage_ratio"] , 0.0)
      self.assertTrue(20.03 < result["waiting_ratio"] < 20.04)
     	
    def testSerialBatchProcessing(self):
      from dream.simulation.Examples.SerialBatchProcessing import main
      result = main(test=1)
      self.assertEquals(result['batches'], 359)
      self.assertTrue(0.104 < result["waiting_ratio_M1"] < 0.105)
      self.assertTrue(0.104 < result["waiting_ratio_M2"] < 0.105)
      self.assertTrue(75.06 < result["waiting_ratio_M3"] < 75.07)
     
    def testJobShop1(self):
      from dream.simulation.Examples.JobShop1 import main
      result = main(test=1)
      expectedResult=[['Queue1', 0], ['Machine1', 0], ['Queue3', 1.0], ['Machine3', 1.0], ['Queue2', 4.0], ['Machine2', 4.0], ['Exit', 6.0]]
      self.assertEquals(result, expectedResult)
     
    def testJobShop2EDD(self):
      from dream.simulation.Examples.JobShop2EDD import main
      result = main(test=1)
      expectedResult=[['Queue1', 0], ['Machine1', 2.0], ['Queue3', 3.0], ['Machine3', 3.0], ['Queue2', 6.0], ['Machine2', 6.0], ['Exit', 8.0], \
    ['Queue1', 0], ['Machine1', 0], ['Queue2', 2.0], ['Machine2', 2.0], ['Queue3', 6.0], ['Machine3', 6.0], ['Exit', 12.0], ['Queue1', 0], \
    ['Machine1', 3.0], ['Queue3', 13.0], ['Machine3', 13.0], ['Exit', 16.0]]
      self.assertEquals(result, expectedResult)	
     
    def testJobShop2MC(self):
      from dream.simulation.Examples.JobShop2MC import main
      result = main(test=1)
      expectedResult=[['Queue1', 0], ['Machine1', 12.0], ['Queue3', 13.0], ['Machine3', 13.0], ['Queue2', 16.0], \
    ['Machine2', 16.0], ['Exit', 18.0], ['Queue1', 0], ['Machine1', 10.0], ['Queue2', 12.0], ['Machine2', 12.0], \
    ['Queue3', 16.0], ['Machine3', 16.0], ['Exit', 22.0], ['Queue1', 0], ['Machine1', 0], ['Queue3', 10.0], ['Machine3', 10.0], ['Exit', 13.0]]
      self.assertEquals(result, expectedResult)	
     
    def testJobShop2Priority(self):
      from dream.simulation.Examples.JobShop2Priority import main
      result = main(test=1)
      expectedResult=[['Queue1', 0], ['Machine1', 10.0], ['Queue3', 11.0], ['Machine3', 13.0], ['Queue2', 16.0], \
    ['Machine2', 17.0], ['Exit', 19.0], ['Queue1', 0], ['Machine1', 11.0], ['Queue2', 13.0], ['Machine2', 13.0], ['Queue3', 17.0], \
    ['Machine3', 17.0], ['Exit', 23.0], ['Queue1', 0], ['Machine1', 0], ['Queue3', 10.0], ['Machine3', 10.0], ['Exit', 13.0]]
      self.assertEquals(result, expectedResult)	
     	
    def testJobShop2RPC(self):
      from dream.simulation.Examples.JobShop2RPC import main
      result = main(test=1)
      expectedResult=[['Queue1', 0], ['Machine1', 12.0], ['Queue3', 13.0], ['Machine3', 13.0], ['Queue2', 16.0], \
    ['Machine2', 16.0], ['Exit', 18.0], ['Queue1', 0], ['Machine1', 10.0], ['Queue2', 12.0], ['Machine2', 12.0], ['Queue3', 16.0], \
    ['Machine3', 16.0], ['Exit', 22.0], ['Queue1', 0], ['Machine1', 0], ['Queue3', 10.0], ['Machine3', 10.0], ['Exit', 13.0]]
      self.assertEquals(result, expectedResult)
     	
    def testParallelServers1(self):
      from dream.simulation.Examples.ParallelServers1 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2880)
      self.assertTrue(23.09 < result["working_ratio_M1"] < 23.1)
      self.assertTrue(26.9 < result["working_ratio_M2"] < 26.91)
     	
    def testParallelServers2(self):
      from dream.simulation.Examples.ParallelServers3 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2880)
      self.assertTrue(46.18 < result["working_ratio_M1"] < 46.19)
      self.assertTrue(3.81 < result["working_ratio_M2"] < 3.82)
     	
    #NOTE: testParallelServers4 is extension of testParallelServers4 so this test really tests if they both run
    def testParallelServers4(self):
      from dream.simulation.Examples.ParallelServers4 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2880)
      self.assertTrue(46.18 < result["working_ratio_M1"] < 46.19)
      self.assertTrue(3.81 < result["working_ratio_M2"] < 3.82)
      self.assertEquals(result['NumM1'], 2660)
      self.assertEquals(result['NumM2'], 220)
     	
    def testServerWithShift1(self):
      from dream.simulation.Examples.ServerWithShift1 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 3)
      self.assertTrue(49.99 < result["working_ratio"] < 50.01)
     	
    def testServerWithShift2(self):
      from dream.simulation.Examples.ServerWithShift2 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 16)
      self.assertTrue(49.99 < result["working_ratio"] < 50.01)
     	
    def testServerWithShift3(self):
      from dream.simulation.Examples.ServerWithShift3 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 4)
      self.assertTrue(59.99 < result["working_ratio"] < 60.01)
     
    def testServerWithShift4(self):
      from dream.simulation.Examples.ServerWithShift4 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2)
      self.assertTrue(29.99 < result["working_ratio"] < 30.01)
     	
    def testSettingWip1(self):
      from dream.simulation.Examples.SettingWip1 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 1)
      self.assertEquals(result['simulationTime'], 0.25)	
      self.assertEquals(result["working_ratio"], 100)
     	
    def testSettingWip2(self):
      from dream.simulation.Examples.SettingWip2 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2)
      self.assertEquals(result['simulationTime'], 0.50)	
      self.assertEquals(result["working_ratio"], 100)
     	
    def testSettingWip3(self):
      from dream.simulation.Examples.SettingWip3 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2)
      self.assertEquals(result['simulationTime'], 0.35)	
      self.assertEquals(result["working_ratio"], 100)
     	
    def testBalancingABuffer(self):
      from dream.simulation.Examples.BalancingABuffer import main
      result = main(test=1)
      self.assertEquals(result['parts'], 13)
      self.assertEquals(result["working_ratio"], 80)
     	
    def testChangingPredecessors(self):
      from dream.simulation.Examples.ChangingPredecessors import main
      result = main(test=1)
      self.assertEquals(result['parts'], 10)
      self.assertEquals(result['simulationTime'], 36.0)
      self.assertTrue(83.32 < result["working_ratio"] < 83.34)
     	
    def testSettingWip3(self):
      from dream.simulation.Examples.SettingWip3 import main
      result = main(test=1)
      self.assertEquals(result['parts'], 2)
      self.assertEquals(result['simulationTime'], 0.35)	
      self.assertEquals(result["working_ratio"], 100)
     	
    def testNonStarvingLine(self):
      from dream.simulation.Examples.NonStarvingLine import main
      result = main(test=1)
      self.assertEquals(result['parts'], 9)
      self.assertEquals(result["working_ratio"], 100)
     	
    def testNonStarvingLineBatches(self):
      from dream.simulation.Examples.NonStarvingLineBatches import main
      result = main(test=1)
      self.assertEquals(result['batches'], 4)
      self.assertEquals(result["working_ratio"], 100)
      
    def testCompoundMachine(self):
      from dream.simulation.Examples.CompoundMachine import main
      result = main(test=1)
      self.assertTrue(5.8 < result < 5.9)
      
    def testJobShop2ScenarioAnalysis(self):
      from dream.simulation.Examples.JobShop2ScenarioAnalysis import main
      result = main(test=1)
      self.assertEquals(result, 2)
      
    def testBufferAllocation(self):
      from dream.simulation.Examples.BufferAllocation import main
      result = main(test=1)
      self.assertTrue(80 < result["parts"] < 1000)
      