'''
Created on 19 Feb 2014

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


from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment
from xml.dom import minidom
from xml.etree import ElementTree as etree

#======================================= The CMSD_Output object ============================================# 
#This object gives as an output the CMSD document of the example topology with the updated calculated values in Operation time and Scrap quantity in the different stations of the production line
def CMSD_example(list1,list2):
    
    #Use of XML.ETREE Python library to create the CMSD document in XML for the CRE production line 
    root = Element('opml')
    root.set('version', '1.0')

    tree=ElementTree(root)
    root.append (Comment('CMSDDocument xmlns=urn:cmsd:mainxmlns:xsi'))

    #Data section of the CMSD document
    DataSection=SubElement(root,'DataSection')
    #Part type definition in XML-based CMSD
    PartType=SubElement(DataSection,'PartType')
    Identifier=SubElement(PartType,'Identifier')
    Identifier.text='Part1'

    PartType=SubElement(DataSection,'PartType')
    Identifier=SubElement(PartType,'Identifier')
    Identifier.text='UnfinishedPart1'

    #Resources definition in XML-based CMSD. It shows the resource identifier, description, resource type and name. 
    #The resource information package contains classes for creating definitions of the characteristics and capabilities of the equipment and employees.
    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource1'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the first of two parallel stations in Section PA'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P1'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource2'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the second of two parallel stations in Section PA'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P4'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource3'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the first of two parallel stations in Section PA'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P2'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource4'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the second of two parallel stations in Section PA'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P5'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource5'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the first of two parallel stations in Section PA'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P3'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource6'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the second of two parallel stations in Section PA'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P6'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource7'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the machine in Section PB'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='machine'
    Name=SubElement(Resource,'Name')
    Name.text='P7'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource8'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the first of two parallel stations in Section PC'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P8'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource9'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the second of two parallel stations in Section PC'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P9'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource10'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the first of two parallel stations in Section PD'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P10'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='resource11'
    Description=SubElement(Resource,'Description')
    Description.text='This resource describes the second of two parallel stations in Section PD'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='station'
    Name=SubElement(Resource,'Name')
    Name.text='P11'


    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='A'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='employee'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='B'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='employee'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='C'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='employee'
    
    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='D'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='employee'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='E'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='employee'

    Resource=SubElement(DataSection,'Resource')
    Identifier=SubElement(Resource,'Identifier')
    Identifier.text='F'
    ResourceType=SubElement(Resource,'ResourceType')
    ResourceType.text='employee'
    
    #Process plan definition in XML-based CMSD. A process plan object contains one or more process objects. 
    #Each process object may represent either an individual process or a process group. The process plan indicates which process executes first.
    ProcessPlan=SubElement(DataSection,'ProcessPlan')

    Identifier=SubElement(ProcessPlan,'Identifier')
    Identifier.text='ProcessPlan:PPPlan1'
    PartsProduced=SubElement(ProcessPlan,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='The part produced the process'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(ProcessPlan,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part consumed the process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'

    FirstProcess=SubElement(ProcessPlan,'FirstProcess')
    ProcessIdentifier=SubElement(FirstProcess,'ProcessIdentifier')
    ProcessIdentifier.text='PFirst'
    
    #A process group indicates that a group of processes either executes in a sequence (sequence group), 
    #only one process in the group executes (decision group), or all processes in the group execute (concurrent group).
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='PFirst'
    SubProcessGroup=SubElement(Process,'SubProcessGroup')
    Type=SubElement(SubProcessGroup,'Type')
    Type.text='sequence'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='PA'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='PB'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='PC'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='PD'

    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='PA'
    SubProcessGroup=SubElement(Process,'SubProcessGroup')
    Type=SubElement(SubProcessGroup,'Type')
    Type.text='decision'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='PA1'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='PA2'

    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='PA1'
    SubProcessGroup=SubElement(Process,'SubProcessGroup')
    Type=SubElement(SubProcessGroup,'Type')
    Type.text='sequence'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P1'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P2'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P3'

    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='PB'
    SubProcessGroup=SubElement(Process,'SubProcessGroup')
    Type=SubElement(SubProcessGroup,'Type')
    Type.text='sequence'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P7'

    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='PC'
    SubProcessGroup=SubElement(Process,'SubProcessGroup')
    Type=SubElement(SubProcessGroup,'Type')
    Type.text='sequence'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P8'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P9'

    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='PD'
    SubProcessGroup=SubElement(Process,'SubProcessGroup')
    Type=SubElement(SubProcessGroup,'Type')
    Type.text='sequence'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P10'
    Process=SubElement(Type,'Process')
    ProcessIdentifier=SubElement(Process,'ProcessIdentifier')
    ProcessIdentifier.text='P11'
    
    #Processes definition in XML-based CMSD. The production planning package contains classes and relationships to create plans for timing of usage of resources 
    #and describing the sequence of steps to manufacture products using the available resources. 
    #It defines information such as orders, resources, and operation time description. Properties like the scrap quantity in our case, used in CMSD information model to define characteristics and capabilities of equipment and employees
    
    #In the following script the eleven stations of the CRE line are defined. In each station there is information about the orders, the required resources, the operation time and the scrap quantity.
    #============================= P1 ==========================================================#
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P1'
    Description=SubElement(Process,'Description')
    Description.text='P1'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='A'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource1'
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P1']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='shape'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P1']['shape'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='rate'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P1']['rate'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P1'])
    
    #================================ P2 ==========================================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P2'
    Description=SubElement(Process,'Description')
    Description.text='P2'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='B'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource3'
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P2']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='shape'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P2']['shape'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='rate'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P2']['rate'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P2'])
    
    #================================ P3 ==========================================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P3'
    Description=SubElement(Process,'Description')
    Description.text='P3'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='C'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource5'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P3']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='mean'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P3']['mean'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='stdev'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P3']['stdev'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P3'])
    
    #================================ P4 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P4'
    Description=SubElement(Process,'Description')
    Description.text='P4'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='A'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource2'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P4']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='mean'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P4']['mean'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='stdev'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P4']['stdev'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P4'])
    
    #================================ P5 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P5'
    Description=SubElement(Process,'Description')
    Description.text='P5'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='B'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource4'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P5']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='shape'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P5']['shape'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='rate'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P5']['rate'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P5'])
    
    #================================ P6 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P6'
    Description=SubElement(Process,'Description')
    Description.text='P6'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='C'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource6'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P6']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='mean'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P6']['mean'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='stdev'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P6']['stdev'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P6'])
    
    #================================ P7 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P7'
    Description=SubElement(Process,'Description')
    Description.text='P7'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='D'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource8'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P7']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='mean'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P7']['mean'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='stdev'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P7']['stdev'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P7'])
    
    #================================ P8 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P8'
    Description=SubElement(Process,'Description')
    Description.text='P8'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='E'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource8'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P8']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='shape'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P8']['shape'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='rate'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P8']['rate'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P8'])
    
    #================================ P9 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P9'
    Description=SubElement(Process,'Description')
    Description.text='P9'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='E'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource9'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P9']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='shape'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P9']['shape'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='rate'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P9']['rate'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P9'])
    
    #================================ P10 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P10'
    Description=SubElement(Process,'Description')
    Description.text='P10'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='F'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource10'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P10']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='mean'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P10']['mean'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='stdev'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P10']['stdev'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P10'])
    
    #================================ P11 =============================================#
    
    Process=SubElement(ProcessPlan,'Process')
    Identifier=SubElement(Process,'Identifier')
    Identifier.text='P11'
    Description=SubElement(Process,'Description')
    Description.text='P11'
    PartsProduced=SubElement(Process,'PartsProduced')
    Description=SubElement(PartsProduced,'Description')
    Description.text='...'
    PartType=SubElement(PartsProduced,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='Part1'
    PartQuantity=SubElement(PartsProduced,'PartQuantity')
    PartQuantity.text='1'
    PartsConsumed=SubElement(Process,'PartsConsumed')
    Description=SubElement(PartsConsumed,'Description')
    Description.text='The part that is an input to this process'
    PartType=SubElement(PartsConsumed,'PartType')
    PartTypeIdentifier=SubElement(PartType,'PartTypeIdentifier')
    PartTypeIdentifier.text='UnfinishedPart1'
    PartQuantity=SubElement(PartsConsumed,'PartQuantity')
    PartQuantity.text='1'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The employee performing the operation'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='F'
    ResourcesRequired=SubElement(Process,'ResourcesRequired')
    Description=SubElement(ResourcesRequired,'Description')
    Description.text='The resource where the operation is being performed'
    Resource=SubElement(ResourcesRequired,'Resource')
    ResourceIdentifier=SubElement(Resource,'ResourceIdentifier')
    ResourceIdentifier.text='resource11'
    
    
    OperationTime=SubElement(Process,'OperationTime')
    Unit=SubElement(OperationTime,'Unit')
    Unit.text='minute'
    Distribution=SubElement(OperationTime,'Distribution')
    Name=SubElement(Distribution,'Name')
    Name.text=str(list1['P11']['distributionType'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='mean'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P11']['mean'])
    DistributionParameter=SubElement(Distribution,'DistributionParameter')
    Name=SubElement(DistributionParameter,'Name')
    Name.text='stdev'
    Value=SubElement(DistributionParameter,'Value')
    Value.text=str(list1['P11']['stdev'])
    
    Property=SubElement(Process,'Property')
    Name=SubElement(Property,'Name')
    Name.text='ScrapQuantity'
    Name=SubElement(Property,'Name')
    Name.text='mean'
    Value=SubElement(Property,'Value')
    Value.text=str(list2['P11'])
    
    #Return a pretty-printed XML string for the Element
    def prettify(elem):
        rough_string = etree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    xmlString=prettify(root)
    #print xmlString
    
    f=open('CMSD.xml','w')  #open an existed xml file in the given directory
    f.write(xmlString)   #Write and save the produced CMSD document in the xml file
    
    return xmlString