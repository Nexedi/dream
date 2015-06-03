'''
Created on 3 Jun 2015

@author: Panos
'''
from distutils.core import setup
import py2exe

setup(console=['C:\Eclipseworkspace\dreamgui\dream\dream\KnowledgeExtraction\PilotCases\JobShop\ExtendedWorkplanExtraction.py'],
      options={
                "py2exe": {
                        "includes": ["decimal"]
                }
        }
)