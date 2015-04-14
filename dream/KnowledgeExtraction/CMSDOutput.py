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
Created on 25 Mar 2015

@author: Panos
'''
#=========================================== The CMSDOutput object =============================================================#
#The CMSDOutput object exports the data prepared by the KE tool to a format that follows the CMSD specification. It uses predefined tags in the CMSD standard. 
class CMSDOutput(object):
    def Distributions(self,data):
        Parameters=[]
        ParameterValue=[]
        if data['distributionType']=='Normal':
            del data['min']
            del data['max']
        for index in list(data.keys()):
            if index is not 'distributionType':
                Parameters.append(index)
                ParameterValue.append(data[index])
        return Parameters, ParameterValue
        
    def ProcessingTimes(self,tree,stationId,distDict):
        root=tree.getroot()
        process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
        for process in process:
            process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
            if process_identifier==stationId:                                      #It checks using if...elif syntax the value of the process identifier 
                OperationTime=process.get('OpeationTime')                       #It gets the element attribute OpearationTime inside the Process node
                Distribution=process.get('./OperationTime/Distribution')        #It gets the element attribute Distribution inside the OpearationTime node
                Name=process.find('./OperationTime/Distribution/Name')          #It finds the subelement Name inside the Distribution attribute
                Name.text=distDict['distributionType']                                     #It changes the text between the Name element tags, putting the name of the distribution (e.g. in Normal distribution that will be Normal) 
                names,values=self.Distributions(distDict)
                DistributionParameterA=process.get('./OperationTime/Distribution/DistributionParameterA')
                Name=process.find('./OperationTime/Distribution/DistributionParameterA/Name')
                Name.text=str(names[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
                Value=process.find('./OperationTime/Distribution/DistributionParameterA/Value')
                Value.text=str(values[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
                DistributionParameterB=process.get('./OperationTime/Distribution/DistributionParameterB')
                Name=process.find('./OperationTime/Distribution/DistributionParameterB/Name')
                try:
                    Name.text=str(names[1])                                #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
                    Value=process.find('./OperationTime/Distribution/DistributionParameterB/Value')
                    Value.text=str(values[1])                           #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
                except IndexError:
                    continue
        return tree
    
    def TTF(self,tree,stationId,distDict):
        root=tree.getroot()
        process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
        for process in process:
            process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
            if process_identifier==stationId:                                      #It checks using if...elif syntax the value of the process identifier 
                TTF=process.find('./Property1/Name')
                if TTF.text=='MeanTimeToFailure':
                    Distribution=process.get('./Property1/Distribution')
                    Name=process.find('./Property1/Distribution/Name')         
                    Name.text=distDict['distributionType']
                    names,values=self.Distributions(distDict)
                    DistributionParameterA=process.get('./Property1/Distribution/DistributionParameterA')
                    Name=process.find('./Property1/Distribution/DistributionParameterA/Name')
                    Name.text=str(names[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
                    Value=process.find('./Property1/Distribution/DistributionParameterA/Value')
                    Value.text=str(values[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
                    DistributionParameterB=process.get('./Property1/Distribution/DistributionParameterB')
                    Name=process.find('./Property1/Distribution/DistributionParameterB/Name')
                    try:
                        Name.text=str(names[1])                                #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
                        Value=process.find('./Property1/Distribution/DistributionParameterB/Value')
                        Value.text=str(values[1])                           #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
                    except IndexError:
                        continue
        return tree
    
    def TTR(self,tree,stationId,distDict):
        root=tree.getroot()
        process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
        for process in process:
            process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
            if process_identifier==stationId:                                      #It checks using if...elif syntax the value of the process identifier 
                property=tree.findall('./DataSection/ProcessPlan/Process/Property2/Name')
                for property in property:
                    if property.text=='MeanTimeToRepair':
                        Distribution=process.get('./Property2/Distribution')
                        Name=process.find('./Property2/Distribution/Name')         
                        Name.text=distDict['distributionType']
                        names,values=self.Distributions(distDict)
                        DistributionParameterA=process.get('./Property2/Distribution/DistributionParameterA')
                        Name=process.find('./Property2/Distribution/DistributionParameterA/Name')
                        Name.text=str(names[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
                        Value=process.find('./Property2/Distribution/DistributionParameterA/Value')
                        Value.text=str(values[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
                        DistributionParameterB=process.get('./Property2/Distribution/DistributionParameterB')
                        Name=process.find('./Property2/Distribution/DistributionParameterB/Name')
                        try:
                            Name.text=str(names[1])                                #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
                            Value=process.find('./Property2/Distribution/DistributionParameterB/Value')
                            Value.text=str(values[1])                           #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
                        except IndexError:
                            continue
        return tree
    
    def InterarrivalTime(self,tree,stationId,distDict):
        root=tree.getroot()
        process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
        for process in process:
            process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
            if process_identifier==stationId:                                      #It checks using if...elif syntax the value of the process identifier 
                interarrivalTime=process.find('./Property/Name')
                if interarrivalTime.text=='interarrivalTime':                                   
                    Distribution=process.get('./Property/Distribution')
                    Name=process.find('./Property/Distribution/Name')         
                    Name.text=distDict['distributionType']
                    names,values=self.Distributions(distDict)
                    DistributionParameterA=process.get('./Property/Distribution/DistributionParameterA')
                    Name=process.find('./Property/Distribution/DistributionParameterA/Name')
                    Name.text=str(names[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
                    Value=process.find('./Property/Distribution/DistributionParameterA/Value')
                    Value.text=str(values[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
                    DistributionParameterB=process.get('./Property/Distribution/DistributionParameterB')
                    Name=process.find('./Property/Distribution/DistributionParameterB/Name')
                    try:
                        Name.text=str(names[1])                                #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
                        Value=process.find('./Property/Distribution/DistributionParameterB/Value')
                        Value.text=str(values[1])                           #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
                    except IndexError:
                        continue
        return tree
    
    def ScrapQuantity(self,tree,stationId,distDict):
        root=tree.getroot()
        process=tree.findall('./DataSection/ProcessPlan/Process')               #It creates a new variable and using the 'findall' order in XML.ETREE library, this new variable holds all the processes defined in the XML file
        for process in process:
            process_identifier=process.find('Identifier').text                  #It creates a new variable that holds the text of the Identifier element in the XML file
            if process_identifier==stationId:                                      #It checks using if...elif syntax the value of the process identifier 
                scrapQuantity=process.find('./Property/Name')
                if scrapQuantity.text=='ScrapQuantity':                                   
                    Distribution=process.get('./Property/Distribution')
                    Name=process.find('./Property/Distribution/Name')         
                    Name.text=distDict['distributionType']
                    names,values=self.Distributions(distDict)
                    DistributionParameterA=process.get('./Property/Distribution/DistributionParameterA')
                    Name=process.find('./Property/Distribution/DistributionParameterA/Name')
                    Name.text=str(names[0])                               #It changes the text between the Name element tags, putting the name of the distribution's first parameter (e.g. in Normal that will be the mean)
                    Value=process.find('./Property/Distribution/DistributionParameterA/Value')
                    Value.text=str(values[0])                          #It changes the text between the Value element tags, putting the value of the distribution's first parameter (e.g. in Normal so for mean value that will be 5.0)
                    DistributionParameterB=process.get('./Property/Distribution/DistributionParameterB')
                    Name=process.find('./Property/Distribution/DistributionParameterB/Name')
                    try:
                        Name.text=str(names[1])                                #It changes the text between the Name element tags, putting the name of the distribution's second parameter (e.g. in Normal that will be the standarddeviation)
                        Value=process.find('./Property/Distribution/DistributionParameterB/Value')
                        Value.text=str(values[1])                           #It changes the text between the Value element tags, putting the value of the distribution's second parameter (e.g. in Normal so for standarddeviation value that will be 1.3)
                    except IndexError:
                        continue
        return tree
                    
    
    
    
    