# This is test suite for erp5 testnode

# test_suite is provided by 'run_test_suite'
from test_suite import EggTestSuite

class DREAM(EggTestSuite):
  def getTestList(self):
    return "dream"
