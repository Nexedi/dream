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
    WIP = data["input"].get("BOM",{}).get("WIP", {})
    for partID, work in WIP.iteritems():
      stationID = work.get("station", None).replace(' ','').split('-')[0]
      if not stationID:
        break
      node = data["graph"]["node"].get(stationID, {})
      if not node:
        break
      wip = node.get("wip", [])
      endOfRoute = False # flag to signal that the part should not be injected as WIP
      mouldCreated = False # flag to signal that the mould of the same order is created
      # if the part lies in an assembly buffer
      if data['graph']['node'][stationID]['_class'] == 'Dream.MouldAssemblyBuffer':
        # find the order it belongs to
        for order in data['input']['BOM']['productionOrders']:
          for component in order.get('componentsList', []):
            if component.get('id',None) == partID:
              # if the part is of class OrderComponent (and NOT Mould)
              if component.get('_class', None) == 'Dream.OrderComponent':
                endOfRoute = True
            # find the Mould component of the order and see it is already in the WIP
            if component.get('_class', None) == 'Dream.Mould':
              if component.get('id', None) in WIP.keys():
                mouldCreated = True
      # if the part reached the end of its route (an assembly buffer) and the mould is already created
      if endOfRoute and mouldCreated:
        continue
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
      remainingSetupTime = work.get('remainingSetupTime', 0)
      # XXX the time is considered to be provided as a single value
      if remainingProcessingTime:
        if isinstance(remainingProcessingTime, dict):
          wip[-1]["remainingProcessingTime"] = remainingProcessingTime
        else:
          # XXX hard-coded distribution of type Fixed - reconsider for stochastic analyis
          wip[-1]["remainingProcessingTime"] = {"Fixed": {"mean": remainingProcessingTime}}
      # XXX the time is considered to be provided as a single value
      if remainingSetupTime:
        if isinstance(remainingSetupTime, dict):
          wip[-1]["remainingSetupTime"] = remainingSetupTime
        else:
          # XXX hard-coded distribution of type Fixed - reconsider for stochastic analyis
          wip[-1]["remainingSetupTime"] = {"Fixed": {"mean": remainingSetupTime}}
      node["wip"] = wip
    return data

if __name__ == '__main__':
    pass
