'''
Created on 2 Jul 2014

@author: Anna
'''

def opAss_LP(machineList, PBlist, PBskills, previousAssignment={}, weightFactors = [2, 1, 0, 2, 1, 1], Tool={}):
    
    from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum, LpStatus
    import pulp
    import copy
    import glob
    import os 
    import time
    from Globals import G

    startPulp=time.time()

    machines = machineList.keys()
    sumWIP = float(sum([machineList[mach]['WIP'] for mach in machines ]))
        
    # define LP problem    
    prob = LpProblem("PBassignment", LpMaximize)
    obj = []
        
    # declare variables...binary assignment variables (operator i to machine j)
    PB_ass = LpVariable.dicts('PB', [(oper,mach) for oper in PBlist for mach in machines if machineList[mach]['stationID'] in PBskills[oper]] , 0, 1, cat=pulp.LpBinary)
    
    # objective...assignment of PBs to stations with higher WIP...sum of WIP associated with stations where PB is assigned
    if weightFactors[0]>0 and sumWIP>0:
        obj.append([machineList[mach]['WIP']*PB_ass[(oper,mach)]*weightFactors[0]/float(sumWIP) for oper in PBlist for mach in machines if machineList[mach]['stationID'] in PBskills[oper]])
    
    
    # second set of variables (delta assignment between stations) to facilitate the distribution of PBs across different stations
    if weightFactors[1]>0:
        stationGroup = {}
        for mach in machines:
            if machineList[mach]['stationID'] not in stationGroup:
                stationGroup[machineList[mach]['stationID']] = []
            stationGroup[machineList[mach]['stationID']].append(mach)
        Delta_Station = LpVariable.dicts("D_station", [(st1, st2) for i1, st1 in enumerate(stationGroup.keys()) for st2 in stationGroup.keys()[i1 + 1:]])
    
        # calculate global max number of machines within a station that will be used as dividers for Delta_Station  
        maxNoMachines = 0
        for st in stationGroup:
            if len(stationGroup[st]) > maxNoMachines:
                maxNoMachines = len(stationGroup[st])
    
        # calculation of DeltaStation values 
        for i, st1 in enumerate(stationGroup.keys()):
            tempList = []
            for mach1 in stationGroup[st1]:
                for oper1 in PBlist:
                    if st1 in PBskills[oper1]:
                        tempList.append(PB_ass[(oper1,mach1)]/float(maxNoMachines))
        
            for st2 in stationGroup.keys()[i+1:]:
            
                finalList = copy.copy(tempList)
                for mach2 in stationGroup[st2]:                
                    for oper2 in PBlist:
                        if st2 in PBskills[oper2]:
                            finalList.append(PB_ass[(oper2,mach2)]*-1/float(maxNoMachines))  
                
                prob += lpSum(finalList)>= Delta_Station[(st1,st2)]
                prob += lpSum([i*-1 for i in finalList])>= Delta_Station[(st1,st2)]
            
        # integration of second obj
        normalisingFactorDeltaStation = 0
        for i in range(len(stationGroup)):
            normalisingFactorDeltaStation += i
        for i1, st1 in enumerate(stationGroup.keys()):
            for st2 in stationGroup.keys()[i1+1:]:
                obj.append(Delta_Station[(st1,st2)]*weightFactors[1]/float(normalisingFactorDeltaStation) )
        
    # min variation in PB assignment
    if weightFactors[2]>0:
        Delta_Assignment = []
        OldAss = {}
        for pb in previousAssignment:
            if pb in PBlist:
                for station in PBskills[pb]:
                    for mach in machineList:
                        if machineList[mach]['stationID'] == station:
                            Delta_Assignment.append([pb, mach])
                            if previousAssignment[pb] == mach:
                                OldAss[(pb,mach)] = 1
                            else:
                                OldAss[(pb,mach)] = 0
                
    
        # create delta assignment variables
        Delta_Ass = LpVariable.dicts("D_Ass",[(d[0],d[1]) for d in Delta_Assignment])
    
        # integration of third objective
        for d in Delta_Assignment:
            obj.append(Delta_Ass[(d[0], d[1])]*(-1.0*weightFactors[2]/(2*len(previousAssignment))) )

        # calculation of Delta_Ass
        for d in Delta_Assignment:
            if OldAss[(d[0],d[1])] == 1:
                prob += lpSum(OldAss[(d[0],d[1])] - PB_ass[(d[0],d[1])]) <= Delta_Ass[(d[0],d[1])]
            else:
                prob += lpSum(PB_ass[(d[0],d[1])] - OldAss[(d[0],d[1])]) <= Delta_Ass[(d[0],d[1])]  
            
            
    # 4th obj = fill a subline
    if weightFactors[3]>0:
        # verify whether there are machines active in the sublines
        subline={0:{'noMach':0, 'WIP':0}, 1:{'noMach':0, 'WIP':0}}
        for mach in machineList:
            if machineList[mach]['stationID'] in [0,1,2]:
                subline[machineList[mach]['machineID']]['noMach'] += 1
                subline[machineList[mach]['machineID']]['WIP'] += machineList[mach]['WIP']
    
        chosenSubLine = False      
    
        # choose subline to be filled first
        if subline[0]['noMach'] == 3:        
            # case when both sublines are fully active
            if subline[1]['noMach'] == 3:
                if subline[0]['WIP'] >= subline [1]['WIP']:
                    chosenSubLine = 1
                else:
                    chosenSubLine = 2        
            else:
                chosenSubLine = 1
    
        elif subline[1]['noMach'] == 3:
            chosenSubLine = 2
    
        #create variable for the chosen subline
        if chosenSubLine:
            chosenSubLine -= 1
            subLine = LpVariable('SubL', lowBound=0)
            sub = []
            for station in range(3):
                mach = Tool[station][chosenSubLine].name        #'St'+str(station)+'_M'+str(chosenSubLine)
                for oper in PBlist:
                    if station in PBskills[oper]:
                        sub.append(PB_ass[(oper,mach)])
            
            
            prob += lpSum(sub) >= subLine
            chosenSubLine+=1
            obj.append(subLine*weightFactors[3]/3.0)  
            
            
    # 5th objective: prioritise machines with furthest in time last assignment 
    LastAssignmentSum = float(sum([machineList[mach]['lastAssignment'] for mach in machines ]))
    if LastAssignmentSum > 0 and weightFactors[4]>0:
        obj += [machineList[mach]['lastAssignment']*PB_ass[(oper,mach)]*weightFactors[4]/float(LastAssignmentSum) for oper in PBlist for mach in machines if machineList[mach]['stationID'] in PBskills[oper]]
       
    # 6th objective: max the number of pb assigned
    if weightFactors[5]>0:
        obj += [PB_ass[(oper,mach)]*weightFactors[5]/float(len(PBlist)) for oper in PBlist for mach in machines if machineList[mach]['stationID'] in PBskills[oper]]
       
    prob += lpSum(obj)
        
    # constraint 1: # operators assigned to a station <= 1
    for machine in machines:
        prob += lpSum([PB_ass[(oper,machine)] for oper in PBlist if machineList[machine]['stationID'] in PBskills[oper]]) <= 1
        
    # constraint 2: # machines assigned to an operator <= 1
    for operator in PBlist:
        prob += lpSum([PB_ass[(operator,machine)] for machine in machines if machineList[machine]['stationID'] in PBskills[operator]]) <= 1
            
            
    # write the problem data to an .lp file.
    prob.writeLP("PBassignment.lp") 
    
    prob.solve()
    
    if LpStatus[prob.status] != 'Optimal':
        print 'WARNING: LP solution ', LpStatus[prob.status]
    
    PBallocation = {}
    
    for mach in machines:
        for oper in PBlist:
            if machineList[mach]['stationID'] in PBskills[oper]:
                if PB_ass[(oper,mach)].varValue > 0.00001:
                    PBallocation[oper]=mach
            
    files = glob.glob('*.mps')
    for f in files:
        os.remove(f)
        
    files = glob.glob('*.lp')
    for f in files:
        os.remove(f)
    
    G.totalPulpTime+=time.time()-startPulp
    return PBallocation
    
        
        