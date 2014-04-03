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
Created on 8 Nov 2012

@author: George
'''
'''
Models a machine that can route Entities according to a probability. It can be merged with CoreObject in the future
'''

from RandomNumberGenerator import RandomNumberGenerator
from Machine import Machine
from SimPy.Simulation import now

# ===========================================================================
# the MachineProbOut object
# ===========================================================================
class MachineProbOut(Machine):

    #initialize the id, the capacity of the resource and the distribution       
    def __init__(self, id, name, capacity=1, processingTime=None,
                  failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None',\
                  operatorPool='None',operationType='None',\
                  setupTime=None, loadTime=None,
                  isPreemptive=False, resetOnPreemption=False,
                  routingOutProbabilities={}):
        if not processingTime:
          processingTime = {'distribution': 'Fixed',
                            'mean': 1}
        # initialize using the default method of the object 
        Machine.__init__(self,id=id,name=name,\
                                    capacity=capacity,\
                                    processingTime=processingTime,
                                    failureDistribution=failureDistribution,MTTF=MTTF,MTTR=MTTR,\
                                    availability=availability,
                                    repairman=repairman)
        # the following is to assert that probability input is valid
        totalProb=0
        for element in routingOutProbabilities:
            totalProb+=routingOutProbabilities[element] 
        assert(totalProb==100)
        self.routingOutProbabilities=routingOutProbabilities    # keeps the probability input
        self.routingOutRng=RandomNumberGenerator(self, 'Uniform', min=0, max=1) # a Random number generator that creates numbers 
                                                                                # that are uniformly distributed in (0,1) 

    # =======================================================================
    # sets the routing in and out elements for the Object
    # extend so thata staticNext is kept
    # =======================================================================
    def defineRouting(self, predecessorList=[], successorList=[]):
        Machine.defineRouting(self, predecessorList, successorList)
        self.staticNext=self.next

    # =======================================================================
    # actions to be carried out when the processing of an Entity ends
    # extends so that a random number is generated to decide where this Entity will be routed to
    # =======================================================================  
    def endProcessingActions(self):
        activeEntity=Machine.endProcessingActions(self)          # run the default method
        randomNumber=self.routingOutRng.generateNumber()*100    # create a random number uniformly distributed in 0-100 
        probabilityLevel=0  
        # in this loop the next object is determined according to the random number
        for object in self.staticNext:
            probabilityLevel+=self.routingOutProbabilities[object.id] 
            if randomNumber<probabilityLevel:
                self.next=[object]
                self.receiver=object    #TODO, I thought this line would not be needed, but it is. Check this
                print now(), 'out of', randomNumber, 'selected', object.id
                break

    # =======================================================================
    # checks if the Object can dispose an entity to the following object 
    # extend default so that if the caller is not in self.next it returns False
    # (TODO maybe this could be added also in CoreObject)
    # =======================================================================
    def haveToDispose(self, callerObject=None):
        if not (callerObject in self.next):
            return False
        return Machine.haveToDispose(self, callerObject)    # run default behaviour
        
        
    