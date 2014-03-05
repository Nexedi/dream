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
Created on 8 Nov 2012

@author: George
'''
'''
carries some global variables
'''

#from SimPy.Simulation import *
from Machine import Machine
from Queue import Queue
from Repairman import Repairman
import xlwt
import xlrd
from random import Random, expovariate, gammavariate, normalvariate
from SimPy.Simulation import now
import scipy.stats as stat

# ===========================================================================
# globals
# ===========================================================================
class G:   
    seed=1450                       #the seed of the random number generator
    Rnd = Random(seed)              #random number generator
    

    ObjList=[]                      #a list that holds all the CoreObjects 
    EntityList=[]                   #a list that holds all the Entities 
    
    numberOfReplications=1          #the number of replications default=1
    confidenceLevel=0.9             #the confidence level default=90%
    Base=1                          #the Base time unit. Default =1 minute
    maxSimTime=0                    #the total simulation time
    
    # data for the trace output in excel
    # -----------------------------------------------------------------------
    trace=""                        #this is written from input. If it is "Yes" then you write to trace, else we do not
    traceIndex=0                    #index that shows in what row we are
    sheetIndex=1                    #index that shows in what sheet we are
    traceFile = xlwt.Workbook()     #create excel file
    traceSheet = traceFile.add_sheet('sheet '+str(sheetIndex), cell_overwrite_ok=True)  #create excel sheet    
    
    
    # variables for excel output
    # -----------------------------------------------------------------------
    outputIndex=0                   #index that shows in what row we are
    sheetIndex=1                    #index that shows in what sheet we are
    outputFile = xlwt.Workbook()    #create excel file
    outputSheet = outputFile.add_sheet('sheet '+str(sheetIndex), cell_overwrite_ok=True)  #create excel sheet
    
    #variables for json output
    # -----------------------------------------------------------------------
    outputJSON={}
    outputJSONFile=None
    
    numberOfEntities = 0
    
# =======================================================================
# method to move entities exceeding a certain safety stock
# =======================================================================
def moveExcess(argumentDict={}):
    giver=findObjectById(argumentDict.get('from', None))
    receiver=findObjectById(argumentDict.get('to', None))
    safetyStock=int(argumentDict.get('safetyStock', 10))
    consumption=int(argumentDict.get('consumption', 1))
    if giver and receiver:
        if len(giver.getActiveObjectQueue())>safetyStock:
            giver.receiver=receiver
            receiver.giver=giver
            for i in range(consumption):
                receiver.getEntity()         
            giver.next=[]
            receiver.previous=[]
    else:
        print "Giver and/or Receiver not defined"

# =======================================================================
# Import a class from a dotted name used in json.
# =======================================================================
def getClassFromName(dotted_name):
  # XXX dotted name is always Dream.Something, but the real class lives in
  # dream.simulation.Something.Something
  dream, class_name = dotted_name.split('.')
  import dream.simulation as ds
  __import__('dream.simulation.%s' % class_name)
  return getattr(getattr(ds, class_name), class_name)

# =======================================================================
# method finding objects by ID
# =======================================================================
def findObjectById(id):
    for obj in G.ObjList:
        if obj.id==id:
            return obj
    return None

# =======================================================================
# Error in the setting up of the WIP
# =======================================================================
class SetWipTypeError(Exception):
    def __init__(self, setWipError):
        Exception.__init__(self, setWipError) 
# =======================================================================
# method to set-up the entities in the current stations 
# as Work In Progress
# -----------------------------------------
# in this case the current station must be defined! 
# otherwise there is no current station but a list of possible stations
# although the entity cannot be in more than one stations
# =======================================================================
def setWIP(entityList):
    # for all the entities in the entityList
    for entity in entityList:
        # if the entity is of type Part
        if entity.type=='Part':
            object=entity.currentStation                        #identify the object
            object.getActiveObjectQueue().append(entity)        #append the entity to its Queue
            entity.schedule.append([object,now()])              #append the time to schedule so that it can be read in the result
            
        
        # if the entity is of type Job/OrderComponent/Order/Mould
        elif entity.type=='Job' or 'OrderComponent' or 'Order' or 'Mould':
            # find the list of starting station of the entity
            currentObjectIds=entity.remainingRoute[0].get('stationIdsList',[])
            # if the list of starting stations has length greater than one then there is a starting WIP definition error 
            try:
                if len(currentObjectIds)==1:
                    objectId=currentObjectIds[0]
                else:
                    raise SetWipTypeError('The starting station of the the entity is not defined uniquely')
            except SetWipTypeError as setWipError:
                print 'WIP definition error: {0}'.format(setWipError)
            # get the starting station of the entity and load it with it
            object = findObjectById(objectId)
            object.getActiveObjectQueue().append(entity)        # append the entity to its Queue
            
            # read the IDs of the possible successors of the object
            nextObjectIds=entity.remainingRoute[1].get('stationIdsList',[])
            # for each objectId in the nextObjects find the corresponding object and populate the object's next list
            nextObjects=[]
            for nextObjectId in nextObjectIds:
                nextObject=findObjectById(nextObjectId)
                nextObjects.append(nextObject)  
            # update the next list of the object
            for nextObject in nextObjects:
                # append only if not already in the list
                if nextObject not in object.next:
                    object.next.append(nextObject)
            
            entity.remainingRoute.pop(0)                        # remove data from the remaining route.   
            entity.schedule.append([object,now()])              #append the time to schedule so that it can be read in the result
            entity.currentStation=object                        # update the current station of the entity 
        # if the currentStation of the entity is of type Machine then the entity 
        #     must be processed first and then added to the pendingEntities list
        #     Its hot flag is not raised
        if not (entity.currentStation in G.MachineList):    
            # variable to inform whether the successors are machines or not
            successorsAreMachines=True
            for nextObject in entity.currentStation.next:
                if not nextObject in G.MachineList:
                    successorsAreMachines=False
                    break
            if not successorsAreMachines:
                entity.hot = False
            else:
                entity.hot = True
            # add the entity to the pendingEntities list
            G.pendingEntities.append(entity)

from Exit import Exit
def countIntervalThroughput(argumentDict={}):
    currentExited=0  
    for obj in G.ObjList:
        if isinstance(obj, Exit):
            totalExited=obj.totalNumberOfUnitsExited
            previouslyExited=sum(obj.intervalThroughPutList)
            currentExited+=totalExited-previouslyExited
            obj.intervalThroughPutList.append(currentExited)


from Queue import Queue
def countQueueMetrics(argumentDict={}):
    for obj in G.ObjList:
        if isinstance(obj, Queue):
            obj.wip_stat_list.append((now(), len(obj.Res.activeQ)))


# =======================================================================
# Helper function to calculate the min, max and average values of a serie
# =======================================================================
def getConfidenceIntervals(value_list):
    from Globals import G
    if len(set(value_list)) == 1:
        # All values are same, no need to perform statistical analysis
        return { 'min': value_list[0],
                 'max': value_list[0],
                 'avg': value_list[0], }
    bayes_mvs = stat.bayes_mvs(value_list, G.confidenceLevel)
    return { 'min': bayes_mvs[0][1][0],
             'max': bayes_mvs[0][1][1],
             'avg': bayes_mvs[0][0], }

