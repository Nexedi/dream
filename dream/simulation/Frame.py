'''
Created on 18 Feb 2013

@author: George
'''

'''
models a frame entity. This can flow through the system and carry parts
'''

from SimPy.Simulation import *
from Globals import G

#The entity object
class Frame(object):    
    type="Frame"
    numOfParts=4    #the number of parts that the frame can take
          
    def __init__(self, name):
        self.name=name
        self.currentStop=None      #contains the current object that the material is in 
        self.creationTime=0
        self.startTime=0           #holds the startTime for the lifespan
        self.Res=Resource(self.numOfParts)
        #dimension data
        self.width=2.0
        self.height=2.0
        self.lenght=2.0        
        

