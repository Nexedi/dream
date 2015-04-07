'''
Created on 13 Jun 2014

@author: Panos
'''
#===========================================================================
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

from dream.KnowledgeExtraction.ImportCSVdata import Import_CSV
from dream.KnowledgeExtraction.ConfidenceIntervals import Intervals
from dream.KnowledgeExtraction.DataManipulation import DataManagement

def main(test=0, CSVFileName='DataSet.csv',
                 csvFile=None):
    if csvFile:
        CSVFileName = csvFile.name
        
    filename = CSVFileName
    data=Import_CSV()   #call the Import_CSV module and using its method Input_data import the data set from the CSV file to the tool
    Data = data.Input_data(filename)
    
    ProcTime = Data.get('ProcessingTimes',[])       #get from the returned Python dictionary the three data sets
    MTTF = Data.get('MTTF',[])
    MTTR = Data.get('MTTR',[])
    
    CI=Intervals()  #create a Intervals object
    DM=DataManagement()
    if test:
        return DM.round(CI.ConfidIntervals(ProcTime, 0.95)), CI.ConfidIntervals(MTTR, 0.95), DM.ceiling(CI.ConfidIntervals(MTTF, 0.90))
    #print the confidence intervals of the data sets applying either 90% or 95% probability
    print DM.round(CI.ConfidIntervals(ProcTime, 0.95))
    print DM.ceiling(CI.ConfidIntervals(MTTF, 0.90))
    print CI.ConfidIntervals(MTTR, 0.95)
    
if __name__ == '__main__':
    main()