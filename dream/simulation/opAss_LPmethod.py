'''
Created on 2 Jul 2014

@author: Anna
'''

def opAss_LP(stationList, PBlist, PBskills):
    '''
    classdocs
    '''
    from pulp import LpProblem, LpMaximize, LpVariable, LpBinary, lpSum
    machines = stationList.keys()
        
    # define LP problem    
    prob = LpProblem("PBassignment", LpMaximize)
        
    # declare variables...binary assignment variables (operator i to machine j)
    PB_ass = LpVariable.dicts('PB', [(i,j) for i in PBlist 
                                        for j in machines] , 0, 1, LpBinary)
        
    # objective...assignment of PBs to stations with higher WIP...sum of WIP associated with stations where PB is assigned
    obj1 = [stationList[st]['WIP']*PB_ass[(oper,st)] for oper in PBlist for st in machines]
    prob += lpSum(obj1)
        
    # constraint 1: # operators assigned to a station <= 1
    for machine in machines:
        prob += lpSum([PB_ass[(oper,machine)] for oper in PBlist]) <= 1
        
    # constraint 2: # machines assigned to an operator <= 1
    for operator in PBlist:
        prob += lpSum([PB_ass[(operator,machine)] for machine in machines]) <= 1
            
    # constraint 3: assign operator that are capable of running a machine
    skills = {}
    for mach in machines:
        for oper in PBlist:
            if stationList[mach]['stationID'] in PBskills[oper]:
                skills[(mach,oper)] = 1
            else:
                skills[(mach,oper)] = 0
            prob += lpSum([skills[(mach,oper)]-PB_ass[(oper,mach)]]) >= 0
            
    # write the problem data to an .lp file.
    prob.writeLP("PBassignment.lp") 
    
    prob.solve()
    solution={}
    for mach in machines:
        for oper in PBlist:                
            if PB_ass[(oper,mach)].varValue > 0.00001:
                # print 'PB', oper, 'assigned to machine', mach
                solution[str(oper)]=str(mach)
    return solution

    
        
        