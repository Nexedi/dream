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
inherits from MachineJobShop it can preempt the currently processed Entity if need be
'''
from MachineJobShop import MachineJobShop
from SimPy.Simulation import reactivate, now

# ===========================================================================
# the MachineJobShop object
# ===========================================================================
class MachinePreemptive(MachineJobShop):
    
    def __init__(self, id, name, capacity=1, distribution='Fixed', mean=1, stdev=0, min=0, max=10,\
                  failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None',\
                  operatorPool='None',operationType='None',\
                  loadDistribution="No",loadMean=0, loadStdev=0, loadMin=0, loadMax=10,\
                  setupDistribution="No",setupMean=0, setupStdev=0, setupMin=0, setupMax=10,\
                  resetOnPreemption=True):
        MachineJobShop.__init__(self, id, name, capacity, distribution, mean, stdev, min, max,\
                  failureDistribution, MTTF, MTTR, availability, repairman,\
                  operatorPool,operationType,\
                  loadDistribution,loadMean, loadStdev, loadMin, loadMax,\
                  setupDistribution,setupMean, setupStdev, setupMin, setupMax)
        self.resetOnPreemption=resetOnPreemption    #flag that shows if the processing  time should be reset or not
                 
#     def getEntity(self):
#         activeEntity=MachineJobShop.getEntity(self)
#         self.lastGiver=self.giver
#         return activeEntity
        
    # =======================================================================
    # method to execute the preemption
    # =======================================================================    
    def preempt(self):
        activeObject=self.getActiveObject()
        activeEntity=self.getActiveObjectQueue()[0] #get the active Entity
        #calculate the remaining processing time
        #if it is reset then set it as the original processing time
        if self.resetOnPreemption:
            remainingProcessingTime=self.procTime
        #else subtract the time that passed since the entity entered
        #(may need also failure time if there was. TO BE MELIORATED)
        else:
            remainingProcessingTime=self.procTime-(now()-self.timeLastEntityEntered)
        #update the remaining route of activeEntity
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.id)],\
                                               'processingTime':\
                                                    {'distributionType':'Fixed',\
                                                     'mean':str(remainingProcessingTime)}})
#         activeEntity.remainingRoute.insert(0, [self.id, remainingProcessingTime])
        activeEntity.remainingRoute.insert(0, {'stationIdsList':[str(self.lastGiver.id)],\
                                               'processingTime':\
                                                    {'distributionType':'Fixed',\
                                                     'mean':'0'}})
#         activeEntity.remainingRoute.insert(0, [self.lastGiver.id, 0])        
        #set the receiver  as the object where the active entity was preempted from 
        self.receiver=self.lastGiver
        self.next=[self.receiver]
        self.waitToDispose=True                     #set that I have to dispose
        self.receiver.timeLastEntityEnded=now()     #required to count blockage correctly in the preemptied station
        reactivate(self)

        

