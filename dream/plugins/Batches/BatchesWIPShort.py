from copy import copy
import json
import time
import random
import operator
import datetime

from dream.plugins import plugin

class BatchesWIPShort(plugin.InputPreparationPlugin):
    """ Input preparation 
        reads the WIP from the short format
    """

    def preprocess(self, data):
        print 1
        return data