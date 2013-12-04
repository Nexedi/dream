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

from SimPy.Simulation import now, activate,simulate
from EventGenerator import EventGenerator

def myMethod():
    print "I was invoked at", now()

EG=EventGenerator(start=60, interval=60, method=myMethod)
activate(EG, EG.run())
simulate(until=480)    #run the simulation








