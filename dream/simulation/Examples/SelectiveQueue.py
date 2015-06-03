from dream.simulation.imports import Queue

#the custom queue
class SelectiveQueue(Queue):
    #override so that it chooses receiver according to priority
    def selectReceiver(self,possibleReceivers=[]):
        #if all the possibleReceivers have the same priority work as cycle
        priorityList=[]
        for element in possibleReceivers:
            priorityList.append(element.priority)
        if len(priorityList):
            if priorityList.count(priorityList[0]) == len(priorityList):
                return Queue.selectReceiver(possibleReceivers)        
        # else sort the receivers according to their priority
        possibleReceivers.sort(key=lambda x: x.priority, reverse=True)
        if possibleReceivers[0].canAccept():
            return possibleReceivers[0]
        elif possibleReceivers[1].canAccept():
            return possibleReceivers[1]
        return None
