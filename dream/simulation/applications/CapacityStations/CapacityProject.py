# ===========================================================================
# Copyright 2013 University of Limerick
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

'''
Created on 5 June 2013

@author: George
'''
'''
a project that requires specific capacity from each station
'''

from dream.simulation.Entity import Entity

# ===========================================================================
# The CapacityEntityProject object 
# ===========================================================================
class CapacityProject(Entity):
    type="CapacityProject"
    
    def __init__(self, id=None, name=None, capacityRequirementDict={}, earliestStartDict={}, dueDate=0,
                 assemblySpaceRequirement=0, **kw):
        Entity.__init__(self, id, name, dueDate=dueDate)
        # a dict that shows the required capacity from every station
        self.capacityRequirementDict=capacityRequirementDict
        # a dict that shows the earliest start in every station
        self.earliestStartDict=earliestStartDict
        # the assembly space the project requires
        self.assemblySpaceRequirement=assemblySpaceRequirement
        from dream.simulation.Globals import G
        if hasattr(G, 'CapacityProjectList'):
            G.CapacityProjectList.append(self)
        else:
            G.CapacityProjectList=[]
            G.CapacityProjectList.append(self)
        
    def initialize(self):
        self.projectSchedule=[]     # a list of dicts to keep the schedule
        self.alreadyWorkedDict={}   # a dict that hold what has been processed at every station
        for stationId in self.capacityRequirementDict:
            self.alreadyWorkedDict[stationId]=0
        
    # =======================================================================    
    # outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from dream.simulation.Globals import G
        json = {'_class': 'Dream.%s' % (self.__class__.__name__),
                'id': self.id,
                'family': 'Job',
                'results': {}}
        if (G.numberOfReplications == 1):
            # if we had just one replication output the results as numbers
            json['results']['schedule']=self.projectSchedule
        G.outputJSON['elementList'].append(json)
