'''
Created on 4 Sep 2015

@author: Anna
'''
from dream.plugins import plugin

class projTabular(plugin.OutputPreparationPlugin):
    """ Output the projection completion date in a tab
    """

    def postprocess(self, data):
        data['result']['result_list'][0]['exit_output'] = [['Project', 'Earliest Completion Date', 'Conservative estimate Completion Date']]
        from dream.simulation.applications.FrozenSimulation.Globals import G
        for proj in G.completionDate['Earliest'].keys():
          data['result']['result_list'][0]['exit_output'].append([proj, G.completionDate['Earliest'][proj], G.completionDate['Latest'][proj]])
            
        return data
        

