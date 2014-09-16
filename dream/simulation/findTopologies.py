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
Created on 16 Sep 2014

@author: GDang
'''
'''
auxiliary script to search for specific objects in topologies
'''

keyString=raw_input('give the string to find:')
numberFound=0
import os
for filename in os.listdir(os.getcwd()+'\JSONInputs'):
    if filename.endswith('.json'):
        file=open(os.path.join('JSONInputs', filename), "r")
        content = file.readlines()
        i=1
        for line in content:
            if keyString in line:
                print 'found in', filename, 'line',i 
                print '---->', line
                numberFound+=1
            i+=1
print 'search ended. Found', numberFound, 'instances'
   
   