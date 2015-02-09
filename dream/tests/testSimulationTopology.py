# ===========================================================================
# Copyright 2013 Nexedi SA
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

from dream.simulation import LineGenerationJSON
import json
import os
import glob
import tempfile
from unittest import TestCase


project_path = os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0]

class SimulationTopology(TestCase):
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

  def setUp(self):
     self.dump_folder_path = os.path.join(project_path, "dream", "tests", "dump")

  def checkTopology(self, filename=None):
    file_path = os.path.join(project_path, "dream", "simulation",
                             "JSONInputs", filename)
    input_file = open(file_path, "r")
    input_data = input_file.read()
    input_file.close()
    result = LineGenerationJSON.main(input_data=input_data)
    result_data = json.loads(result)
    # Slightly change the output to make it stable
    del result_data['result']['result_list'][0]["general"]["totalExecutionTime"]
    result_data['result']['result_list'][0]["elementList"].sort(key=lambda x: x["id"])
    stable_result = json.dumps(result_data['result']['result_list'][0], indent=True, sort_keys=True)
    dump_path = os.path.join(self.dump_folder_path, "%s.result" % filename)
    if bool(os.environ.get("dump", False)):
      dump_file = open(dump_path, 'w')
      dump_file.write(stable_result)
      dump_file.close()
    dump_file = open(dump_path, "r")
    dump_result = json.dumps(json.loads(dump_file.read()), indent=True, sort_keys=True)
    dump_file.close()
    self.assertEquals(stable_result, dump_result, "outputs are different")

# Automatically create a test method for every topology
for filepath in glob.glob(os.path.join(project_path, "dream", "simulation",
                             "JSONInputs", "*.json")):
  filename = os.path.basename(filepath)
  def getTestTopology(filename = None):
    def test_topology(self):
      self.checkTopology(filename=filename)
    return test_topology
  setattr(SimulationTopology, "test_%s" % filename, getTestTopology(filename = filename))
