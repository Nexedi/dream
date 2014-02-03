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
Created on 20 Dec 2012

@author: George
'''
'''
Inherits from QueueJobShop. If it gets an isCritical Entity it can interrupt the  destination station
'''

from QueueJobShop import QueueJobShop
from SimPy.Simulation import now

# ===========================================================================
# the QueuePreemptive object
# ===========================================================================
class QueuePreemptive(QueueJobShop):
#     # =======================================================================
#     # extend he default so that it can interrupt the receiver if need be
#     # =======================================================================
#     def getEntity(self):
#         activeEntity=QueueJobShop.getEntity(self)   #execute default behaviour
#         #if the obtained Entity is critical
#         if activeEntity.isCritical:
#             #if the receiver is not empty
#             if len(self.receiver.getActiveObjectQueue())>0:
#                 #if the receiver does not hold an Entity that is also critical
#                 if not self.receiver.getActiveObjectQueue()[0].isCritical:
#                     self.receiver.shouldPreempt=True
#                     self.receiver.preempt()
#                     self.receiver.timeLastEntityEnded=now()     #required to count blockage correctly in the preemptied station
#         return activeEntity
    
    # =======================================================================                
    # for future use
    # =======================================================================
    def sortEntities(self):
        QueueJobShop.sortEntities(self)
    
    
    