'''
Created on 18 Jun 2014

@author: Panos
'''
from distutils.core import setup
import py2exe

setup(console=['C:\Eclipseworkspace\dreamgui\dream\dream\KnowledgeExtraction\PilotCases\JobShop\WorkplanExtractionJS.py'],
      options={
                "py2exe": {
                        "includes": ["decimal"]
                }
        }
)