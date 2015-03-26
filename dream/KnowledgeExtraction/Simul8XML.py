'''
Created on 27 Nov 2014

@author: Panos
'''
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

#=============================================== Simul8XML  ============================================#
# This script consists of one object and several methods, the use of these methods allow the integration of the KE tool and Simul8 simulation software.
# By using this script the KE tool integrates with Simul8 accessing the XML of one model and modifying several info based on the available data
from xml.etree import ElementTree as et
# The Distributions object
class Simul8Output(object):
    
    def Simul8Dist(self,dist):     #Using this method the statistical distributions from the DistributionFitting objects translated to meaningful info for the Simul8 package
        self.sim8Dist=[]
        if dist['distributionType'] == 'Normal':
            self.sim8Dist.insert(0,'3')
            self.sim8Dist.insert(1,dist['mean'])
            self.sim8Dist.insert(2,dist['stdev'])
        elif dist['distributionType'] == 'Exp':
            self.sim8Dist.insert(0,'7')
            self.sim8Dist.insert(1,dist['mean'])
        elif dist['distributionType'] == 'Lognormal':
            self.sim8Dist.insert(0,'9')
            self.sim8Dist.insert(1,dist['logmean'])
            self.sim8Dist.insert(2,dist['logsd'],)
        elif dist['distributionType'] == 'Weibull':
            self.sim8Dist.insert(0,'10')
            self.sim8Dist.insert(1,dist['shape'])
            self.sim8Dist.insert(2,dist['scale'])
        elif dist['distributionType'] == 'Gamma':
            self.sim8Dist.insert(0,'11')
            self.sim8Dist.insert(1,dist['shape'])
            rate= 1.0 / dist['scale']
            self.sim8Dist.insert(2,rate)
        elif dist['distributionType'] == 'Poisson':
            self.sim8Dist.insert(0,'17')
            self.sim8Dist.insert(1,dist['lambda'])
        elif dist['distributionType'] == 'NegativeBinomial':
            self.sim8Dist.insert(0,'18')
            self.sim8Dist.insert(1,dist['size'])
            self.sim8Dist.insert(2,dist['mu'])
        elif dist['distributionType'] == 'Geometric':
            self.sim8Dist.insert(0,'20')
            self.sim8Dist.insert(1,dist['probability'])
        return self.sim8Dist
        
    def Title(self, tree, title):          # Calling this method, the user can modify the title of the simulation model, as arguments are given the tree, which is the XML file after parsing, and the proposed title 
        root=tree.getroot()
        for objects in root.findall('./SimulationParameters'):
            Title = objects.find('./Trial/Title')
            Title.text = str(title)
        return tree                        # The output is the tree with the inserted title
    
    def Runs(self, tree, runs):       # Similar to Title method, choosing the Runs method the user is able to define the number of the runs in the Simul8 model
        root=tree.getroot()
        for objects in root.findall('./SimulationParameters'):
            Runs = objects.find('./Trial/Runs')
            Runs.text = str(runs)
        return tree
    
    def ResultsPeriod(self, tree, collectPreiod):      # Calling this method, the user can modify the ResultsCollectionPeriod of the simulation model, as arguments are given the tree, which is the XML file after parsing, and the simulation time 
        root=tree.getroot()
        for objects in root.findall('./SimulationParameters'):
            ResultsCollectionPeriod = objects.find('./ResultsCollectionPeriod')
            ResultsCollectionPeriod.text = str(collectPreiod)
        return tree
    
    def WarmupTime(self, tree, warmupTime):  # Another method similar to the above to modify the warm up period by modifying the Warmuptime
        root=tree.getroot()
        for objects in root.findall('./SimulationParameters'):
            WarmupTime= objects.find('./Warmuptime')
            WarmupTime.text = str(warmupTime)
        return tree
    
    def InterArrivalTime(self, tree, name, dist):   # A method to define the Interarrival times of the start point item or source, the Simul8Dist method called in this method 
        root=tree.getroot()
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Entry Point' and objects.attrib['Name'] == name:
                procDist = objects.find('./InterArrivalTimeSampleData/DistribType')
                procPar1 = objects.find('./InterArrivalTimeSampleData/DistParam1')
                procPar2 = objects.find('./InterArrivalTimeSampleData/DistParam2')
                simParam= self.Simul8Dist(dist)
                procDist.text = str(simParam[0])
                procPar1.text = str(simParam[1])
                try: 
                    procPar2.text = str(simParam[2])
                except:
                    continue
        return tree    
    
    def ProcTimes(self, tree, name, dist):      # Another method to modify the processing times of the Activities or stations, using this method the user exports the outcome of the KE tool distribution fitting into the simul8 XML
        root=tree.getroot()
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Center' and objects.attrib['Name'] == name:
                procDist = objects.find('./OperationTimeSampleData/DistribType')
                procPar1 = objects.find('./OperationTimeSampleData/DistParam1')
                procPar2 = objects.find('./OperationTimeSampleData/DistParam2')
                simParam= self.Simul8Dist(dist)
                procDist.text = str(simParam[0])
                procPar1.text = str(simParam[1])
                try: 
                    procPar2.text = str(simParam[2])
                except:
                    continue
        return tree
    
    def MTBF(self, tree, name, dist):  # A method to modify the MTBF (Mean Time Between Failure) of an Activity, again this method uses the Simul8Dist method
        root=tree.getroot()
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Center' and objects.attrib['Name'] == name:
                procDist = objects.find('./BreakDowns/MTBFSampleData/DistribType')
                procPar1 = objects.find('./BreakDowns/MTBFSampleData/DistParam1')
                procPar2 = objects.find('./BreakDowns/MTBFSampleData/DistParam2')
                simParam= self.Simul8Dist(dist)
                procDist.text = str(simParam[0])
                procPar1.text = str(simParam[1])
                try: 
                    procPar2.text = str(simParam[2])
                except:
                    continue
        return tree
        
    def MTTR(self, tree, name, dist):   # Similar to the MTBF method, the MTTR (Mean Time To Repair) to export the results from the KE tool distribution fitting process
        root= tree.getroot()  
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Work Center' and objects.attrib['Name'] == name:
                procDist = objects.find('./BreakDowns/MTTRSampleData/DistribType')
                procPar1 = objects.find('./BreakDowns/MTTRSampleData/DistParam1')
                procPar2 = objects.find('./BreakDowns/MTTRSampleData/DistParam2')
                simParam= self.Simul8Dist(dist)
                procDist.text = str(simParam[0])
                procPar1.text = str(simParam[1])
                try: 
                    procPar2.text = str(simParam[2])
                except:
                    continue
        return tree 
    
    def QueueCap(self, tree, name, cap):      #By calling this method the user is able to modify the capacity of Queues in the simulation object, as arguments the user should give the tree and the number of the capacity 
        root= tree.getroot()  
        for objects in root.findall('./SimulationObjects/SimulationObject'):
            if objects.attrib['Type'] == 'Storage Area' and objects.attrib['Name'] == name:
                capacity = objects.find('./MaxConts')
                capacity.text = str(cap)
        return tree
        
            
            
            
        
        