'''
Created on 14 Aug 2015

@author: Anna
'''

from operator import itemgetter
from .Globals import G

def findSequence(Projects, seqPrjDone, idDone):
    
    opReady = []
    
    print('find sequence', Projects)
    print('find sequence', seqPrjDone)
    
    for proj in list(seqPrjDone.keys()):
        
        for part in list(seqPrjDone[proj].keys()):
            
            if seqPrjDone[proj][part] < len(Projects[proj][part]):
                
                possibleOp = True
                
                print('part', part, Projects[proj][part][seqPrjDone[proj][part]]['id'])
                
                if seqPrjDone[proj][part]==0 or Projects[proj][part][seqPrjDone[proj][part]-1]['id'] not in list(G.Schedule.keys()):
                    minStartTime = max(G.xlreftime, G.OrderDates[proj])
                else:
                    minStartTime = G.Schedule[Projects[proj][part][seqPrjDone[proj][part]-1]['id']]['endDate']
                
                # verify whether the operation can be performed in terms of prerequisite operations
                for preReq in Projects[proj][part][seqPrjDone[proj][part]]['preReq']:
                    
                    if preReq not in idDone:
                        possibleOp = False
                        break 
                    
                    else:
                        if minStartTime < G.Schedule[preReq]['endDate']:
                            minStartTime = G.Schedule[preReq]['endDate']
                
                if possibleOp:
                    newOp = Projects[proj][part][seqPrjDone[proj][part]]
                    print(newOp['id'], 'possible')                
                    newOp['minStartTime'] = minStartTime
                    newOp['project'] = proj
                    newOp['part'] = part
                    if newOp['personnel'].lower() != 'automatic':
                        newOp['manualTime'] = newOp['pt'] * newOp['qty']
                    seqPrjDone[proj][part] += 1
#                    newOp['manualTime']
                    
                    # if it is a setup operation add the following operation
                    if 'SET' in newOp['operation']:
                        
                        assert(seqPrjDone[proj][part] < len(Projects[proj][part]))
                        
                        followOp =  Projects[proj][part][seqPrjDone[proj][part]]
                        seqPrjDone[proj][part] += 1
                        
                        # verify that the operation is the same
                        print(followOp['operation'], newOp['operation'])
                        assert (followOp['operation'].split('-')[0] in newOp['operation'])
                        
                        # update operation (erase set)
                        newOp['operation'] = followOp['operation']
                        
                        # update automatic time
                        newOp['autoTime'] = followOp['pt'] * followOp['qty']
                        
                        # update opID, add followOp id
                        newOp['preID'] = newOp['id']
                        newOp['id'] = followOp['id']                       
                        
                        
                    else:
                        newOp['autoTime'] = 0
                        newOp['preID'] = None
                    
                    if newOp['operation'] in ['INJM', 'MILL', 'EDM', 'TURN', 'DRILL']:
                        newOp['mode'] = 'MA'
                        
                    elif newOp['operation'] == 'INJM-MAN':
                        newOp['mode'] = 'MM'
                        newOp['operation'] = 'INJM'         
                    
                    else:
                        newOp['mode'] = 'M'
                    
                    opReady.append(newOp)
        
        print('pre', opReady)
        opReady = sorted(opReady, key=itemgetter('sequence', 'manualTime', 'autoTime'))
        
        print('seq', seqPrjDone, G.seqPrjDone)
        return opReady
                        
    
if __name__ == '__main__':
    
    from . import jsonReader as jR
    
    seq = jR.seqPrjDone
    seq['Order 1']['Order 1 - Mould'] = 2
    seq['Order 1']['Order 1 - Part 01'] = 3
    seq['Order 1']['Order 1 - Part 02'] = 3
    seq['Order 1']['Order 1 - Part 03'] = 1
    
    op = findSequence(jR.Projects, jR.seqPrjDone, ['ID-00001','ID-00002','ID-00003','ID-00004','ID-00005', 'ID-00006', 'ID-00007', 'ID-00008', 'ID-00009'])
    print('op', op)
    