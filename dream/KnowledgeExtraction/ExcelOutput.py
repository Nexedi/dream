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
from StatisticalMeasures import BasicStatisticalMeasures
from DistributionFitting import DistFittest

#=========================================== The ExcelOutput object =============================================================#
#The ExcelOutput object export in Excel document both the calculated statistical measures and the distribution fitting test of a dataset 
class Output(BasicStatisticalMeasures,DistFittest):
    
    def PrintStatisticalMeasures(self,data,fileName="StatisticalMeasuresResults.xls"):
        data=robjects.FloatVector(data)     #The given list changes into float vector in order to be handled by RPy2
        
        book = Workbook()                   
        sheet1 = book.add_sheet('StatisticalMeasures', cell_overwrite_ok=True)  #Add one sheet in the excel document with the name StatisticalMeasures
        
        ###Give names to cells###
        sheet1.write(0,0,('Dataset statistical measures'))
        sheet1.write(3,0,('Length'))
        
        sheet1.write(4,0,('Summary'))
        sheet1.write(4,1,('Min'))
        sheet1.write(4,2,('1st Qu.'))
        sheet1.write(4,3,('Median'))
        sheet1.write(4,4,('Mean'))
        sheet1.write(4,5,('3rd Qu.'))
        sheet1.write(4,6,('Max'))
        
        sheet1.write(7,0,('Data points'))
        
        sheet1.write(10,0,('Quantile'))
        sheet1.write(10,1,('0%'))
        sheet1.write(10,2,('25%'))
        sheet1.write(10,3,('50%'))
        sheet1.write(10,4,('75%'))
        sheet1.write(10,5,('100%'))
        
        sheet1.write(12,0,('Mean'))
        sheet1.write(13,0,('Variance'))
        sheet1.write(14,0,('Standard deviation'))
        sheet1.write(16,0,('Range'))
        sheet1.write(17,0,('Interquartile Range'))
        
        ###Length###
        sheet1.write(3,1,(self.length(data)))
        
        ###Summary###
        sheet1.write(5,1,(self.summary(data)[0]))
        sheet1.write(5,2,(self.summary(data)[1]))
        sheet1.write(5,3,(self.summary(data)[2])) 
        sheet1.write(5,4,(self.summary(data)[3]))
        sheet1.write(5,5,(self.summary(data)[4]))
        sheet1.write(5,6,(self.summary(data)[5]))
               
        ###Dataset###
        i=0
        while (i<self.length(data)):
            sheet1.write(7,i+1,((data[i])))
            i=i+1
               
        ###Quantselfles###
        sheet1.write(11,1,(self.quantile(data)[0]))
        sheet1.write(11,2,(self.quantile(data)[1]))
        sheet1.write(11,3,(self.quantile(data)[2]))
        sheet1.write(11,4,(self.quantile(data)[3]))
        sheet1.write(11,5,(self.quantile(data)[4]))
        
        ###Mean###
        sheet1.write(12,1,(self.mean(data)))
        
        ###Varselfance####
        sheet1.write(13,1,(self.var(data)))
        
        ###Standard devselfatselfon###
        sheet1.write(14,1,(self.sd(data)))
        
        ###Range###
        sheet1.write(16,1,(self.range(data)[0]))
        sheet1.write(16,2,(self.range(data)[1]))
        
        ###selfnterquartselfle Range###
        sheet1.write(17,1,(self.IQR(data)))
        book.save(fileName)  #Save the excel document 
        
    
    
    def PrintDistributionFit(self,data,fileName="DistributionFittingResults.xls"):
        data=robjects.FloatVector(data)
        
        book = Workbook()
        sheet2 = book.add_sheet('Distribution Fitting', cell_overwrite_ok=True)
        
        ###Give names to cells###
        sheet2.write(0,0,('DistributionFit'))
        sheet2.write(1,0,('data points'))
        
        
        sheet2.write(3,1,('Discrete distributions'))
        sheet2.write(3,8,('Kolmogorov-Smirnov test'))
        sheet2.write(12,14,('Best distribution fitting'))
        
        sheet2.write(8,1,('Poisson'))
        sheet2.write(8,2,('lambda'))
        sheet2.write(8,6,('D-statistic'))
        sheet2.write(8,8,('p-value'))
        
        sheet2.write(11,1,('Geometric'))
        sheet2.write(11,2,('probability'))
        sheet2.write(11,6,('D-statistic'))
        sheet2.write(11,8,('p-value'))
        
        sheet2.write(15,1,('Continuous distributions'))
        
        sheet2.write(17,1,('Normal'))
        sheet2.write(17,2,('mean'))
        sheet2.write(17,3,('standard deviation'))
        sheet2.write(17,6,('D-statistic'))
        sheet2.write(17,8,('p-value'))
        
        sheet2.write(21,1,('Exponential'))
        sheet2.write(21,2,('rate'))
        sheet2.write(21,6,('D-statistic'))
        sheet2.write(21,8,('p-value'))
        
        sheet2.write(25,1,('Gamma'))
        sheet2.write(25,2,('shape'))
        sheet2.write(25,3,('rate'))
        sheet2.write(25,6,('D-statistic'))
        sheet2.write(25,8,('p-value'))
        
        sheet2.write(29,1,('Lognormal'))
        sheet2.write(29,2,('log mean'))
        sheet2.write(29,3,('log standard deviation'))
        sheet2.write(29,6,('D-statistic'))
        sheet2.write(29,8,('p-value'))
        
        sheet2.write(33,1,('Weibull'))
        sheet2.write(33,2,('shape'))
        sheet2.write(33,3,('scale'))
        sheet2.write(33,6,('D-statistic'))
        sheet2.write(33,8,('p-value'))
        
        sheet2.write(37,1,('Logistic'))
        sheet2.write(37,2,('location'))
        sheet2.write(37,3,('scale'))
        sheet2.write(37,6,('D-statistic'))
        sheet2.write(37,8,('p-value'))
        
        sheet2.write(41,1,('Cauchy'))
        sheet2.write(41,2,('location'))
        sheet2.write(41,3,('scale'))
        sheet2.write(41,6,('D-statistic'))
        sheet2.write(41,8,('p-value'))
        
        ###Dataset###
        i=0
        while (i<robjects.r['length'](data)[0]):
            sheet2.write(1,i+1,((data[i])))
            i=i+1

        ###Poisson###
        sheet2.write(9,2,(robjects.r['fitdistr'](data,'Poisson')[0][0]))
        sheet2.write(9,6,(self.Pois_kstest(data)[0][0]))
        sheet2.write(9,8,(self.Pois_kstest(data)[1][0]))
        
        ###Geometric###
        sheet2.write(12,2,(robjects.r['fitdistr'](data,'Geometric')[0][0]))
        sheet2.write(12,6,(self.Geom_kstest(data)[0][0]))
        sheet2.write(12,8,(self.Geom_kstest(data)[1][0]))
        
        ###Normal###
        sheet2.write(18,2,(robjects.r['fitdistr'](data,'Normal')[0][0]))
        sheet2.write(18,3,(robjects.r['fitdistr'](data,'Normal')[0][1]))
        sheet2.write(18,6,(self.Norm_kstest(data)[0][0]))
        sheet2.write(18,8,(self.Norm_kstest(data)[1][0]))
        
        ###Exponential###
        sheet2.write(22,2,(robjects.r['fitdistr'](data,'Exponential')[0][0]))
        sheet2.write(22,6,(self.Exp_kstest(data)[0][0]))
        sheet2.write(22,8,(self.Exp_kstest(data)[1][0]))
        
        ###Gamma###
        sheet2.write(26,2,(robjects.r['fitdistr'](data,'Gamma')[0][0]))
        sheet2.write(26,3,(robjects.r['fitdistr'](data,'Gamma')[0][1]))
        sheet2.write(26,6,(self.Gam_kstest(data)[0][0]))
        sheet2.write(26,8,(self.Gam_kstest(data)[1][0]))
        
        ###Lognormal###
        sheet2.write(30,2,(robjects.r['fitdistr'](data,'Lognormal')[0][0]))
        sheet2.write(30,3,(robjects.r['fitdistr'](data,'Lognormal')[0][1]))
        sheet2.write(30,6,(self.Lognorm_kstest(data)[0][0]))
        sheet2.write(30,8,(self.Lognorm_kstest(data)[1][0]))
        
        ###Weibull###
        sheet2.write(34,2,(robjects.r['fitdistr'](data,'Weibull')[0][0]))
        sheet2.write(34,3,(robjects.r['fitdistr'](data,'Weibull')[0][1]))
        sheet2.write(34,6,(self.Weib_kstest(data)[0][0]))
        sheet2.write(34,8,(self.Weib_kstest(data)[1][0]))
        
        ###Logistic###
        sheet2.write(38,2,(robjects.r['fitdistr'](data,'Logistic')[0][0]))
        sheet2.write(38,3,(robjects.r['fitdistr'](data,'Logistic')[0][1]))
        sheet2.write(38,6,(self.Logis_kstest(data)[0][0]))
        sheet2.write(38,8,(self.Logis_kstest(data)[1][0]))
        
        ###Cauchy###
        sheet2.write(42,2,(robjects.r['fitdistr'](data,'Cauchy')[0][0]))
        sheet2.write(42,3,(robjects.r['fitdistr'](data,'Cauchy')[0][1]))
        sheet2.write(42,6,(self.Cauchy_kstest(data)[0][0]))
        sheet2.write(42,8,(self.Cauchy_kstest(data)[1][0]))
        
        ###BestDistributionFit###
        A=self.ks_test(data)
        sheet2.write(14,14,(A.get('type')))
        sheet2.write(14,15,(A.get('aParameter')))
        sheet2.write(14,16,(A.get('bParameter')))
        sheet2.write(15,15,(A.get('aParameterValue')))
        sheet2.write(15,16,(A.get('bParameterValue')))
        
        book.save(fileName)    #Save the excel document 
