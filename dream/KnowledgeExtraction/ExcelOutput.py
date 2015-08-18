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
Created on 19 Feb 2014

@author: Panos
'''
from xlwt import Workbook
import rpy2.robjects as robjects
from StatisticalMeasures import StatisticalMeasures
from DistributionFitting import DistFittest

#=========================================== The ExcelOutput object =============================================================#
#The ExcelOutput object export in Excel document both the calculated statistical measures and the distribution fitting test of a dataset 
class ExcelOutput(StatisticalMeasures,DistFittest):
    
    def PrintStatisticalMeasures(self,data,fileName="StatisticalMeasuresResults.xls"):
        data=robjects.FloatVector(data)     #The given list changes into float vector in order to be handled by RPy2
        
        book = Workbook()                   
        sheet1 = book.add_sheet('StatisticalMeasures', cell_overwrite_ok=True)  #Add one sheet in the excel document with the name StatisticalMeasures
        
        ###Give names to cells###
        sheet1.write(0,0,('Dataset statistical measures'))
        sheet1.write(3,1,('Length'))
        
        sheet1.write(4,1,('Summary'))
        sheet1.write(4,2,('Min'))
        sheet1.write(4,3,('1st Qu.'))
        sheet1.write(4,4,('Median'))
        sheet1.write(4,5,('Mean'))
        sheet1.write(4,6,('3rd Qu.'))
        sheet1.write(4,7,('Max'))
        
        sheet1.write(1,0,('Data points'))
        
        sheet1.write(10,1,('Quantile'))
        sheet1.write(10,2,('0%'))
        sheet1.write(10,3,('25%'))
        sheet1.write(10,4,('50%'))
        sheet1.write(10,5,('75%'))
        sheet1.write(10,6,('100%'))
        
        sheet1.write(12,1,('Mean'))
        sheet1.write(13,1,('Variance'))
        sheet1.write(14,1,('Standard deviation'))
        sheet1.write(16,1,('Range'))
        sheet1.write(17,1,('Interquartile Range'))
        
        ###Length###
        sheet1.write(3,2,(self.length(data)))
        
        ###Summary###
        sheet1.write(5,2,(self.summary(data)[0]))
        sheet1.write(5,3,(self.summary(data)[1]))
        sheet1.write(5,4,(self.summary(data)[2])) 
        sheet1.write(5,5,(self.summary(data)[3]))
        sheet1.write(5,6,(self.summary(data)[4]))
        sheet1.write(5,7,(self.summary(data)[5]))
               
        ###Dataset###
        i=0
        while (i<self.length(data)):
            sheet1.write(i+2,0,((data[i])))
            i=i+1
               
        ###Quantselfles###
        sheet1.write(11,2,(self.quantile(data)[0]))
        sheet1.write(11,3,(self.quantile(data)[1]))
        sheet1.write(11,4,(self.quantile(data)[2]))
        sheet1.write(11,5,(self.quantile(data)[3]))
        sheet1.write(11,6,(self.quantile(data)[4]))
        
        ###Mean###
        sheet1.write(12,2,(self.mean(data)))
        
        ###Varselfance####
        sheet1.write(13,2,(self.var(data)))
        
        ###Standard devselfatselfon###
        sheet1.write(14,2,(self.sd(data)))
        
        ###Range###
        sheet1.write(16,2,(self.range(data)[0]))
        sheet1.write(16,3,(self.range(data)[1]))
        
        ###selfnterquartselfle Range###
        sheet1.write(17,2,(self.IQR(data)))
        book.save(fileName)  #Save the excel document 
        
    
    
    def PrintDistributionFit(self,data,fileName="DistributionFittingResults.xls"):
        data=robjects.FloatVector(data)
        
        book = Workbook()
        sheet2 = book.add_sheet('Distribution Fitting', cell_overwrite_ok=True)
        
        ###Give names to cells###
        sheet2.write(0,0,('Distribution Fitting'))
        sheet2.write(1,0,('data points'))
        
        
        sheet2.write(3,1,('Discrete distributions'))
        sheet2.write(2,4,('Kolmogorov-Smirnov test'))
        sheet2.write(12,11,('Best fitted distribution'))
        
        sheet2.write(4,1,('Poisson'))
        sheet2.write(4,2,('lambda'))
        sheet2.write(4,6,('D-statistic'))
        sheet2.write(4,8,('p-value'))
        
        sheet2.write(7,1,('Geometric'))
        sheet2.write(7,2,('probability'))
        sheet2.write(7,6,('D-statistic'))
        sheet2.write(7,8,('p-value'))
        
        sheet2.write(10,1,('Continuous distributions'))
        
        sheet2.write(11,1,('Normal'))
        sheet2.write(11,2,('mean'))
        sheet2.write(11,3,('standard deviation'))
        sheet2.write(11,6,('D-statistic'))
        sheet2.write(11,8,('p-value'))
        
        sheet2.write(14,1,('Exponential'))
        sheet2.write(14,2,('rate'))
        sheet2.write(14,6,('D-statistic'))
        sheet2.write(14,8,('p-value'))
        
        sheet2.write(17,1,('Gamma'))
        sheet2.write(17,2,('shape'))
        sheet2.write(17,3,('rate'))
        sheet2.write(17,6,('D-statistic'))
        sheet2.write(17,8,('p-value'))
        
        sheet2.write(20,1,('Lognormal'))
        sheet2.write(20,2,('log mean'))
        sheet2.write(20,3,('log standard deviation'))
        sheet2.write(20,6,('D-statistic'))
        sheet2.write(20,8,('p-value'))
        
        sheet2.write(23,1,('Weibull'))
        sheet2.write(23,2,('shape'))
        sheet2.write(23,3,('scale'))
        sheet2.write(23,6,('D-statistic'))
        sheet2.write(23,8,('p-value'))
        
        sheet2.write(26,1,('Logistic'))
        sheet2.write(26,2,('location'))
        sheet2.write(26,3,('scale'))
        sheet2.write(26,6,('D-statistic'))
        sheet2.write(26,8,('p-value'))
        
        sheet2.write(29,1,('Cauchy'))
        sheet2.write(29,2,('location'))
        sheet2.write(29,3,('scale'))
        sheet2.write(29,6,('D-statistic'))
        sheet2.write(29,8,('p-value'))
        
        ###Dataset###
        i=0
        while (i<robjects.r['length'](data)[0]):
            sheet2.write(i+2,0,((data[i])))
            i=i+1

        ###Poisson###
        sheet2.write(5,2,(robjects.r['fitdistr'](data,'Poisson')[0][0]))
        sheet2.write(5,6,(self.Pois_kstest(data)[0][0]))
        sheet2.write(5,8,(self.Pois_kstest(data)[1][0]))
        
        ###Geometric###
        sheet2.write(8,2,(robjects.r['fitdistr'](data,'Geometric')[0][0]))
        sheet2.write(8,6,(self.Geom_kstest(data)[0][0]))
        sheet2.write(8,8,(self.Geom_kstest(data)[1][0]))
        
        ###Normal###
        sheet2.write(12,2,(robjects.r['fitdistr'](data,'Normal')[0][0]))
        sheet2.write(12,3,(robjects.r['fitdistr'](data,'Normal')[0][1]))
        sheet2.write(12,6,(self.Norm_kstest(data)[0][0]))
        sheet2.write(12,8,(self.Norm_kstest(data)[1][0]))
        
        ###Exponential###
        sheet2.write(15,2,(robjects.r['fitdistr'](data,'Exponential')[0][0]))
        sheet2.write(15,6,(self.Exp_kstest(data)[0][0]))
        sheet2.write(15,8,(self.Exp_kstest(data)[1][0]))
        
        ###Gamma###
        sheet2.write(18,2,(robjects.r['fitdistr'](data,'Gamma')[0][0]))
        sheet2.write(18,3,(robjects.r['fitdistr'](data,'Gamma')[0][1]))
        sheet2.write(18,6,(self.Gam_kstest(data)[0][0]))
        sheet2.write(18,8,(self.Gam_kstest(data)[1][0]))
        
        ###Lognormal###
        sheet2.write(21,2,(robjects.r['fitdistr'](data,'Lognormal')[0][0]))
        sheet2.write(21,3,(robjects.r['fitdistr'](data,'Lognormal')[0][1]))
        sheet2.write(21,6,(self.Lognorm_kstest(data)[0][0]))
        sheet2.write(21,8,(self.Lognorm_kstest(data)[1][0]))
        
        ###Weibull###
        sheet2.write(24,2,(robjects.r['fitdistr'](data,'Weibull')[0][0]))
        sheet2.write(24,3,(robjects.r['fitdistr'](data,'Weibull')[0][1]))
        sheet2.write(24,6,(self.Weib_kstest(data)[0][0]))
        sheet2.write(24,8,(self.Weib_kstest(data)[1][0]))
        
        ###Logistic###
        sheet2.write(27,2,(robjects.r['fitdistr'](data,'Logistic')[0][0]))
        sheet2.write(27,3,(robjects.r['fitdistr'](data,'Logistic')[0][1]))
        sheet2.write(27,6,(self.Logis_kstest(data)[0][0]))
        sheet2.write(27,8,(self.Logis_kstest(data)[1][0]))
        
        ###Cauchy###
        sheet2.write(30,2,(robjects.r['fitdistr'](data,'Cauchy')[0][0]))
        sheet2.write(30,3,(robjects.r['fitdistr'](data,'Cauchy')[0][1]))
        sheet2.write(30,6,(self.Cauchy_kstest(data)[0][0]))
        sheet2.write(30,8,(self.Cauchy_kstest(data)[1][0]))
        
        ###BestDistributionFit###
        A=self.ks_test(data)
        sheet2.write(13,10,(A.get('distributionType')))
        if A['distributionType']=='Normal':
            del A['min']
            del A['max']
            del A['distributionType']
            sheet2.write(13,11,(A.keys()[0]))
            sheet2.write(13,12,(A.keys()[1]))
            sheet2.write(14,11,(A.values()[0]))
            sheet2.write(14,12,(A.values()[1]))
        elif A['distributionType']=='Exp' or A['distributionType']=='Poisson' or A['distributionType']=='Geometric':
            del A['distributionType']
            sheet2.write(13,11,(A.keys()[0]))
            sheet2.write(14,11,(A.values()[0]))
             
        else:
            del A['distributionType']
            sheet2.write(13,11,(A.keys()[0]))
            sheet2.write(13,12,(A.keys()[1]))
            sheet2.write(14,11,(A.values()[0]))
            sheet2.write(14,12,(A.values()[1]))
        
        book.save(fileName)    #Save the excel document 
