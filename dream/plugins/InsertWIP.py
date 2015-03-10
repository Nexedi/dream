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
      # operator
      operator = work.get("operator", None)
      if operator:
        wip[-1]["operator"]=operator
      # remaining Processing Time
      remainingProcessingTime = work.get("remainingProcessingTime", 0)
      # XXX the time is considered to be provided as a single value
      if remainingProcessingTime:
        # XXX hard-coded distribution of type Fixed - reconsider for stochastic analyis
        wip[-1]["remainingProcessingTime"] = {"Fixed": {"mean": remainingProcessingTime}}
      node["wip"] = wip
    return data

if __name__ == '__main__':
    pass