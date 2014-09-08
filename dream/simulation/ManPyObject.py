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
Created on 08 Sep 2014

@author: George
'''
'''
Class that acts as an abstract. It should have no instances. All ManPy objects inherit from it
Also only abstract ManPy classes inherit directly (CoreObject, Entity, ObjectResource, ObjectInterruption)
'''

# ===========================================================================
# the ManPy object
# ===========================================================================
class ManPyObject(object):
    
    def __init__(self, id, name,**kw):
        self.id=id
        self.name=name 
        
        
    #===========================================================================
    #  method used to request allocation from the Router
    #===========================================================================
    @staticmethod
    def requestAllocation():
        # TODO: signal the Router, skilled operators must be assigned to operatorPools
        from Globals import G
        G.Router.allocation=True
        G.Router.waitEndProcess=False
        if not G.Router.invoked:
            G.Router.invoked=True
            G.Router.isCalled.succeed(G.env.now)
            
    #===========================================================================
    #  signalRouter method
    #===========================================================================
    @staticmethod
    def signalRouter(receiver=None):
        # if an operator is not assigned to the receiver then do not signal the receiver but the Router
        try:
            # XXX in the case of dedicatedOperator assignedOperators must be always True in order to avoid invoking the Router
            if not receiver.assignedOperator or\
                   (receiver.isPreemptive and len(receiver.Res.users)>0):
                if receiver.isLoadRequested():
                    try:
                        from Globals import G
                        if not G.Router.invoked:
#                             self.printTrace(self.id, signal='router')
                            G.Router.invoked=True
                            G.Router.isCalled.succeed(G.env.now)
                        return True
                    except:
                        return False
            else:
                return False
        except:
            return False
        
    #===========================================================================
    # check if the any of the operators are skilled (having a list of skills regarding the objects)
    #===========================================================================
    @staticmethod
    def checkForDedicatedOperators():
        from Globals import G
        # XXX this can also be global
        # flag used to inform if the operators assigned to the station are skilled (skillsList)
        return any(operator.skillsList for operator in G.OperatorsList)
    
    @staticmethod
    def printTrace(entity='', **kw):
        assert len(kw)==1, 'only one phrase per printTrace supported for the moment'
        from Globals import G
        import Globals
        time=G.env.now
        charLimit=60
        remainingChar=charLimit-len(entity)-len(str(time))
        if(G.console=='Yes'):
            print time,entity,
            for key in kw:
                if key not in Globals.getSupportedPrintKwrds():
                    raise ValueError("Unsupported phrase %s for %s" % (key, entity))
                element=Globals.getPhrase()[key]
                phrase=element['phrase']
                prefix=element.get('prefix',None)
                suffix=element.get('suffix',None)
                arg=kw[key]
                if prefix:
                    print prefix*remainingChar,phrase,arg
                elif suffix:
                    remainingChar-=len(phrase)+len(arg)
                    suffix*=remainingChar
                    if key=='enter':
                        suffix=suffix+'>'
                    print phrase,arg,suffix
                else:
                    print phrase,arg
                    
    # =======================================================================
    # outputs message to the trace.xls 
    # outputs message to the trace.xls. Format is (Simulation Time | Entity or Frame Name | message)
    # =======================================================================
    @staticmethod
    def outputTrace(entityName, message):
        from Globals import G
        if(G.trace=="Yes"):         #output only if the user has selected to
            #handle the 3 columns
            G.traceSheet.write(G.traceIndex,0,str(G.env.now))
            G.traceSheet.write(G.traceIndex,1,entityName)
            G.traceSheet.write(G.traceIndex,2,message)          
            G.traceIndex+=1       #increment the row
            #if we reach row 65536 we need to create a new sheet (excel limitation)  
            if(G.traceIndex==65536):
                G.traceIndex=0
                G.sheetIndex+=1
                G.traceSheet=G.traceFile.add_sheet('sheet '+str(G.sheetIndex), cell_overwrite_ok=True)

    #===========================================================================
    # actions to be performed after the end of the simulation
    #===========================================================================
    def postProcessing(self):
        pass
    
    # =======================================================================
    #                        outputs data to "output.xls"
    # =======================================================================
    def outputResultsXL(self, MaxSimtime=None):
        pass
    
    # =======================================================================
    #                       outputs results to JSON File
    # =======================================================================
    def outputResultsJSON(self):
        pass