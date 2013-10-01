from dream.simulation import LineGenerationJSON
import json
import os
import tempfile
from unittest import TestCase

class SimulationTopology(TestCase):
  """
  Test topology files. The simulation is launched with files Topology01.json,
  Topology02.json, etc, and every time we look if the result is like we expect.

  If the result format or content change, it is required to dump again all
  result files. But this is easy to do :

  dump=1 python setup.py test

  This will regenerate all dump files in dream/test/dump/.
  Then you can check carefully if all outputs are correct. You could use git
  diff to check what is different. Once you are sure that your new dumps are
  correct, you could commit, your new dumps will be used as new reference.
  """

  def setUp(self):
     self.project_path = os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0]
     self.dump_folder_path = os.path.join(self.project_path, "dream", "test", "dump")

  def checkTopology(self, filename=None):
    file_path = os.path.join(self.project_path, "dream", "simulation",
                             "JSONInputs", "%s.json" % filename)
    input_file = open(file_path, "r")
    input_data = input_file.read()
    input_file.close()
    result = LineGenerationJSON.main(input_data=input_data)
    result_data = json.loads(result)
    # Slightly change the output to make it stable
    del result_data["general"]["totalExecutionTime"]
    result_data["elementList"].sort(key=lambda x: x["id"])
    stable_result = json.dumps(result_data, indent=True)
    dump_path = os.path.join(self.dump_folder_path, "%s.result" % filename)
    if bool(os.environ.get("dump", False)):
      dump_file = open(dump_path, 'w')
      dump_file.write(stable_result)
      dump_file.close()
    dump_file = open(dump_path, "r")
    dump_result = dump_file.read()
    dump_file.close()
    self.assertEquals(stable_result, dump_result, "outputs are different")

# Automatically create a test method for every topology
for x in range(1, 18):
  def getTestTopology():
   filename = "Topology%02i" % x
   def test_topology(self):
      self.checkTopology(filename=filename)
   return test_topology
  setattr(SimulationTopology, "test_topology_%02i" % x, getTestTopology())
