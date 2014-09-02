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
Created on 06 May 2013

@author: Anna, George
'''
'''
Entity that is the MA in the DemandPlanning case. Inherits from Job (TODO see if this offers anything)
'''

from Job import Job

class JobMA(Job):
    def __init__(self,orderID, MAid, SPid, PPOSid, qty, minQty, origWeek, future):
        Job.__init__(self, id=MAid)
        self.type = 'item'
        self.orderID = orderID
        self.MAid = MAid
        self.SPid = SPid
        self.PPOSid = PPOSid
        self.qty = qty
        self.minQty = minQty
        self.originalWeek = origWeek
        self.future = future        # if 1 suggests that the MA belongs to the future demand (0 for the PPOS to be disaggregated)
        self.weekPlan = self.originalWeek

