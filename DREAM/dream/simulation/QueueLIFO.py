'''
Created on 15 Feb 2013

@author: George
'''

'''
Models a LIFO queue where entities can wait in order to get into a server
'''


from Queue import Queue

class QueueLIFO(Queue):
        
    #gets an entity from the predecessor     
    def getEntity(self):
        self.Res.activeQ=[self.previous[0].Res.activeQ[0]]+self.Res.activeQ   #get the entity from the previous object
                                                                              #and put it in front of the activeQ       
        self.previous[0].removeEntity()     #remove the entity from the previous object        