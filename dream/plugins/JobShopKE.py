from copy import copy, deepcopy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class JobShopKE(plugin.InputPreparationPlugin):
    """ Input preparation 
    """

    def preprocess(self, data):
        print 'arkouda'
        from dream.KnowledgeExtraction.PilotCases.JobShop.DataExtraction import DataExtraction
        
        print '!!!!!!!!!!'
        print data['general']
        return data

    