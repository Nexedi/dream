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
    result = main()
    self.assertEquals(result['parts'], 732)
    self.assertTrue(78.17 < result["blockage_ratio"] < 78.18)
    self.assertTrue(26.73 < result["working_ratio"] < 27.74)
    from dream.simulation.Examples.AssemblyLine import main
    result = main()
    self.assertEquals(result['frames'], 664)
    self.assertTrue(92.36 < result["working_ratio"] < 93.37)

