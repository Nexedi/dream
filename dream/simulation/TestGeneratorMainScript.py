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
Created on 4 Dec 2013

@author: George
'''
'''
test script to test the generator
'''

from SimPy.Simulation import now, activate,simulate, infinity,initialize
from EventGenerator import EventGenerator
from Machine import Machine
from Source import Source
from Exit import Exit
from Part import Part
from Queue import Queue
from Globals import G
import ExcelHandler
import Globals


G.trace="Yes"           
            
S=Source('S1','Source', mean=1, item=Part)
M1=Machine('M1','Machine1', mean=0.75)
Q1=Queue('Q1','Queue1',capacity=infinity)
M2=Machine('M2','Machine2', mean=0.75)
Q2=Queue('Q2','Queue2',capacity=infinity)
E=Exit('E1','Exit')  

#define predecessors and successors for the objects    
S.defineRouting([M1])
M1.defineRouting([S],[Q1])
Q1.defineRouting([M1],[M2])
M2.defineRouting([Q1],[Q2])
Q2.defineRouting([M2])

argumentDict={'from':'Q2','to':'E1','safetyStock':70,'consumption':20}
EG=EventGenerator(id="EV", name="ExcessEntitiesMover" ,start=60, interval=60, method=Globals.moveExcess, argumentDict=argumentDict)
G.ObjList=[S,M1,M2,E,Q1,Q2,EG]

initialize()                        #initialize the simulation (SimPy method)
    
for object in G.ObjList:
    object.initialize()

for object in G.ObjList:
    activate(object, object.run())
    
G.maxSimTime=400
simulate(until=G.maxSimTime)    #run the simulation

#carry on the post processing operations for every object in the topology       
for object in G.ObjList:
    object.postProcessing()

ExcelHandler.outputTrace('TRACE')

print "the system produced", E.numOfExits, "parts"
print "the waiting ratio of", M1.objName,  "is", (M1.totalWaitingTime/G.maxSimTime)*100, "%"
print "the waiting ratio of", M2.objName,  "is", (M2.totalWaitingTime/G.maxSimTime)*100, "%"




