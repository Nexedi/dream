# ===========================================================================
# Copyright 2015 Dublin City University
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
Created on 27 Nov 2014

@author: Anna
'''

from AllocManagement_Hybrid import AllocManagement_Hybrid2
from ImportInput import ImportInput
from outputResults import outputResults

def main(input):
    assert input, 'no input is provided, the algorithm cannot run'
    ImportInput(input)   
    AllocManagement_Hybrid2()
    outputResults()
