from copy import copy

from dream.plugins import plugin
import datetime

class InsertWIP(plugin.InputPreparationPlugin):
  """ Input preparation
      reads the BOM - wip and inserts the work in progress to the corresponding stations
  """

  def preprocess(self, data):
    """ updates the Work in Process of each station according to the BOM
    """
    wip = data["input"]["BOM"].get("WIP", {})
    for partID, work in wip.iteritems():
      stationID = work.get("station", None)
      if not stationID:
        break
      node = data["graph"]["node"].get(stationID, {})
      if not node:
        break
      wip = node.get("wip", [])
      wip.append({
        "id": partID,
        "sequence": work.get("sequence", None),
        "task_id": work.get("task_id", None)
      })
      operator = work.get("operator", None)
      if operator:
        wip[-1]["operator"]=operator
      node["wip"] = wip
    return data

if __name__ == '__main__':
    pass