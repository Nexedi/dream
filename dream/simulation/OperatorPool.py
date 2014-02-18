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
Created on 22 Nov 2012

@author: Ioannis
'''

'''
models a Broker that organizes the dispatch of operators/repairmen
'''

from SimPy.Simulation import Resource, now
import xlwt
import scipy.stats as stat
from ObjectResource import ObjectResource
from Operator import Operator

# ===========================================================================
#               the resource that handles multiple operators
# ===========================================================================
class OperatorPool(ObjectResource):
    
    def __init__(self, id, name, capacity=1,operatorsList='None'):    
        self.id=id      
        self.objName=name
        
        self.type="OperatorPool"
#         self.Res=Resource(self.capacity)
        # lists to hold statistics of multiple runs
#         self.Waiting=[]             # holds the percentage of waiting time 
#         self.Working=[]             # holds the percentage of working time 
        # list with the coreObjects IDs that the Operators operate
        self.coreObjectIds=[]
        # list with the coreObjects that the Operators operate
        self.coreObjects=[]
        # holds the object/Machine that currently handles the operator pool
        self.currentObject='None'
        # TODO: variables to be used by OperatorPreemptive
        # TODO: the object requesting the OperatorPreemptive
        self.requestingObject=None
        # TODO: the last object calling the OperatorPool
        self.receivingObject=None
        
        # check if an operatorsList is 'None'
        if operatorsList=='None' or (operatorsList!='None' and len(operatorsList)==0):
            # list of operators that the OperatorPool holds
            self.operators = []
            # the capacity of the OperatorPool in Operators
            self.capacity=capacity      
            # populate the the operators list and initiate the operators
            for index in range(self.capacity):
                id='O_'+str(index)
                name=self.objName+str(index)
                self.operators.append(Operator(id,name))
        # if a list of operators is given then update accordingly the self.operators variable 
        else:
            assert type(operatorsList) is list, "operatorsList is not a List" 
            self.operators=operatorsList
            self.capacity=len(self.operators)
                
            
    # =======================================================================
    #                     initialize the object 
    # =======================================================================
    def initialize(self):
#         self.totalWorkingTime=0         #holds the total working time
#         self.totalWaitingTime=0         #holds the total waiting time
#         self.timeLastOperationStarted=0    #holds the time that the last operation was started        

        # initialize the operators
        # an operator that may have been initialized by an other operator pool, is initiated again
        # reconsider
        for operator in self.operators:
            if not operator.isInitialized():
                operator.initialize()
            
    # =======================================================================
    #                  checks if there are operators available
    # =======================================================================       
    def checkIfResourceIsAvailable(self):
        # TODO: to discuss with George if using a callerObject is the proper way to inform the OperatorPreemptive
        #     about the object that is requesting to know about its availability
        # TODO: first check if there is any free operator, then check if the requesting entity is critical and preempt
        # if callerOjbect is None then the checkIfResourceIsAvailable performs the default behaviour
        #     so initially it checks whether there is a free operator 
        isAvailable = any(operator.checkIfResourceIsAvailable()==True for operator in self.operators)
#         if isAvailable:
#             return True
        return isAvailable
#         # if there is no free operator, then check if any of the operators can preempt
#         return any(operator.checkIfResourceIsAvailable(callerObject=self)==True for operator in self.operators)
    
    # =======================================================================
    #              find the first available operator and return it
    # =======================================================================
    def findAvailableOperator(self):            # may need to implement different sorting of the operators
        # find the free operator if any
        freeOperator = next(x for x in self.operators if x.checkIfResourceIsAvailable())
#         if freeOperator:
#             return freeOperator
        return freeOperator
#         # if there is no free operator, return the operator that can preempt
#         return next(x for x in self.operators if x.checkIfResourceIsAvailable(callerObject=self))
        
    # =======================================================================
    #                           returns the resource
    # =======================================================================
    # TODO: check if it is valid to use it as filter in operatorPoolBroker run()
    def getResource(self,operator):
        # have to return the resource of the first operator available
        return operator.getResource()
    
    # =======================================================================
    #               returns the active queue of the resource
    #                         needs refining 
    # =======================================================================
    def getResourceQueue(self,operator):
        return operator.getResourceQueue()
    
                
    