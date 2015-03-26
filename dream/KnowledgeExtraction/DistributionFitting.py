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
class Distributions(object):
           
    def Normal_distrfit(self,data):
        data=robjects.FloatVector(data)     #The given data sample changes into float vector in order to be handled by RPy2
        rFitDistr=robjects.r['fitdistr']    #Call FitDistr function - R function
        try:                                        #try..except syntax to test if the data sample fits to Normal distribution
            self.Normal= rFitDistr(data,'Normal')   #It fits the normal distribution to the given data sample
        except RRuntimeError:                        
            raise
            return None                             #If it doesn't fit Return None
        myDict = {'distributionType':'Normal','mean':self.Normal[0][0],'stdev': self.Normal[0][1],'min':0, 'max':(self.Normal[0][0]+3*self.Normal[0][1])}      #Create a dictionary with keys distribution's and distribution's parameters  names and the parameters' values                      
        return myDict                      #If there is no Error return the dictionary with the Normal distribution parameters for the given data sample
        
    def Lognormal_distrfit(self,data):
        data=robjects.FloatVector(data)     #The given data sample changes into float vector in order to be handled by RPy2
        rFitDistr=robjects.r['fitdistr']    #Call FitDistr function - R function
        try:                                #try..except syntax to test if the data sample fits to Lognormal distribution
            self.Lognormal= rFitDistr(data,'Lognormal')     #It fits the Lognormal distribution to the given data sample
        except RRuntimeError: 
            return None                                     #If it doesn't fit Return None
        myDict ={'distributionType':'Lognormal','logmean':self.Lognormal[0][0],'logsd': self.Lognormal[0][1]}      #Create a dictionary with keys distribution's and distribution's parameters  names and the parameters' values                      
        return myDict                                                #If there is no Error return the dictionary with the Lognormal distribution parameters for the given data sample

    def NegativeBinomial_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:   
            self.NegBinom= rFitDistr(data,'Negative Binomial')
        except RRuntimeError: 
            return None 
        myDict = {'distributionType':'NegativeBinomial','size':self.NegBinom[0][0],'mu':self.NegBinom[0][1]}
        return myDict   
    
    def Exponential_distrfit(self,data):
        data=robjects.FloatVector(data)    
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Exp= rFitDistr(data,'Exponential')
        except RRuntimeError: 
            return None
        myDict = {'distributionType':'Exp', 'mean':self.Exp[0][0]}
        return myDict
    
    def Poisson_distrfit(self,data):
        data=robjects.FloatVector(data)    
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Poisson= rFitDistr(data,'Poisson')
        except RRuntimeError: 
            return None
        myDict = {'distributionType':'Poisson', 'lambda':self.Poisson[0][0]}
        return myDict
    
    def Logistic_distrfit(self,data): 
        data=robjects.FloatVector(data)   
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Logist= rFitDistr(data,'logistic')
        except RRuntimeError: 
            return None
        myDict = {'distributionType':'Logistic', 'location':self.Logist[0][0],'scale':self.Logist[0][1]}
        return myDict
   
    def Geometric_distrfit(self,data): 
        data=robjects.FloatVector(data)   
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Geom= rFitDistr(data,'Geometric')
        except RRuntimeError: 
            return None
        myDict = {'distributionType':'Geometric','probability':self.Geom[0][0]}
        return myDict
    
    def Gamma_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Gam=rFitDistr(data,'Gamma') 
        except RRuntimeError: 
            return None
        myDict = {'distributionType':'Gamma','shape':self.Gam[0][0],'rate':self.Gam[0][1]}
        return myDict
        
    def Weibull_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:
            self.Weib=rFitDistr(data,'weibull')   
        except RRuntimeError:
            return None
        myDict = {'distributionType':'Weibull','shape':self.Weib[0][0],'scale':self.Weib[0][1]}
        return myDict
        
    def Cauchy_distrfit(self,data):
        data=robjects.FloatVector(data)
        rFitDistr=robjects.r['fitdistr']
        try:    
            self.Cauchy=rFitDistr(data,'Cauchy') 
        except RRuntimeError: 
            return None
        myDict = {'distributionType':'Cauchy','location':self.Cauchy[0][0],'scale':self.Cauchy[0][1]}
        return myDict
        
#The Distribution Fitting test object
class DistFittest(object):
    
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
        self.Gamtest= rkstest(data,"pgamma",rate=gam[0][1],shape=gam[0][0])
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
        #Create a list with strings the available statistical distributions
        list1=['Normal','Lognormal','Exp','Poisson', 'Geometric','Logistic','Gamma','Weibull', 'Cauchy']
        list2=[]                  #Create a list 
        #if...else syntaxes to test if the Kolmogorov-Smirnov statistical tests can be conducted to the available distributions 
        
        norm_test = self.Norm_kstest(data)
        if norm_test is not None:
            list2.insert(0,norm_test[0][0])
        else:
            list2.insert(0,'')
           
        lognorm_test = self.Lognorm_kstest(data)
        if lognorm_test is not None:
            list2.insert(1,lognorm_test[0][0])
        else:
            list2.insert(1,'')
           
        exp_test = self.Exp_kstest(data)
        if exp_test is not None:
            list2.insert(2,exp_test[0][0])
        else:
            list2.insert(2,'')
           
        pois_test = self.Pois_kstest(data)
        if pois_test is not None:
            list2.insert(3,pois_test[0][0])
        else:
            list2.insert(3,'')
           
        geom_test = self.Geom_kstest(data)
        if geom_test is not None:
            list2.insert(4,geom_test[0][0])
        else:
            list2.insert(4,'')
           
        logis_test = self.Logis_kstest(data)
        if logis_test is not None:
            list2.insert(5,logis_test[0][0])
        else:
            list2.insert(5,'')
           
        gam_test = self.Gam_kstest(data)
        if gam_test is not None:
            list2.insert(6,gam_test[0][0])
        else:
            list2.insert(6,'')
           
        weib_test = self.Weib_kstest(data)
        if weib_test is not None:
            list2.insert(7,weib_test[0][0])
        else:
            list2.insert(7,'')
           
        cauchy_test = self.Cauchy_kstest(data)
        if cauchy_test is not None:
            list2.insert(8,cauchy_test[0][0])
        else:
            list2.insert(8,'')
                     
        #Create a list with parameters the above D parameters calculated by the Kolmogorov-Smirnov tests in the available statistical distributions
        a=min(list2)     #Create a variable that holds the minimum value from the above list  
        b=list2.index(a) #Create a variable that holds the actual position  of the minimum value in the list
        
        self=Distributions()
        #Set of if...elif syntax in order to get a Python dictionary with the best fitting statistical distribution and its parameters
        if list1[b]=='Normal':          #Check if in list's b position is the Normal distribution
            self.Normal_distrfit(data)
            myDict = {'distributionType':list1[b],'mean':self.Normal[0][0],'stdev': self.Normal[0][1],'min':0, 'max':(self.Normal[0][0]+3*self.Normal[0][1])} #Create a dictionary with distribution's and distribution parameters' names and distribution parameters' values
            return myDict     
        elif list1[b]=='Lognormal':
            self.Lognormal_distrfit(data)
            myDict = {'distributionType':list1[b],'logmean':self.Lognormal[0][0],'logsd': self.Lognormal[0][1]}
            return myDict
        elif list1[b]=='Exp':
            self.Exponential_distrfit(data)
            myDict = {'distributionType':list1[b],'mean':self.Exp[0][0]}
            return myDict
        elif list1[b]=='Poisson':
            self.Poisson_distrfit(data)
            myDict = {'distributionType':list1[b],'lambda':self.Poisson[0][0]}
            return myDict
        elif list1[b]=='Geometric':
            self.Geometric_distrfit(data)
            myDict = {'distributionType':list1[b],'probability':self.Geom[0][0]}
            return myDict
        elif list1[b]=='Logistic':
            self.Logistic_distrfit(data)
            myDict = {'distributionType':list1[b],'location':self.Logist[0][0],'scale':self.Logist[0][1]}
            return myDict
        elif list1[b]=='Gamma':
            self.Gamma_distrfit(data)
            myDict = {'distributionType':list1[b],'shape':self.Gam[0][0],'rate':self.Gam[0][1]}
            return myDict
        elif list1[b]=='Weibull':
            self.Weibull_distrfit(data)
            myDict = {'distributionType':list1[b],'shape':self.Weib[0][0],'scale':self.Weib[0][1]}
            return myDict
        else:
            self.Cauchy_distrfit(data)
            myDict = {'distributionType':list1[b],'location':self.Cauchy[0][0],'scale':self.Cauchy[0][1]}
            return myDict
         
 
         
 
 
 
         
         
