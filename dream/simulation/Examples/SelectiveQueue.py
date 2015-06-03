from dream.simulation.imports import Queue

#the custom queue
class SelectiveQueue(Queue):
    #override so that it chooses receiver according to priority
    def selectReceiver(self,possibleReceivers=[]):
        #if all the possibleReceivers have the same priority work as cycle
        if len(possibleReceivers):
            if possibleReceivers.count(possibleReceivers[0]) == len(possibleReceivers):
                return Queue.selectReceiver(possibleReceivers)        
        # sort the receivers according to their priority
        possibleReceivers.sort(key=lambda x: x.priority, reverse=True)
        if possibleReceivers[0].canAccept():
            return possibleReceivers[0]
        elif possibleReceivers[1].canAccept():
            return possibleReceivers[1]
        return None
