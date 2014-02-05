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
Models a machine that can also have failures
'''

from SimPy.Simulation import Process, Resource
from SimPy.Simulation import activate, passivate, waituntil, now, hold, request, release

from Failure import Failure
from CoreObject import CoreObject

from OperatedPoolBroker import Broker
from OperatorPool import OperatorPool

from RandomNumberGenerator import RandomNumberGenerator
import scipy.stats as stat

# ===========================================================================
# the Machine object
# ===========================================================================
class Machine(CoreObject):
    # =======================================================================
    # initialise the id the capacity, of the resource and the distribution
    # =======================================================================
    def __init__(self, id, name, capacity=1, distribution='Fixed', mean=1, stdev=0, min=0, max=10,\
                  failureDistribution='No', MTTF=0, MTTR=0, availability=0, repairman='None',\
                  operatorPool='None',operationType='None',\
                  loadDistribution="No",loadMean=0, loadStdev=0, loadMin=0, loadMax=10,
                  setupDistribution="No",setupMean=0, setupStdev=0, setupMin=0, setupMax=10,
                  isPreemptive=False, resetOnPreemption=False):
        CoreObject.__init__(self)
        # hold the id, name, and type of the Machine instance
        self.id=id
        self.objName=name
        self.type="Machine"                         #String that shows the type of object
        #     holds the capacity of the machine 
        self.capacity=capacity
        #     define the distribution types of the processing and failure times respectively
        self.distType=distribution                  #the distribution that the procTime follows      
        self.failureDistType=failureDistribution    #the distribution that the failure follows   
        #     sets the repairman resource of the Machine
        self.repairman=repairman         
        #     Sets the attributes of the processing (and failure) time(s)
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=mean
        self.rng.stdev=stdev
        self.rng.min=min
        self.rng.max=max
        self.MTTF=MTTF
        self.MTTR=MTTR
        self.availability=availability
        ''' sets the operator resource of the Machine
             check if the operatorPool is a List or a OperatorPool type Object
             if it is a list then initiate a OperatorPool type object containing
             the list of operators provided
            if the  list is empty create operator pool with empty list
        '''
        if (type(operatorPool) is list) and len(operatorPool)>0:
            id = id+'_OP'
            name=self.objName+'_operatorPool'
            self.operatorPool=OperatorPool(id, name, operatorsList=operatorPool)
        elif(type(operatorPool) is OperatorPool):
            self.operatorPool=operatorPool         
        else:
            self.operatorPool='None'
            #self.operatorPool=operatorPool
        # update the operatorPool coreObjects list
        if self.operatorPool!='None':
             self.operatorPool.coreObjectIds.append(self.id)
             self.operatorPool.coreObjects.append(self)
        # holds the Operator currently processing the Machine
        self.currentOperator=None
        # define if load/setup/removal/processing are performed by the operator 
        self.operationType=operationType
        # boolean to check whether the machine is being operated
        self.toBeOperated = False
        # define the load times
        self.loadDistType=loadDistribution 
        self.loadRng=RandomNumberGenerator(self, self.loadDistType)
        self.loadRng.avg=loadMean
        self.loadRng.stdev=loadStdev
        self.loadRng.min=loadMin
        self.loadRng.max=loadMax
        # variable that informs on the need for setup
        self.setUp=True
        # define the setup times
        self.setupDistType=setupDistribution 
        self.stpRng=RandomNumberGenerator(self, self.setupDistType)
        self.stpRng.avg=setupMean
        self.stpRng.stdev=setupStdev
        self.stpRng.min=setupMin
        self.stpRng.max=setupMax
        # examine if there are multiple operation types performed by the operator
        #     there can be Setup/Processing operationType
        #     or the combination of both (MT-Load-Setup-Processing) 
        self.multOperationTypeList=[]   
        if self.operationType.startswith("MT"):
            OTlist = operationType.split('-')
            self.operationType=OTlist.pop(0)
            self.multOperationTypeList = OTlist
        else:
            self.multOperationTypeList.append(self.operationType)
        #     lists to hold statistics of multiple runs
        self.WaitingForOperator=[]
        self.WaitingForLoadOperator=[]
        self.Loading = []
        self.SettingUp =[]
        
        self.isPreemptive=isPreemptive
        self.resetOnPreemption=resetOnPreemption
    
    # =======================================================================
    # initialize the machine
    # =======================================================================        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)        
        # initialize the internal Queue (type Resource) of the Machine 
        self.Res=Resource(self.capacity)
        # initiate the Broker responsible to control the request/release
        # initialize the operator pool if any
        if (self.operatorPool!="None"):
            self.operatorPool.initialize()
            self.broker = Broker(self)
            activate(self.broker,self.broker.run())
            for operator in self.operatorPool.operators:
                operator.coreObjectIds.append(self.id)
                operator.coreObjects.append(self)
        # the time that the machine started/ended its wait for the operator
        self.timeWaitForOperatorStarted=0
        self.timeWaitForOperatorEnded=0
        self.totalTimeWaitingForOperator=0
        # the time that the machine started/ended its wait for the operator
        self.timeWaitForLoadOperatorStarted=0
        self.timeWaitForLoadOperatorEnded=0
        self.totalTimeWaitingForLoadOperator=0
        # the time that the operator started/ended loading the machine
        self.timeLoadStarted=0
        self.timeLoadEnded=0
        self.totalLoadTime=0
        # the time that the operator started/ended setting-up the machine
        self.timeSetupStarted=0
        self.timeSetupEnded=0
        self.totalSetupTime=0
        # Current entity load/setup/loadOperatorwait/operatorWait related times 
        self.operatorWaitTimeCurrentEntity=0        # holds the time that the machine was waiting for the operator
        self.loadOperatorWaitTimeCurrentEntity = 0  # holds the time that the machine waits for operator to load the it
        self.loadTimeCurrentEntity = 0              # holds the time to load the current entity
        self.setupTimeCurrentEntity = 0             # holds the time to setup the machine before processing the current entity
        # TODO: check whether the requestingEntity variable can be used in OperatorPreemptive
        self.requestingEntity=None
    
    # =======================================================================
    # the main process of the machine
    # =======================================================================
    def run(self):
        # execute all through simulation time
        while 1:
            # wait until the machine can accept an entity and one predecessor requests it 
            # canAcceptAndIsRequested is invoked to check when the machine requested to receive an entity  
            yield waituntil, self, self.canAcceptAndIsRequested           
            # here or in the get entity (apart from the loatTimeCurrentEntity)
            # in case they are placed inside the getEntity then the initialize of
            # the corresponding variables should be moved to the initialize() of the CoreObject
            self.operatorWaitTimeCurrentEntity = 0
            self.loadOperatorWaitTimeCurrentEntity = 0
            self.loadTimeCurrentEntity = 0
            self.setupTimeCurrentEntity = 0
            
    # ======= request a resource
            if(self.operatorPool!="None") and any(type=='Load' for type in self.multOperationTypeList):
                # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
                # machines waits to be operated (waits for the operator)
                self.requestOperator()
                self.timeWaitForLoadOperatorStarted = now()
                # wait until the Broker has waited times equal to loadTime (if any)
                yield waituntil, self, self.broker.brokerIsSet
                self.timeWaitForLoadOperatorEnded = now()
                self.loadOperatorWaitTimeCurrentEntity += self.timeWaitForLoadOperatorEnded-self.timeWaitForLoadOperatorStarted
                self.totalTimeWaitingForLoadOperator += self.loadOperatorWaitTimeCurrentEntity 
                
    # ======= Load the machine if the Load is defined as one of the Operators' operation types
            if any(type=="Load" for type in self.multOperationTypeList) and self.isOperated():
                self.timeLoadStarted = now()
                yield hold,self,self.calculateLoadTime()
                # if self.interrupted(): There is the issue of failure during the Loading
                self.timeLoadEnded = now()
                self.loadTimeCurrentEntity = self.timeLoadEnded-self.timeLoadStarted 
                self.totalLoadTime += self.loadTimeCurrentEntity
                
    # ======= release a resource if the only operation type is Load
            if (self.operatorPool!="None")\
                 and any(type=="Load" for type in self.multOperationTypeList)\
                 and not (any(type=="Processing" for type in self.multOperationTypeList)\
                          or any(type=="Setup" for type in self.multOperationTypeList))\
                 and self.isOperated():
                # after getting the entity release the operator
                # machine has to release the operator
                self.releaseOperator()
                # wait until the Broker has finished processing
                yield waituntil, self, self.broker.brokerIsSet
            
            # TODO: reset the requestinEntity before receiving the currentEntity
            self.requestingEntity=None
            # get the entity
                    # TODO: if there was loading time then we must solve the problem of getting an entity
                    # from an unidentified giver or not getting an entity at all as the giver 
                    # may fall in failure mode (assignExit()?)
            self.currentEntity=self.getEntity()
            # TODO: the Machine receive the entity  after the operator is available
            #     the canAcceptAndIsRequested method checks only in case of Load type of operation 
            
    # ======= request a resource if it is not already assigned an Operator
            if(self.operatorPool!="None")\
                 and (any(type=="Processing" for type in self.multOperationTypeList)\
                      or any(type=="Setup" for type in self.multOperationTypeList))\
                 and not self.isOperated():
                # when it's ready to accept (canAcceptAndIsRequested) then inform the broker
                # machines waits to be operated (waits for the operator)
                self.requestOperator()
                self.timeWaitForOperatorStarted = now()
                # wait until the Broker has waited times equal to loadTime (if any)
                yield waituntil, self, self.broker.brokerIsSet
                self.timeWaitForOperatorEnded = now()
                self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
            
            # variables dedicated to hold the processing times, the time when the Entity entered, 
            # and the processing time left 
            self.totalProcessingTimeInCurrentEntity=self.calculateProcessingTime()                # get the processing time, tinMStarts holds the processing time of the machine 
            tinM=self.totalProcessingTimeInCurrentEntity                                          # timer to hold the processing time left
            
    # ======= setup the machine if the Setup is defined as one of the Operators' operation types
            # in plantSim the setup is performed when the machine has to process a new type of Entity and only once
            if any(type=="Setup" for type in self.multOperationTypeList) and self.isOperated():
                self.timeSetupStarted = now()
                yield hold,self,self.calculateSetupTime()
                # if self.interrupted(): There is the issue of failure during the setup
                self.timeSetupEnded = now()
                self.setupTimeCurrentEntity = self.timeSetupEnded-self.timeSetupStarted
                self.totalSetupTime += self.setupTimeCurrentEntity
            
    # ======= release a resource if the only operation type is Setup
            if (self.operatorPool!="None")\
                and self.isOperated()\
                and (any(type=="Setup" for type in self.multOperationTypeList)\
                     or any(type=="Load" for type in self.multOperationTypeList))\
                and not any(type=="Processing" for type in self.multOperationTypeList):
                # after getting the entity release the operator
                # machine has to release the operator
                self.releaseOperator()
                # wait until the Broker has finished processing
                yield waituntil, self, self.broker.brokerIsSet
                                                                                 
            # variables used to flag any interruptions and the end of the processing     
            interruption=False    
            processingNotFinished=True 
            # timers to follow up the failure time of the machine while on current Entity

            self.downTimeInCurrentEntity=0                          #holds the total time that the 
                                                                    #object was down while holding current entity
            
            # this loop is repeated until the processing time is expired with no failure
            # check when the processingEndedFlag switched to false              
            while processingNotFinished:
                # timeRestartingProcessing : dummy variable to keep track of the time that the processing starts after 
                #           every interruption                        
                timeRestartingProcessing=now()
                # wait for the processing time left tinM, if no interruption occurs then change the 
                # processingEndedFlag and exit loop,
                # else (if interrupted()) set interruption flag to true (only if tinM==0),
                # and recalculate the processing time left tinM,
                # passivate while waiting for repair.
                yield hold,self,tinM                                # getting processed for remaining processing time tinM
                if self.interrupted():                              # if a failure occurs while processing the machine is interrupted.
                    #self.interruptionActions()                      # execute interruption actions
                    # output to trace that the Machine (self.objName) got interrupted           
                    try:                                                       
                        self.outputTrace(self.getActiveObjectQueue()[0].name, "Interrupted at "+self.objName)
                    except IndexError:
                        pass
                    # recalculate the processing time left tinM
                    tinM=tinM-(now()-timeRestartingProcessing)
                    if(tinM==0):            # sometimes the failure may happen exactly at the time that the processing would finish
                                            # this may produce disagreement with the simul8 because in both SimPy and Simul8
                                            # it seems to be random which happens 1st
                                            # this should not appear often to stochastic models though where times are random
                        interruption=True
                    # passivate the Machine for as long as there is no repair
                    # start counting the down time at breatTime dummy variable
                    breakTime=now()                                 # dummy variable that the interruption happened
    
    # =============== release the operator if there is interruption 
                    if (self.operatorPool!="None")\
                        and self.isOperated()\
                        and any(type=="Processing" for type in self.multOperationTypeList):
                        self.releaseOperator()
                        yield waituntil,self,self.broker.brokerIsSet 
    
                    # if there is a failure in the machine it is passivated
                    yield passivate,self
                    # use the timers to count the time that Machine is down and related 
                    self.downTimeProcessingCurrentEntity+=now()-breakTime       # count the time that Machine is down while processing this Entity
                    self.downTimeInCurrentEntity+=now()-breakTime               # count the time that Machine is down while on currentEntity
                    self.timeLastFailureEnded=now()                             # set the timeLastFailureEnded
                    self.failureTimeInCurrentEntity+=now()-breakTime                                # dummy variable keeping track of the failure time 
                    # output to trace that the Machine self.objName was passivated for the current failure time
                    self.outputTrace(self.getActiveObjectQueue()[0].name, "passivated in "+self.objName+" for "+str(now()-breakTime))
                    
                    #if during the interruption the object became empty break        
                    if (len(self.getActiveObjectQueue())==0 and self.shouldPreempt):
                        break
                
    # =============== request a resource after the repair
                    if (self.operatorPool!="None")\
                        and any(type=="Processing" for type in self.multOperationTypeList)\
                        and not interruption:
                        self.timeWaitForOperatorStarted = now()
                        self.requestOperator()
                        yield waituntil,self,self.broker.brokerIsSet
                        self.timeWaitForOperatorEnded = now() 
                        self.operatorWaitTimeCurrentEntity += self.timeWaitForOperatorEnded-self.timeWaitForOperatorStarted
                
                # if no interruption occurred the processing in M1 is ended 
                else:
                    processingNotFinished=False
                    
            #if during the interruption the object became empty continue        
            if (len(self.getActiveObjectQueue())==0 and self.shouldPreempt):
                self.shouldPreempt=False
                self.totalWorkingTime+=now()-(self.timeLastEntityEntered)
                # TODO: Should release operator here
    # =============== release resource in case of preemption
                if (self.operatorPool!='None')\
                    and any(type=="Processing" for type in self.multOperationTypeList)\
                    and not interruption: 
                    self.releaseOperator()
                    yield waituntil,self,self.broker.brokerIsSet
                continue
            
            # output to trace that the processing in the Machine self.objName ended 
            try:
                self.outputTrace(self.getActiveObjectQueue()[0].name,"ended processing in "+self.objName)
            except IndexError:
                pass
                       
    # =============== release resource after the end of processing
            if (self.operatorPool!='None')\
                and any(type=="Processing" for type in self.multOperationTypeList)\
                and not interruption: 
                self.releaseOperator()
                yield waituntil,self,self.broker.brokerIsSet
            
            # set the variable that flags an Entity is ready to be disposed 
            self.waitToDispose=True
            # update the total working time 
            self.totalWorkingTime+=self.totalProcessingTimeInCurrentEntity                        # the total processing time for this entity 
                                                                    # is what the distribution initially gave
            
            # update the variables keeping track of Entity related attributes of the machine    
            self.timeLastEntityEnded=now()                          # this holds the time that the last entity ended processing in Machine 
            self.nameLastEntityEnded=self.currentEntity.name        # this holds the name of the last entity that ended processing in Machine
            self.completedJobs+=1                                   # Machine completed one more Job
            
            while 1:
                # wait until the next Object is available or machine has failure
                yield waituntil, self, self.ifCanDisposeOrHaveFailure
                
                # if Next object available break      
                if self.Up:   
                    break
                # if M1 had failure, we want to wait until it is fixed and also count the failure time. 
                else:
                    failTime=now()                                  # dummy variable holding the time failure happened
                    #self.interruptionActions()                      # execute interruption actions
                    # passivate until machine is up
                    yield waituntil, self, self.checkIfMachineIsUp  
                    self.failureTimeInCurrentEntity+=now()-failTime                     # count the failure while on current entity time with failureTime variable
                    # calculate the time the Machine was down while trying to dispose the current Entity, 
                    # and the total down time while on current Entity
                    self.downTimeInTryingToReleaseCurrentEntity+=now()-failTime         
                    self.downTimeInCurrentEntity+=now()-failTime    # already updated from failures during processing
                    # update the timeLastFailureEnded   
                    self.timeLastFailureEnded=now()
                    
                    #if during the interruption the object became empty break        
                    if (len(self.getActiveObjectQueue())==0 and self.shouldPreempt):
                        self.shouldPreempt==False
                        break     
                    
                            
    # =======================================================================
    # checks if the machine is Up
    # =======================================================================
    def checkIfMachineIsUp(self):
        return self.Up

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
            if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                    or any(type=='Setup' for type in activeObject.multOperationTypeList))):
                return activeObject.operatorPool.checkIfResourceIsAvailable()\
                        and activeObject.Up\
                        and len(activeObjectQueue)<activeObject.capacity
            else:
                return activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                      
        thecaller=callerObject
        # return True ONLY if the length of the activeOjbectQue is smaller than
        # the object capacity, and the callerObject is not None but the giverObject
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            return activeObject.operatorPool.checkIfResourceIsAvailable()\
                and activeObject.Up\
                and len(activeObjectQueue)<activeObject.capacity
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity and (thecaller is giverObject)
            # while if the set up is performed before the (automatic) loading of the machine then the availability of the
            # operator is requested
#             return (activeObject.operatorPool=='None' or activeObject.operatorPool.checkIfResourceIsAvailable())\
#                and activeObject.Up and len(activeObjectQueue)<activeObject.capacity
    
    # =======================================================================
    # checks if the Machine can accept an entity and there is an entity in 
    # some possible giver waiting for it
    # also updates the giver to the one that is to be taken
    # =======================================================================
    def canAcceptAndIsRequested(self):
        # get active and giver objects
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        giverObject=self.getGiverObject()
        # if we have only one predecessor just check if there is a place, 
        # the machine is up and the predecessor has an entity to dispose
        # if the machine has to compete for an Operator that loads the entities onto it
        # check if the predecessor if blocked by an other Machine 
        # if not then the machine has to block the predecessor giverObject to avoid conflicts
        # with other competing machines
        if(len(activeObject.previous)==1):
            if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                    or any(type=='Setup' for type in activeObject.multOperationTypeList))):
                if giverObject.haveToDispose(activeObject):
                    # TODO: 
                    # check whether this entity is the one to be hand in
                    #     to be used in operatorPreemptive
                    activeObject.requestingEntity=giverObject.getActiveObjectQueue()[0]
                    # TODO: 
                    # update the objects requesting the operator
                    activeObject.operatorPool.requestingObject=activeObject.giver
                    # TODOD: 
                    # update the last object calling the operatorPool
                    activeObject.operatorPool.receivingObject=activeObject
                    
                    if activeObject.operatorPool.checkIfResourceIsAvailable()\
                        and activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                        and not giverObject.exitIsAssigned():
                        activeObject.giver.assignExit()
                        return True
                else:
                    return False
            else:
                # the operator performs no load and the entity is received by the machine while there is 
                # no need for operators presence. The operator needs to be present only where the load Type 
                # operation is assigned
                return activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                        and giverObject.haveToDispose(activeObject)
                # TODO: if the set-up performance needs be first performed before the transfer of the entity to 
                # the machine then the presence of an operator to setup the machine before the getEntity()
                # is requested
#                 return (activeObject.operatorPool=='None'\
#                         or activeObject.operatorPool.checkIfResourceIsAvailable())\
#                         and activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
#                         and giverObject.haveToDispose()
        
        # dummy variables that help prioritise the objects requesting to give objects to the Machine (activeObject)
        isRequested=False                                           # is requested is dummyVariable checking if it is requested to accept an item
        maxTimeWaiting=0                                            # dummy variable counting the time a predecessor is blocked
        
        # loop through the possible givers to see which have to dispose and which is the one blocked for longer
        for object in activeObject.previous:
            if(object.haveToDispose(activeObject) and object.receiver==self):# and not object.exitIsAssigned()):
                isRequested=True                                    # if the possible giver has entities to dispose of
                if(object.downTimeInTryingToReleaseCurrentEntity>0):# and the possible giver has been down while trying to give away the Entity
                    timeWaiting=now()-object.timeLastFailureEnded   # the timeWaiting dummy variable counts the time end of the last failure of the giver object
                else:
                    timeWaiting=now()-object.timeLastEntityEnded    # in any other case, it holds the time since the end of the Entity processing
                
                #if more than one possible givers have to dispose take the part from the one that is blocked longer
                if(timeWaiting>=maxTimeWaiting): 
                    activeObject.giver=object                 # set the giver
                    maxTimeWaiting=timeWaiting    
        
        if (activeObject.operatorPool!='None' and (any(type=='Load' for type in activeObject.multOperationTypeList)\
                                                or any(type=='Setup' for type in activeObject.multOperationTypeList))):
            if isRequested:
                # TODO: 
                # check whether this entity is the one to be hand in
                #     to be used in operatorPreemptive
                activeObject.requestingEntity=activeObject.giver.getActiveObjectQueue()[0]
                # TODO: 
                # update the object requesting the operator
                activeObject.operatorPool.requestingObject=activeObject.giver
                # TODOD: 
                # update the last object calling the operatorPool
                activeObject.operatorPool.receivingObject=activeObject
                
                if activeObject.operatorPool.checkIfResourceIsAvailable()\
                    and activeObject.Up and len(activeObjectQueue)<activeObject.capacity\
                    and isRequested and not activeObject.giver.exitIsAssigned():
                    activeObject.giver.assignExit()
                    return True
            else:
                return False
        else:
            # the operator doesn't have to be present for the loading of the machine as the load operation
            # is not assigned to operators
            return activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested
            # while if the set up is performed before the (automatic) loading of the machine then the availability of the
            # operator is requested
#             return (activeObject.operatorPool=='None' or activeObject.operatorPool.checkIfResourceIsAvailable())\
#                 and activeObject.Up and len(activeObjectQueue)<activeObject.capacity and isRequested
    
    # =======================================================================
    # checks if the machine down or it can dispose the object
    # =======================================================================
    def ifCanDisposeOrHaveFailure(self):
        return self.Up==False or self.getReceiverObject().canAccept(self) or len(self.getActiveObjectQueue())==0  
  
    # =======================================================================
    # removes an entity from the Machine
    # =======================================================================
    def removeEntity(self):
        activeObject=self.getActiveObject()  
        #activeObject.outputTrace("releases "+activeObject.objName)  # output to trace that the Entity was released from the currentObject
        activeEntity=CoreObject.removeEntity(self)                               #run the default method     
        activeObject.waitToDispose=False                            # update the waitToDispose flag
        return activeEntity
        
    # ======================================================================= 
    # checks if the Machine can dispose an entity to the following object
    # =======================================================================
    def haveToDispose(self, callerObject=None):
        # get active and the receiver object
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()    
        receiverObject=activeObject.getReceiverObject() 
        #if we have only one successor just check if machine waits to dispose and also is up
        # this is done to achieve better (cpu) processing time        
        if(len(activeObject.next)==1 or callerObject==None): 
            return len(activeObjectQueue)>0 and activeObject.waitToDispose and activeObject.Up
        
#         # if the Machine is empty it returns false right away
#         if(len(activeObjectQueue)==0):
#             return False
   
        thecaller=callerObject
        # give the entity to the successor that is waiting for the most time. 
        # (plant simulation does not do this in every occasion!)       
        maxTimeWaiting=0                                            # dummy variable counting the time a successor is waiting
        for object in activeObject.next:
            if(object.canAccept(activeObject)):                     # if a successor can accept an object
                timeWaiting=now()-object.timeLastEntityLeft         # the time it has been waiting is updated and stored in dummy variable timeWaiting
                if(timeWaiting>maxTimeWaiting or maxTimeWaiting==0):# if the timeWaiting is the maximum among the ones of the successors 
                    maxTimeWaiting=timeWaiting
                    activeObject.receiver=object                    # set the receiver as the longest waiting possible receiver
                                                                    # in the next loops, check the other successors in the previous list
        return len(activeObjectQueue)>0 and activeObject.waitToDispose\
             and activeObject.Up and (thecaller is self.receiver)       

    # =======================================================================
    #                       calculates the setup time
    # =======================================================================
    def calculateSetupTime(self):
        return self.stpRng.generateNumber()
    
    # =======================================================================
    #                        calculates the Load time
    # =======================================================================
    def calculateLoadTime(self):
        return self.loadRng.generateNumber()
    
    # =======================================================================
    #                   prepare the machine to be operated
    # =======================================================================
    def requestOperator(self):
        self.broker.invokeBroker()
        self.toBeOperated = True
    
    # =======================================================================
    #                   prepare the machine to be released
    # =======================================================================
    def releaseOperator(self):
        self.outputTrace(self.currentOperator.objName, "released from "+ self.objName)
        self.broker.invokeBroker()
        self.toBeOperated = False
        
    # =======================================================================
    #       check if the machine is currently operated by an operator
    # =======================================================================
    def isOperated(self):
        return self.toBeOperated
    
    # =======================================================================
    #               check if the machine is already set-up
    # =======================================================================
    def isSetUp(self):
        return self.setUp
    
    # =======================================================================
    #          request that the machine is set-up by an operator
    # =======================================================================
    def requestSetup(self):
        self.setUp=False
    
    # =======================================================================
    # actions to be taken after the simulation ends
    # =======================================================================
    def postProcessing(self, MaxSimtime=None):
        if MaxSimtime==None:
            from Globals import G
            MaxSimtime=G.maxSimTime
        
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        alreadyAdded=False                      # a flag that shows if the blockage time has already been added
        
        # checks all the successors. If no one can accept an Entity then the machine might be blocked
        mightBeBlocked=True
        for nextObject in self.next:
            if nextObject.canAccept():
                mightBeBlocked=False
        
        # if there is an entity that finished processing in a Machine but did not get to reach 
        # the following Object till the end of simulation, 
        # we have to add this blockage to the percentage of blockage in Machine
        # we should exclude the failure time in current entity though!
        # if (len(self.Res.activeQ)>0) and (len(self.next[0].Res.activeQ)>0) and ((self.nameLastEntityEntered == self.nameLastEntityEnded)):
        if (len(activeObjectQueue)>0) and (mightBeBlocked)\
             and ((activeObject.nameLastEntityEntered == activeObject.nameLastEntityEnded)):
            # be careful here, might have to reconsider
            activeObject.totalBlockageTime+=now()-(activeObject.timeLastEntityEnded+activeObject.downTimeInTryingToReleaseCurrentEntity)
            if activeObject.Up==False:
                activeObject.totalBlockageTime-=now()-activeObject.timeLastFailure
                alreadyAdded=True

        #if Machine is currently processing an entity we should count this working time  
        if(len(activeObject.getActiveObjectQueue())>0)\
            and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered))\
            and (not (activeObject.operationType=='Processing' and (activeObject.currentOperator==None))):
            #if Machine is down we should add this last failure time to the time that it has been down in current entity 
            if self.Up==False:
#             if(len(activeObjectQueue)>0) and (self.Up==False):
                activeObject.downTimeProcessingCurrentEntity+=now()-activeObject.timeLastFailure             
            activeObject.totalWorkingTime+=now()-activeObject.timeLastEntityEntered\
                                                -activeObject.downTimeProcessingCurrentEntity\
                                                -activeObject.operatorWaitTimeCurrentEntity\
                                                -activeObject.setupTimeCurrentEntity
            activeObject.totalTimeWaitingForOperator+=activeObject.operatorWaitTimeCurrentEntity
        elif(len(activeObject.getActiveObjectQueue())>0)\
            and (not (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered))\
            and (activeObject.currentOperator==None):
            # TODO: needs further research as the time of failure while waiting for operator is not counted yet
            if self.Up==False:
                activeObject.downTimeProcessingCurrentEntity+=now()-activeObject.timeLastFailure
            activeObject.totalTimeWaitingForOperator+=now()-activeObject.timeWaitForOperatorStarted\
                                                           -activeObject.downTimeProcessingCurrentEntity

        # if Machine is down we have to add this failure time to its total failure time
        # we also need to add the last blocking time to total blockage time     
        if(activeObject.Up==False):
            activeObject.totalFailureTime+=now()-activeObject.timeLastFailure
            # we add the value only if it hasn't already been added
            #if((len(self.next[0].Res.activeQ)>0) and (self.nameLastEntityEnded==self.nameLastEntityEntered) and (not alreadyAdded)):
            if((mightBeBlocked) and (activeObject.nameLastEntityEnded==activeObject.nameLastEntityEntered) and (not alreadyAdded)):        
                activeObject.totalBlockageTime+=(now()-activeObject.timeLastEntityEnded)-(now()-activeObject.timeLastFailure)-activeObject.downTimeInTryingToReleaseCurrentEntity 
        
        #Machine was idle when it was not in any other state    
        activeObject.totalWaitingTime=MaxSimtime-activeObject.totalWorkingTime-activeObject.totalBlockageTime-activeObject.totalFailureTime-activeObject.totalLoadTime-activeObject.totalSetupTime
        
        if activeObject.totalBlockageTime<0 and activeObject.totalBlockageTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalBlockageTime=0  
        
        if activeObject.totalWaitingTime<0 and activeObject.totalWaitingTime>-0.00001:  #to avoid some effects of getting negative cause of rounding precision
            self.totalWaitingTime=0  
        
        activeObject.Failure.append(100*self.totalFailureTime/MaxSimtime)    
        activeObject.Blockage.append(100*self.totalBlockageTime/MaxSimtime)  
        activeObject.Waiting.append(100*self.totalWaitingTime/MaxSimtime)    
        activeObject.Working.append(100*self.totalWorkingTime/MaxSimtime)
        activeObject.WaitingForOperator.append(100*self.totalTimeWaitingForOperator/MaxSimtime)
        activeObject.WaitingForLoadOperator.append(100*self.totalTimeWaitingForLoadOperator/MaxSimtime)
        activeObject.Loading.append(100*self.totalLoadTime/MaxSimtime)
        activeObject.SettingUp.append(100*self.totalSetupTime/MaxSimtime)
     
    # =======================================================================
    # outputs the the "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        from Globals import G
        if MaxSimtime==None:
            MaxSimtime=G.maxSimTime
        
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel    
            G.outputSheet.write(G.outputIndex,0, "The percentage of Failure of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalFailureTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Working of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWorkingTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Blockage of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalBlockageTime/MaxSimtime)
            G.outputIndex+=1 
            G.outputSheet.write(G.outputIndex,0, "The percentage of Waiting of " +self.objName+ " is:")
            G.outputSheet.write(G.outputIndex,1,100*self.totalWaitingTime/MaxSimtime)
            G.outputIndex+=1       
        else:        #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value    
            
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Failure of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Failure):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][1])
            else:     
                G.outputSheet.write(G.outputIndex,1,self.Failure[0])
                G.outputSheet.write(G.outputIndex,2,self.Failure[0])
                G.outputSheet.write(G.outputIndex,3,self.Failure[0])            
            
            G.outputIndex+=1  
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Working of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Working):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Working[0])
                G.outputSheet.write(G.outputIndex,2,self.Working[0])
                G.outputSheet.write(G.outputIndex,3,self.Working[0])                           
            
            G.outputIndex+=1  
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Blockage of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Blockage):
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][1])
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Blockage[0])
                G.outputSheet.write(G.outputIndex,2,self.Blockage[0])
                G.outputSheet.write(G.outputIndex,3,self.Blockage[0])                    
            
            G.outputIndex+=1               
            G.outputSheet.write(G.outputIndex,0, "CI "+str(G.confidenceLevel*100)+"% for the mean percentage of Waiting of "+ self.objName+" is:")
            if self.checkIfArrayHasDifValues(self.Waiting):        
                G.outputSheet.write(G.outputIndex,1,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][0])
                G.outputSheet.write(G.outputIndex,2,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][0])
                G.outputSheet.write(G.outputIndex,3,stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][1])   
            else: 
                G.outputSheet.write(G.outputIndex,1,self.Waiting[0])
                G.outputSheet.write(G.outputIndex,2,self.Waiting[0])
                G.outputSheet.write(G.outputIndex,3,self.Waiting[0])                            
            G.outputIndex+=1    
        G.outputIndex+=1    
    
    # =======================================================================    
    # outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        from Globals import G
        if(G.numberOfReplications==1): #if we had just one replication output the results to excel
            json={}
            json['_class'] = 'Dream.Machine';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['failure_ratio']=100*self.totalFailureTime/G.maxSimTime
            json['results']['working_ratio']=100*self.totalWorkingTime/G.maxSimTime
            json['results']['blockage_ratio']=100*self.totalBlockageTime/G.maxSimTime
            json['results']['waiting_ratio']=100*self.totalWaitingTime/G.maxSimTime
            if any(type=='Setup' for type in self.multOperationTypeList):
                json['results']['setup_ratio']=100*self.totalSetupTime/G.maxSimTime
            if any(type=='Load' for type in self.multOperationTypeList):
                json['results']['load_ratio']=100*self.totalLoadTime/G.maxSimTime
        else: #if we had multiple replications we output confidence intervals to excel
                #for some outputs the results may be the same for each run (eg model is stochastic but failures fixed
                #so failurePortion will be exactly the same in each run). That will give 0 variability and errors.
                #so for each output value we check if there was difference in the runs' results
                #if yes we output the Confidence Intervals. if not we output just the fix value    
            # TODO: update the following with the setup- and load- times       
            json={}
            json['_class'] = 'Dream.Machine';
            json['id'] = str(self.id)
            json['results'] = {}
            json['results']['failure_ratio']={}
            if self.checkIfArrayHasDifValues(self.Failure):
                json['results']['failure_ratio']['min']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][0]
                json['results']['failure_ratio']['avg']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][0]
                json['results']['failure_ratio']['max']=stat.bayes_mvs(self.Failure, G.confidenceLevel)[0][1][1]
            else:
                json['results']['failure_ratio']['min']=self.Failure[0]
                json['results']['failure_ratio']['avg']=self.Failure[0]
                json['results']['failure_ratio']['max']=self.Failure[0] 
            json['results']['working_ratio']={}
            if self.checkIfArrayHasDifValues(self.Working):
                json['results']['working_ratio']['min']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][0]
                json['results']['working_ratio']['avg']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][0]
                json['results']['working_ratio']['max']=stat.bayes_mvs(self.Working, G.confidenceLevel)[0][1][1]
            else:
                json['results']['working_ratio']['min']=self.Working[0]
                json['results']['working_ratio']['avg']=self.Working[0]
                json['results']['working_ratio']['max']=self.Working[0]   
            json['results']['blockage_ratio']={}
            if self.checkIfArrayHasDifValues(self.Blockage):
                json['results']['blockage_ratio']['min']=stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][0]
                json['results']['blockage_ratio']['avg']=stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][0]
                json['results']['blockage_ratio']['max']=stat.bayes_mvs(self.Blockage, G.confidenceLevel)[0][1][1]
            else:
                json['results']['blockage_ratio']['min']=self.Blockage[0]
                json['results']['blockage_ratio']['avg']=self.Blockage[0]
                json['results']['blockage_ratio']['max']=self.Blockage[0]                 
            json['results']['waiting_ratio']={}
            if self.checkIfArrayHasDifValues(self.Waiting):
                json['results']['waiting_ratio']['min']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][0]
                json['results']['waiting_ratio']['avg']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][0]
                json['results']['waiting_ratio']['max']=stat.bayes_mvs(self.Waiting, G.confidenceLevel)[0][1][1]
            else:
                json['results']['waiting_ratio']['min']=self.Waiting[0]
                json['results']['waiting_ratio']['avg']=self.Waiting[0]
                json['results']['waiting_ratio']['max']=self.Waiting[0] 
                
        G.outputJSON['elementList'].append(json)
    