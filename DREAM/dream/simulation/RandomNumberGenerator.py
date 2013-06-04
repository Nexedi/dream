'''
Created on 14 Feb 2013

@author: George
'''

'''
holds methods for generations of numbers from different distributions
'''
class RandomNumberGenerator(object):
    def __init__(self, obj, type):
        self.distType=type
        self.avg=0
        self.stdev=0
        self.min=0
        self.max=0
        #self.availability=0
        self.alpha=0
        self.beta=0
        self.object=obj
                
    def generateNumber(self):
        from Globals import G
        number=0
        if(self.distType=="Fixed"):     #if the distribution is Fixed 
            number=self.avg
        elif(self.distType=="Exp"):     #if the distribution is Exponential      
            number=G.Rnd.expovariate(1.0/(self.avg))
        elif(self.distType=="Normal"):      #if the distribution is Normal 
            while 1:
                number=G.Rnd.normalvariate(self.avg, self.stdev)
                if number>self.max or number<self.min and max!=0:  #if the number is out of bounds repeat the process                                                                      #if max=0 this means that we did not have time "time" bounds             
                    continue
                else:           #if the number is in the limits stop the process
                    break           
        elif self.distType=="Erlang":    #if the distribution is erlang          
            number=G.Rnd.gammavariate(self.alpha,self.beta)                      
        else:
            print "unknown distribution error in "+str(self.object.type)+str(self.object.id)                   
        return number
    
        