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
from dream.KnowledgeExtraction.Plots import Graphs

filename = ("DataSet.csv")
A=Import_CSV()   #call the Import_CSV module and using its method Input_data import the data set from the CSV file to the tool
Data = A.Input_data(filename)

M1 = Data.get('M1',[])       #get from the returned Python dictionary the two data sets:
M2 = Data.get('M2',[])

graph=Graphs()  #create a graph object

#create the following charts
graph.Plots(M1, 'M1SimplePlot.jpg')
graph.ScatterPlot(M1, M2, 'Scatterplot.jpg')           
graph.Barplot(M2, 'M2Barplot.jpg')   
graph.Histogram(M1, 'M1Histogram.jpg')
graph.TwoSetPlot(M1, M2, 'M1M2Plot.jpg')
graph.Pie(M2, 'M2PieChar.jpg')

