'''
Created on 8 Nov 2012

@author: George
'''

'''
script for making the project into a standalone .exe file
this fails since I used sciPy
'''

from distutils.core import setup
import py2exe

setup(
          options = {
            "py2exe":{
            #"dll_excludes": [ "HID.DLL", "libmmd.dll","w9xpopen.exe"],        
            #"MSVCP90.dll","libifcoremd.dll",
        }
    },
      
      
      console=['Line01.py'])
