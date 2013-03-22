'''
Created on 6 Feb 2013

@author: George
'''

'''
models a part entity that flows through the system
'''


from SimPy.Simulation import *
from Globals import G


#The entity object
class Part(object):    
    type="Part"
          
    def __init__(self, name):
        self.name=name
        self.currentStop=None      #contains the current object that the material is in 
        self.creationTime=0
        self.startTime=0           #holds the startTime for the lifespan
