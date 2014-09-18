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

# from SimPy.Simulation import Resource, now
import simpy
import xlwt
from ObjectResource import ObjectResource
from Operator import Operator

# ===========================================================================
#               the resource that handles multiple operators
# ===========================================================================
class OperatorPool(ObjectResource):
    
    def __init__(self, id, name, capacity=1, operatorsList='None',**kw):

        capacity = int(capacity or 1)

        self.id=id
        self.objName=name
        
        self.type="OperatorPool"
        # list with the coreObjects IDs that the Operators operate
        self.coreObjectIds=[]
        # list with the coreObjects that the Operators operate
        self.coreObjects=[]
        # holds the object/Machine that currently handles the operator pool
        self.currentObject='None'
        # if operatorsList is of type list and of length 0
        #     then no operators will be created, they may be 
        #     populated earlier on by the logic of the Stations
        if operatorsList!='None' and len(operatorsList)==0:
            # list of operators that the OperatorPool holds
            self.operators = []
            # the capacity of the OperatorPool in Operators
            self.capacity=capacity
        # check if an operatorsList is 'None'
        elif operatorsList=='None':
            # list of operators that the OperatorPool holds
            self.operators = []
            # the capacity of the OperatorPool in Operators
            self.capacity=capacity
            # populate the the operators list and initiate the operators
            for index in range(self.capacity):
                id=self.id+'_O_'+str(index)
                name=self.objName+'_Operator_'+str(index)
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
        # initialize the operators
        # an operator that may have been initialized by an other operator pool, is initiated again
        # TODO: reconsider
        for operator in self.operators:
            if not operator.isInitialized():
                operator.initialize()
            
    # =======================================================================
    #                  checks if there are operators available
    # =======================================================================       
    def checkIfResourceIsAvailable(self): 
        return any(operator.checkIfResourceIsAvailable()==True for operator in self.operators)
    
    # =======================================================================
    #              find the first available operator and return it
    # =======================================================================
    def findAvailableOperator(self):            # may need to implement different sorting of the operators
        # find the free operator if any
        freeOperator = None
        for operator in self.operators:
            if operator.checkIfResourceIsAvailable():
                freeOperator=operator
                break
        return freeOperator
    
    #===========================================================================
    # returns the operators that are currently available
    #===========================================================================
    def availableOperators(self):
        return [operator for operator in self.operators if operator.checkIfResourceIsAvailable()]
        
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
    
                
    
