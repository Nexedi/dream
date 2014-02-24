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

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.rinterface
from rpy2.rinterface import RRuntimeError

MASS= importr('MASS')
#=============================================== Distribution Fitting  ============================================#
#This script consists of two objects for distribution fitting
#Distributions object: for maximum-likelihood fitting of univariate distributions without any information about likelihood analytical expression. 
#DistFittest object: for Kolmogorov-Smirnov distribution fitting test in order to find the best distribution fitting for the given data points

#The Distributions object
class Distributions:
           
    def Normal_distrfit(self,data):
        data=robjects.FloatVector(data)     #The given data sample changes into float vector in order to be handled by RPy2
        rFitDistr=robjects.r['fitdistr']    #Call FitDistr function - R function
        try:                                        #try..except syntax to test if the data sample fits to Normal distribution
            self.Normal= rFitDistr(data,'Normal')   #It fits the normal distribution to the given data sample
        except RRuntimeError:                        
            return None                             #If it doesn't fit Return None
        myDict = {'type':'Normal','mean':self.Normal[0][0],'sd': self.Normal[0][1]}       #Create a dictionary with keys the name of the distribution and its parameters                       
        return myDict                      #If there is no Error return the dictionary with the Normal distribution parameters for the given data sample
        
    def Lognormal_distrfit(self,data):
        data=robjects.FloatVector(data)     #The given data sample changes into float vector in order to be handled by RPy2
        rFitDistr=robjects.r['fitdistr']    #Call FitDistr function - R function
        try:                                #try..except syntax to test if the data sample fits to Lognormal distribution
            self.Lognormal= rFitDistr(data,'Lognormal')     #It fits the Lognormal distribution to the given data sample
        except RRuntimeError: 
            return None                                     #If it doesn't fit Return None
        myDict = {'type':'Lognormal','logmean':self.Lognormal[0][0], 'logsd':self.Lognormal[0][1]}      #Create a dictionary with keys the name of the distribution and its parameters
        return myDict                                                #If there is no Error return the dictionary with the Lognormal distribution parameters for the given data sample

    def NegativeBinomial_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:   
            self.NegBinom= rFitDistr(data,'Negative Binomial')
        except RRuntimeError: 
            return None 
        myDict = {'type':'NegativeBinomial','size':self.NegBinom[0][0],'mu':self.NegBinom[0][1]}
        return myDict   
    
    def Exponential_distrfit(self,data):
        data=robjects.FloatVector(data)    
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Exp= rFitDistr(data,'Exponential')
        except RRuntimeError: 
            return None
        myDict = {'type':'Exponential','rate':self.Exp[0][0]}
        return myDict
    
    def Poisson_distrfit(self,data):
        data=robjects.FloatVector(data)    
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Poisson= rFitDistr(data,'Poisson')
        except RRuntimeError: 
            return None
        myDict = {'type':'Poisson','lambda':self.Poisson[0][0]}
        return myDict
    
    def Logistic_distrfit(self,data): 
        data=robjects.FloatVector(data)   
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Logist= rFitDistr(data,'logistic')
        except RRuntimeError: 
            return None
        myDict = {'type':'Logistic','location':self.Logist[0][0],'scale': self.Logist[0][1]}
        return myDict
   
    def Geometric_distrfit(self,data): 
        data=robjects.FloatVector(data)   
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Geom= rFitDistr(data,'Geometric')
        except RRuntimeError: 
            return None
        myDict = {'type':'Geometric','probability':self.Geom[0][0]}
        return myDict
    
    def Gamma_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Gam=rFitDistr(data,'Gamma') 
        except RRuntimeError: 
            return None
        myDict = {'type':'Gamma','shape':self.Gam[0][0],'rate':self.Gam[0][1]}
        return myDict
        
    def Weibull_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Weib=rFitDistr(data,'weibull')   
        except RRuntimeError:
            return None
        myDict = {'type':'Weibull','shape':self.Weib[0][0], 'scale':self.Weib[0][1]}
        return myDict
        
    def Cauchy_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Cauchy=rFitDistr(data,'Cauchy') 
        except RRuntimeError: 
            return None
        myDict = {'type':'Cauchy','location':self.Cauchy[0][0],'scale':self.Cauchy[0][1]}
        return myDict
        
#The Distribution Fitting test object
class DistFittest:
    
    def Norm_kstest(self,data):             
        data=robjects.FloatVector(data)         #The given data sample changes into float vector in order to be handled by RPy2
        rkstest= robjects.r['ks.test']          #Call ks.test function - R function
        rFitDistr=robjects.r['fitdistr']        #Call FitDistr function - R function
        try:                                        #try..except syntax to test if the data sample fits to Normal distribution    
            self.Normal= rFitDistr(data,'Normal')       #It fits the normal distribution to the given data sample                                                
        except RRuntimeError: 
            return None                             #If it doesn't fit Return None
        norm=self.Normal                        
        self.Normtest= rkstest(data,"pnorm",norm[0][0],norm[0][1])      #It conducts the Kolmogorov-Smirnov test for Normal distribution to the given data sample
        return self.Normtest                    #If there is no error returns the outcome of the Kolmogorov-Smirnov test (p-value,D) 
        
    def Lognorm_kstest(self,data):              #The given data sample changes into float vector in order to be handled by RPy2
        data=robjects.FloatVector(data)         #Call ks.test function - R function
        rkstest= robjects.r['ks.test']          #Call FitDistr function - R function
        rFitDistr=robjects.r['fitdistr']        #It fits the Lognormal distribution to the given data sample
        try:                                     #try..except syntax to test if the data sample fits to Lognormal distribution
            self.Lognormal= rFitDistr(data,'Lognormal')
        except RRuntimeError: 
            return None                         #If it doesn't fit Return None
        lognorm=self.Lognormal
        self.Lognormtest= rkstest(data,"plnorm",lognorm[0][0],lognorm[0][1])        #It conducts the Kolmogorov-Smirnov test for Lognormal distribution to the given data sample
        return self.Lognormtest                 #If there is no error returns the outcome of the Kolmogorov-Smirnov test (p-value,D) 
    
    def NegBinom_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.NegBinom= rFitDistr(data,'Negative Binomial')
        except RRuntimeError: 
            return None
        negbinom=self.NegBinom
        self.NegBinomtest= rkstest(data,"pnbinom",negbinom[0][0],negbinom[1][1])
        return self.NegBinomtest
    
    def Exp_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Exp= rFitDistr(data,'Exponential')
        except RRuntimeError: 
            return None
        exp=self.Exp
        self.Exptest= rkstest(data,"pexp",exp[0][0])
        return self.Exptest
        
    def Pois_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Poisson= rFitDistr(data,'Poisson')
        except RRuntimeError: 
            return None
        pois=self.Poisson
        self.Poistest= rkstest(data,"ppois",pois[0])
        return self.Poistest
   
    def Geom_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Geom= rFitDistr(data,'Geometric')
        except RRuntimeError: 
            return None
        geom=self.Geom
        self.Geomtest= rkstest(data,"pgeom",geom[0])
        return self.Geomtest
        
    def Logis_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Logist= rFitDistr(data,'logistic')
        except RRuntimeError: 
            return None
        logis=self.Logist
        self.Logistest= rkstest(data,"plogis",logis[0][0],logis[0][1])
        return self.Logistest
       
    def Gam_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Gam=rFitDistr(data,'Gamma')
        except RRuntimeError: 
            return None
        gam=self.Gam
        self.Gamtest= rkstest(data,"pgamma",scale=gam[0][1],shape=gam[0][0])
        return self.Gamtest

    def Weib_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Weib=rFitDistr(data,'weibull')
        except RRuntimeError: 
            return None
        weib=self.Weib
        self.Weibtest= rkstest(data,"pweibull",scale=weib[0][1],shape=weib[0][0])
        return self.Weibtest
        
    def Cauchy_kstest(self,data):
        data=robjects.FloatVector(data)
        rkstest= robjects.r['ks.test']
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Cauchy=rFitDistr(data,'Cauchy') 
        except RRuntimeError: 
            return None
        cauch=self.Cauchy
        self.Cauchytest= rkstest(data,"pcauchy",cauch[0][0],cauch[0][1])
        return self.Cauchytest
        
    def ks_test(self,data):             #Method that conducts the Kolmogorov-Smirnov statistical test and returns the best fitting distribution among the list of the available statistical distributions
        data=robjects.FloatVector(data)     #The given data sample changes into float vector in order to be handled by RPy2
        
        self.Norm_kstest(data)
        self.Lognorm_kstest(data)
        self.Exp_kstest(data)
        self.Pois_kstest(data)
        self.Geom_kstest(data)
        self.Logis_kstest(data)
        self.Geom_kstest(data)
        self.Weib_kstest(data)
        self.Cauchy_kstest(data)
        
        #Create a list with strings the available statistical distributions
        list1=('Normal','Lognormal','Exponential','Poisson', 'Geometric','Logistic','Gamma','Weibull', 'Cauchy')
        list2=[]                                    #Create a list 
        
        #try...except syntaxes to test if the Kolmogorov-Smirnov statistical tests can be conducted to the available distributions  
        try:
            list2.append(self.Normtest[0][0])        #It appends in list2 the D statistic parameter of the Kolmogorov-Smirnov test in Normal distribution
        except:
            list2.append('')                         #in case of an error, it appends a blank point 
        try:    
            list2.append(self.Lognormtest[0][0])    #It appends in list2 the D statistic parameter of the Kolmogorov-Smirnov test in Lognormal distribution
        except:
            list2.append('')                        # #in case of an error, it appends a blank point
        try:   
            list2.append(self.Exptest[0][0])         #It appends in list2 the D statistic parameter of the Kolmogorov-Smirnov test in Exponential distribution
        except:
            list2.append('')                          #in case of an error, it appends a blank point
        try:
            list2.append(self.Poistest[0][0])
        except:
            list2.append('')
        try:
            list2.append(self.Geomtest[0][0])
        except:         
            list2.append('')
        try:
            list2.append(self.Logistest[0][0])
        except:
            list2.append('')   
        try:    
            list2.append(self.Gamtest[0][0])
        except:
            list2.append('')
        try:   
            list2.append(self.Weibtest[0][0])
        except:
            list2.append('')   
        try:   
            list2.append(self.Cauchytest[0][0])
        except:
            list2.append('')               
        
        #Create a list with parameters the above D parameters calculated by the Kolmogorov-Smirnov tests in the available statistical distributions
        a=min(list2)     #Create a variable that holds the minimum value from the above list  
        b=list2.index(a) #Create a variable that holds the actual position  of the minimum value in the list
        
        self=Distributions()
        #Set of if...elif syntax in order to get a Python dictionary with the best fitting statistical distribution and its parameters
        if list1[b]=='Normal':          #Check if in list's b position is the Normal distribution
            self.Normal_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'mean','bParameter':'standarddeviation','aParameterValue':self.Normal[0][0],'bParameterValue': self.Normal[0][1]} #Create a dictionary with distribution's and distribution parameters' names and distribution parameters' values
            return myDict     
        elif list1[b]=='Lognormal':
            self.Lognormal_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'logmean','bParameter':'logsd','aParameterValue':self.Lognormal[0][0],'bParameterValue': self.Lognormal[0][1]}
            return myDict
        elif list1[b]=='Exponential':
            self.Exponential_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'rate', 'aParameterValue':self.Exp[0][0]}
            return myDict
        elif list1[b]=='Poisson':
            self.Poisson_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'lambda','aParameterValue':self.Poisson[0][0]}
            return myDict
        elif list1[b]=='Geometric':
            self.Geometric_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'probability','aParameterValue':self.Geom[0][0]}
            return myDict
        elif list1[b]=='Logistic':
            self.Logistic_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'location','bParameter':'scale','aParameterValue':self.Logist[0][0],'bParameterValue':self.Logist[0][1]}
            return myDict
        elif list1[b]=='Gamma':
            self.Gamma_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'shape','bParameter':'rate','aParameterValue':self.Gam[0][0],'bParameterValue':self.Gam[0][1]}
            return myDict
        elif list1[b]=='Weibull':
            self.Weibull_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'shape','bParameter':'scale','aParameterValue':self.Weib[0][0],'bParameterValue':self.Weib[0][1]}
            return myDict
        else:
            self.Cauchy_distrfit(data)
            myDict = {'type':list1[b],'aParameter':'location','bParameter':'scale','aParameterValue':self.Cauchy[0][0],'bParameterValue':self.Cauchy[0][1]}
            return myDict
         
 
         
 
 
 
         
         
