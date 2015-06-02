from dream.simulation.imports import Queue

#the custom queue
class SelectiveQueue(Queue):
    #override so that it chooses receiver according to priority
    def selectReceiver(self,possibleReceivers=[]):
        # sort the receivers according to their priority
        possibleReceivers.sort(key=lambda x: x.priority, reverse=True)
        if possibleReceivers[0].canAccept():
            return possibleReceivers[0]
        elif possibleReceivers[1].canAccept():
            return possibleReceivers[1]
        return None
