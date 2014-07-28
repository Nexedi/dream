'''
Created on 2 Jul 2014

@author: Anna
'''

from pulp import *


def opAss_LP(stationList, PBlist, PBskills):
    '''
    classdocs
    '''
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
        
    # constraint 2: # machines assigned to an oeprator <= 1
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
def main():
    
    # dict with stations to be operated during a shift (only active stations...ID can be the same for 2 machines as it identifies the type of process
    # WIP can be derived from the buffer upstream the station...when 2 machines operate at a step the WIP will be divided between the two machines
    stations = {}
    stations['M1'] = {'stationID':1, 'WIP':1}
    stations['M2'] = {'stationID':2, 'WIP':1}
#     stations['M3'] = {'stationID':3, 'WIP':1}
#     stations['M4'] = {'stationID':4, 'WIP':1}
#     stations['M5'] = {'stationID':5, 'WIP':1}
#     stations['M6'] = {'stationID':6, 'WIP':1}
    
    # dict with stations' IDs on which an operator can work
    PBskills = {}
    PBskills['PB1'] = [1, 2]#, 3]
    PBskills['PB2'] = [1, 2]#, 3]
#     PBskills['PB3'] = [4, 5]
#     PBskills['PB4'] = [2, 4]
#     PBskills['PB5'] = [1, 2]
#     PBskills['PB6'] = [2, 3, 4]
#     PBskills['PB7'] = [5, 6]
#     PBskills['PB8'] = [5]
#     PBskills['PB9'] = [6]
    
    # list of available PB's 
#     PBlist = ['PB2', 'PB4', 'PB5', 'PB7']
    PBlist = ['PB1', 'PB2']
    
    opAss_LP(stations, PBlist, PBskills)

    
if __name__ == '__main__':
    main()
    
    
        
        