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
Created on 22 Nov 2012

@author: Ioannis
'''
'''
Models a machine that can also have failures
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold, request, release

from Failure import Failure
# from CoreObject import CoreObject
from Machine import Machine

from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat

# ===========================================================================
# the Machine object
# ===========================================================================
# class Machine(CoreObject):
class OperatedMachine(Machine):
    # =======================================================================
    #  initialize the id the capacity, of the resource and the distribution
    # =======================================================================  
    def __init__(self, id, name, capacity=1, distribution='Fixed', mean=1, stdev=0, min=0, max=10,\
                  failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None',\
                  operator='None',operationType='None',\
                  setupDistribution="No",setupMean=0, setupStdev=0, setupMin=0, setupMax=10):
        Machine.__init__(self, id, name, capacity, distribution, mean, stdev, min, max,\
                          failureDistribution, MTTF, MTTR, availability, repairman)
        # type of the machine
        self.type = "OperatedMachine"
        # sets the operator resource of the Machine
        self.operator=operator
        # define if setup/removal/processing are performed by the operator 
        self.operationType=operationType
        # boolean to check weather the machine is being operated
        self.toBeOperated = False
        # define the setup times
        self.setupDistType=setupDistribution 
        self.stpRng=RandomNumberGenerator(self, self.setupDistType)
        self.stpRng.avg=setupMean
        self.stpRng.stdev=setupStdev
        self.stpRng.min=setupMin
        self.stpRng.max=setupMax
        # examine if there are multiple operation types performed by the operator
        self.multOperationTypeList=[]   # there can be Setup/Processing operationType 
                                        #     or the combination of both (MT-Setup-Processing)
        if self.operationType.startswith("MT"):
            OTlist = operationType.split('-')
            self.operationType=OTlist.pop(0)
            self.multOperationTypeList = OTlist
        else:
            self.multOperationTypeList.append(self.operationType)
            
    # =======================================================================
    #                     initialize the machine
    # =======================================================================
    def initialize(self):
        Machine.initialize(self)
        self.broker = Broker(self)
        activate(self.broker,self.broker.run())
        self.call=False
        self.set=False
        self.totalTimeWaitingForOperator=0
        
    # =======================================================================
    #                the main process of the machine
    # =======================================================================
    def run(self):
        # execute all through simulation time
        while 1:
            # wait until the machine can accept an entity and one predecessor requests it 
            # canAcceptAndIsRequested is invoked to check when the machine requested to receive an entity  
            yield waituntil, self, self.canAcceptAndIsRequested
            
    # ======= request a resource
            if(self.operator!="None"):
                # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
                # machines waits to be operated (waits for the operator)
                self.operateMachine()
                # wait until the Broker has waited times equal to setupTime (if any)
                yield waituntil, self, self.brokerIsSet
                
            # get the entity
            self.getEntity()
            
    # ======= release a resource
            if (self.operator!="None")\
                and any(type=="Setup" for type in self.multOperationTypeList)\
                and not any(type=="Processing" for type in self.multOperationTypeList):
                # after getting the entity release the operator
                # machine has to release the operator
                self.releaseMachine()
                # wait until the Broker has finished processing
                yield waituntil, self, self.brokerIsSet
            
          
                
            # set the currentEntity as the Entity just received and initialize the timer timeLastEntityEntered
            self.currentEntity=self.getActiveObjectQueue()[0]       # entity is the current entity processed in Machine
            self.nameLastEntityEntered=self.currentEntity.name      # this holds the name of the last entity that got into Machine                   
            self.timeLastEntityEntered=now()                        #this holds the last time that an entity got into Machine  
            # variables dedicated to hold the processing times, the time when the Entity entered, 
            # and the processing time left 
            timeEntered=now()                                       # timeEntered dummy Timer that holds the time the last Entity Entered
            tinMStart=self.calculateProcessingTime()                # get the processing time, tinMStarts holds the processing time of the machine 
            tinM=tinMStart                                          # timer to hold the processing time left
            self.processingTimeOfCurrentEntity=tinMStart            # processing time of the machine 
                                                            
            # variables used to flag any interruptions and the end of the processing     
            interruption=False    
            processingEndedFlag=True 
            # timers to follow up the failure time of the machine while on current Entity
            failureTime=0                                           # dummy variable keeping track of the failure time 
                                                                    # might be feasible to avoid it
            self.downTimeInCurrentEntity=0                          #holds the total time that the 
                                                                    #object was down while holding current entity
            # this loop is repeated until the processing time is expired with no failure
            # check when the processingEndedFlag switched to false              
            while processingEndedFlag:
                # tBefore : dummy variable to keep track of the time that the processing starts after 
                #           every interruption                        
                tBefore=now()
                # wait for the processing time left tinM, if no interruption occurs then change the 
                # processingEndedFlag and exit loop,
                # else (if interrupted()) set interruption flag to true (only if tinM==0),
                # and recalculate the processing time left tinM,
                # passivate while waiting for repair.             
                yield hold,self,tinM                                # getting processed for remaining processing time tinM
                if self.interrupted():                              # if a failure occurs while processing the machine is interrupted.
                    # output to trace that the Machine (self.objName) got interrupted                                                                  
                    self.outputTrace(self.getActiveObjectQueue()[0].name, "Interrupted at "+self.objName)
                    # recalculate the processing time left tinM
                    tinM=tinM-(now()-tBefore)
                    if(tinM==0):            # sometimes the failure may happen exactly at the time that the processing would finish
                                            # this may produce disagreement with the simul8 because in both SimPy and Simul8
                                            # it seems to be random which happens 1st
                                            # this should not appear often to stochastic models though where times are random
                        interruption=True
                    # passivate the Machine for as long as there is no repair
                    # start counting the down time at breatTime dummy variable
                    breakTime=now()                                 # dummy variable that the interruption happened
                    
    # =============== release the operator if there is failure
                    if (self.operator!="None")\
                        and any(type=="Processing" for type in self.multOperationTypeList):
                        self.releaseMachine()
                        yield waituntil,self,self.brokerIsSet 
                    
                    # if there is a failure in the machine it is passivated                    
                    yield passivate,self                            
                    # use the timers to count the time that Machine is down and related 
                    self.downTimeProcessingCurrentEntity+=now()-breakTime       # count the time that Machine is down while processing this Entity
                    self.downTimeInCurrentEntity+=now()-breakTime               # count the time that Machine is down while on currentEntity
                    self.timeLastFailureEnded=now()                             # set the timeLastFailureEnded
                    failureTime+=now()-breakTime                                # dummy variable keeping track of the failure time 
                    # output to trace that the Machine self.objName was passivated for the current failure time
                    self.outputTrace(self.getActiveObjectQueue()[0].name, "passivated in "+self.objName+" for "+str(now()-breakTime))
                    
    # =============== request a resource after the repair
                    if (self.operator!="None")\
                        and any(type=="Processing" for type in self.multOperationTypeList)\
                        and not interruption:
                        self.operateMachine()
                        yield waituntil,self,self.brokerIsSet 
                                  
                # if no interruption occurred the processing in M1 is ended 
                else:
                    processingEndedFlag=False
            # output to trace that the processing in the Machine self.objName ended 
            self.outputTrace(self.getActiveObjectQueue()[0].name,"ended processing in "+self.objName)
            
    # =============== release resource after the end of processing
            if any(type=="Processing" for type in self.multOperationTypeList)\
                and not iterruption: 
                self.releaseMachine()
                yield waituntil,self,self.brokerIsSet 

            
            # set the variable that flags an Entity is ready to be disposed 
            self.waitToDispose=True
            # update the total working time 
            self.totalWorkingTime+=tinMStart                        # the total processing time for this entity 
                                                                    # is what the distribution initially gave
                                                                    
            # update the variables keeping track of Entity related attributes of the machine    
            self.timeLastEntityEnded=now()                          # this holds the time that the last entity ended processing in Machine 
            self.nameLastEntityEnded=self.currentEntity.name        # this holds the name of the last entity that ended processing in Machine
            self.completedJobs+=1                                   # Machine completed one more Job
            # re-initialize the downTimeProcessingCurrentEntity.
            # a new machine is about to enter
            self.downTimeProcessingCurrentEntity=0
               
            # dummy variable requests the successor object now
            reqTime=now()                                           # entity has ended processing in Machine and requests for the next object 
            # initialize the timer downTimeInTryingToReleaseCurrentEntity, we have to count how much time 
            # the Entity will wait for the next successor to be able to accept (canAccept)
            self.downTimeInTryingToReleaseCurrentEntity=0
                
            while 1:
                # wait until the next Object is available or machine has failure
                yield waituntil, self, self.ifCanDisposeOrHaveFailure 
                 
                
                # if Next object available break      
                if self.Up:   
                    break
                # if M1 had failure, we want to wait until it is fixed and also count the failure time. 
                else:
                    failTime=now()                                  # dummy variable holding the time failure happened
                    # passivate until machine is up
                    yield waituntil, self, self.checkIfMachineIsUp  
                    failureTime+=now()-failTime                     # count the failure while on current entity time with failureTime variable
                    # calculate the time the Machine was down while trying to dispose the current Entity, 
                    # and the total down time while on current Entity
                    self.downTimeInTryingToReleaseCurrentEntity+=now()-failTime         
                    self.downTimeInCurrentEntity+=now()-failTime    # already updated from failures during processing
                    # update the timeLastFailureEnded   
                    self.timeLastFailureEnded=now()           
                            
            totalTime=now()-timeEntered                             # dummy variable holding the total time the Entity spent in the Machine
            blockageTime=totalTime-(tinMStart+failureTime)          # count the time the Machine was blocked subtracting the failureTime 
                                                                    #    and the processing time from the totalTime spent in the Machine
            # might be possible to avoid using blockageTime
            #    self.totalBlockageTime+=blockageTime
            self.totalBlockageTime+=totalTime-(tinMStart+failureTime)   #the time of blockage is derived from 
                                                                                         #the whole time in the machine
                                                                                         #minus the processing time and the failure time
    
   
    # =======================================================================
    # checks if the Machine can accept an entity       
    # it checks also who called it and returns TRUE only to the predecessor 
    # that will give the entity.
    # =======================================================================  
    def canAccept(self, callerObject=None):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        
        # if we have only one predecessor just check if there is a place and the machine is up
        # this is done to achieve better (cpu) processing time 
        # then we can also use it as a filter for a yield method
        if(len(activeObject.previous)==1 or callerObject==None):      
            return (activeObject.operator=='None' or activeObject.operator.checkIfResourceIsAvailable())\
                and activeObject.Up and len(activeObjectQueue)==0
                      
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        return (activeObject.operator=='None' or activeObject.operator.checkIfResourceIsAvailable())\
            and len(activeObjectQueue)<activeObject.capacity and (thecaller is giverObject)
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some predecessor waiting for it
    # also updates the predecessorIndex to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
                
        # if we have only one predecessor just check if there is a place, 
        # the machine is up and the predecessor has an entity to dispose
        # this is done to achieve better (cpu) processing time
        if(len(activeObject.previous)==1):
            return (activeObject.operator=='None' or activeObject.operator.checkIfResourceIsAvailable())\
                 and activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                 and giverObject.haveToDispose(activeObject) 
        
        # dummy variables that help prioritize the objects requesting to give objects to the Machine (activeObject)
        isRequested=False                                           # is requested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked
        
        # loop through the predecessors to see which have to dispose and which is the one blocked for longer
        i=0                                                         # index used to set the predecessorIndex to the giver waiting the most
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject)):
                isRequested=True                                    # if the predecessor objects have entities to dispose of
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the predecessor has been down while trying to give away the Entity
                    timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                else:
                    timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
                
                #if more than one predecessor have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.predecessorIndex=i                 # the object to deliver the Entity to the activeObject is set to the ith member of the previous list
                    maxTimeWaiting=timeWaiting    
            i+=1                                                    # in the next loops, check the other predecessors in the previous list
        return (activeObject.operator=='None' or activeObject.operator.checkIfResourceIsAvailable())\
            and activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested
            
    # =======================================================================
    #                 calculates the setup time
    # =======================================================================
    def calculateSetupTime(self):
        return self.stpRng.generateNumber()
    
    # =======================================================================
    #                        call the broker 
    #                   filter for yield waituntil 
    # =======================================================================
    def brokerIsCalled(self):
        return self.call 
    
    # =======================================================================
    #         the broker returns control to OperatedMachine.Run
    #                     filter for yield request/release  
    # =======================================================================
    def brokerIsSet(self):
        return not self.call
    
    # =======================================================================
    #                       invoke the broker
    # =======================================================================
    def invokeBroker(self):
        self.call=True
#         self.set=not self.call
    
    # =======================================================================
    #               prepare the machine to be operated
    # =======================================================================
    def operateMachine(self):
        self.invokeBroker()
        self.toBeOperated = True
    
    # =======================================================================
    #               prepare the machine to be released
    # =======================================================================
    def releaseMachine(self):
        self.invokeBroker()
        self.toBeOperated = False
        
    # =======================================================================
    #           check if the machine is currently operated
    # =======================================================================
    def isOperated(self):
        return self.toBeOperated
    
# ===========================================================================
#            Method that handles the Operator Behavior
# ===========================================================================
class Broker(Process):
    def __init__(self, operatedMachine):
        Process.__init__(self)
        self.operatedMachine=operatedMachine      # the machine that is handled by the broker
        self.setupTime = 0
        self.timeOperationStarted = 0;
        self.timeWaitForOperatorStarted=0
        
    # =======================================================================
    #                       exit the broker
    # =======================================================================
    def exitBroker(self):
        self.operatedMachine.call=False
#         self.operatedMachine.set=not self.operatedMachine.call
    
    def run(self):
        while 1:
            yield waituntil,self,self.operatedMachine.brokerIsCalled # wait until the broker is called
    # ======= request a resource
                # have to see if the availability of resources is enough to check weather the machine is operated
                # or not
            if self.operatedMachine.isOperated()\
                and any(type=="Setup" or type=="Processing" for type in self.operatedMachine.multOperationTypeList):
                
                # update the time that the station is waiting for the operator
                self.timeWaitForOperatorStarted=now() 
                yield request,self,self.operatedMachine.operator.getResource()
                self.operatedMachine.totalTimeWaitingForOperator+=now()-self.timeWaitForOperatorStarted
                
                # update the time that the operation started
                self.timeOperationStarted=now()
                self.operatedMachine.operator.timeLastOperationStarted=now()
                if any(type=="Setup" for type in self.operatedMachine.multOperationTypeList):
                    self.setupTime = self.operatedMachine.calculateSetupTime()
                    yield hold,self,self.setupTime
    # ======= release a resource
                # have to see if the availability of resources is enough to check weather the machine is operated        
            elif not self.operatedMachine.isOperated():
                self.operatedMachine.operator.totalWorkingTime+=now()-self.timeOperationStarted
                yield release,self,self.operatedMachine.operator.getResource()

            else:
                pass
            
            self.exitBroker()
                    
              