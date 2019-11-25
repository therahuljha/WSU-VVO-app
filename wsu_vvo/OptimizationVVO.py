import json
import networkx as nx 
import numpy as np
from pulp import *
import math


# start = time.clock()


class WSUVVO(object):
    """
    This code is for solving the VVO for  test cases. The planning model is used as
    input and real time load data is required.

    """
    def __init__(self):
        """
        Inputs:
           LinePar
           LoadData
           Graph =  G (V,E)
        """
        pass        
   
    def VVO9500 (self, Linepar, LoadData):    
        
        # Find Tree and Planning model using Linepar
        G = nx.Graph()
        
        # Note: If required, this nor_open list can be obtained from Platform
        nor_open = ['ln0653457_sw','v7173_48332_sw', 'tsw803273_sw', 'a333_48332_sw','tsw320328_sw',\
                   'a8645_48332_sw','tsw568613_sw', 'wf856_48332_sw', 'wg127_48332_sw']  
        for l in Linepar:
            if l['line'] not in nor_open:
                G.add_edge(l['from_br'], l['to_br'])
        T = list(nx.bfs_tree(G, source = 'SOURCEBUS').edges())
        Nodes = list(nx.bfs_tree(G, source = 'SOURCEBUS').nodes())
        
        for l in Linepar:
            if l['line'] in nor_open:
                SW = (l['from_br'], l['to_br'])
                T.append(SW)
                G.add_edge(l['from_br'], l['to_br'])             

        # parameters
        nNodes = G.number_of_nodes()
        nEdges = G.number_of_edges() 
        fr, to = zip(*T)
        fr = list(fr)
        to = list(to) 
        bigM = 15000   
        CVRP = 0.6
        CVRQ = 3
        tap_r1 = 33
        # loadmult = 0.285
            
        # Different variables for optimization function
        si = LpVariable.dicts("s_i", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        vi = LpVariable.dicts("v_i", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        xij = LpVariable.dicts("x_ij", ((i) for i in range(nEdges) ), lowBound=0, upBound=1, cat='Binary')
        Pija = LpVariable.dicts("xPa", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Pijb = LpVariable.dicts("xPb", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Pijc = LpVariable.dicts("xPc", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qija = LpVariable.dicts("xQa", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qijb = LpVariable.dicts("xQb", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qijc = LpVariable.dicts("xQc", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Via = LpVariable.dicts("xVa", ((i) for i in range(nNodes) ), lowBound=0.81, upBound=1.2025, cat='Continous')
        Vib = LpVariable.dicts("xVb", ((i) for i in range(nNodes) ), lowBound=0.81, upBound=1.2025, cat='Continous')
        Vic = LpVariable.dicts("xVc", ((i) for i in range(nNodes) ), lowBound=0.81, upBound=1.2025, cat='Continous')
        tapi1 = LpVariable.dicts("xtap1", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi2 = LpVariable.dicts("xtap2", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi3 = LpVariable.dicts("xtap3", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi4 = LpVariable.dicts("xtap4", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi5 = LpVariable.dicts("xtap5", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi6 = LpVariable.dicts("xtap6", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        swia = LpVariable.dicts("xswa", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        swib = LpVariable.dicts("xswb", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        swic = LpVariable.dicts("xswc", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')

        # Optimization problem objective definitions
        # Minimize the power flow from feeder 
       
        No = [2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753]
        
        prob = LpProblem("CVRSW",LpMinimize)
        prob += Pija[0]+Pijb[0]+Pijc[0] 

        # Constraints (v_i==1)
        for k in range(nNodes):
            prob += vi[k] == 1
        
        # Constraints (s_i<=1)
        for k in range(nNodes):
            prob += si[k] == 1
        


        # Real power flow equation for Phase A, B, and C
        #Phase A   
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            demandQc = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'A':
                    demandP += d['kW']
                    demandQ += d['kVaR']
                    demandQc += d['kVaR_C']
            prob += lpSum(Pija[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Via[indb] == \
                    lpSum(Pija[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2)
            prob += lpSum(Qija[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Via[indb] == \
                    lpSum(Qija[ch[j]] for j in M) + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swia[indb]

        # Phase B
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            demandQc = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'B':
                    demandP += d['kW']
                    demandQ += d['kVaR']
                    demandQc += d['kVaR_C']
            prob += lpSum(Pijb[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Vib[indb] == \
                    lpSum(Pijb[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2)
            prob += lpSum(Qijb[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vib[indb] == \
                    lpSum(Qijb[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swib[indb]

        # Phase C
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            demandQc = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'C':
                    demandP += d['kW']
                    demandQ += d['kVaR']
                    demandQc += d['kVaR_C']
            prob += lpSum(Pijc[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Vic[indb] == \
                    lpSum(Pijc[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2)
            prob += lpSum(Qijc[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vic[indb] == \
                    lpSum(Qijc[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swic[indb]

        # Big-M method for real power flow and switch variable
        for k in range(nEdges):    
            prob += Pija[k] <= bigM * xij[k]
            prob += Pijb[k] <= bigM * xij[k]
            prob += Pijc[k] <= bigM * xij[k] 
            prob += Qija[k] <= bigM * xij[k]
            prob += Qijb[k] <= bigM * xij[k]
            prob += Qijc[k] <= bigM * xij[k] 
            # For reverse flow
            prob += Pija[k] >= -bigM * xij[k]
            prob += Pijb[k] >= -bigM * xij[k] 
            prob += Pijc[k] >= -bigM * xij[k] 
            prob += Qija[k] >= -bigM * xij[k]
            prob += Qijb[k] >= -bigM * xij[k] 
            prob += Qijc[k] >= -bigM * xij[k] 

        # Voltage constraints by coupling with switch variable
        base_Z = 7.2**2
        M = 4
        unit = 1.

        indr  = [8, 33, 41, 1550, 2043, 1014]
        # Phase A
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  list(np.zeros(9))
            Xmatrix =  list(np.zeros(9))
            if l['nPhase'] == 3:
                Rmatrix = l['r']
                Xmatrix = l['x']
                r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = Rmatrix[0], Xmatrix[0], Rmatrix[1], Xmatrix[1], Rmatrix[2], Xmatrix[2]
            if l['nPhase'] == 1 and l['Phase'] == 'A':
                r, x = l['r'], l['x']
                Rmatrix[0], Xmatrix[0] =  r[0], x[0]
                r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = Rmatrix[0], Xmatrix[0], Rmatrix[1], Xmatrix[1], Rmatrix[2], Xmatrix[2]

            if l['is_Switch'] == 1:
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1000)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1000)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1000)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1000)*Qijc[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1000)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1000)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1000)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1000)*Qijc[k] + M*(1-xij[k]) >= 0
            elif l['index'] not in indr : 
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1000)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1000)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1000)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1000)*Qijc[k] == 0

        # Phase B
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_bb,x_bb,r_ba,x_ba,r_bc,x_bc = Rmatrix[4], Xmatrix[4], Rmatrix[3], Xmatrix[3], Rmatrix[5], Xmatrix[5]
            # Write voltage constraints
            if l['is_Switch'] == 1:
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1000)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1000)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1000)*Qijc[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1000)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1000)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1000)*Qijc[k] + M*(1-xij[k]) >= 0
            elif l['index'] not in indr : 
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1000)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1000)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1000)*Qijc[k] == 0

        # Phase C
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_cc,x_cc,r_ca,x_ca,r_cb,x_cb = Rmatrix[8], Xmatrix[8], Rmatrix[6], Xmatrix[6], Rmatrix[7], Xmatrix[7]
            # Write voltage constraints
            if l['is_Switch'] == 1:
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1000)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1000)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1000)*Qijb[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1000)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1000)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1000)*Qijb[k] + M*(1-xij[k]) >= 0
            elif l['index'] not in indr : 
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1000)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1000)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1000)*Qijb[k] == 0
        
        # Initialize source bus at 1.05 p.u. V^2 = 1.1025
        prob += Via[0] == 1.1025
        prob += Vib[0] == 1.1025
        prob += Vic[0] == 1.1025




        # No reverse real power flow in substation
        sub = [4, 27, 34]
        for s in sub:
            prob += Pija[s] >= 0
            prob += Pijb[s] >= 0
            prob += Pijc[s] >= 0
            
        for t in No:
            prob += xij[t]==0
        
        ## 3 regulator at substation and 3 are along the feeder
        
    
        prob += lpSum([tapi1[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi2[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi3[i] for i in range(tap_r1)]) == 1 
        prob += lpSum([tapi4[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi5[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi6[i] for i in range(tap_r1)]) == 1  

        

      
        M = 10
        tapk = np.arange(0.9, 1.1, 0.00625)
        for k in range(0,33):
           prob += Via[9] - tapk[k]**2*Via[7] - M*(1-tapi1[k]) <= 0
           prob += Via[9] - tapk[k]**2*Via[7] + M*(1-tapi1[k]) >= 0
           prob += Vib[9] - tapk[k]**2*Vib[7] - M*(1-tapi1[k]) <= 0
           prob += Vib[9] - tapk[k]**2*Vib[7] + M*(1-tapi1[k]) >= 0
           prob += Vic[9] - tapk[k]**2*Vic[7] - M*(1-tapi1[k]) <= 0
           prob += Vic[9] - tapk[k]**2*Vic[7] + M*(1-tapi1[k]) >= 0
           
           prob += Via[34] - tapk[k]**2*Via[31] - M*(1-tapi2[k]) <= 0    
           prob += Via[34] - tapk[k]**2*Via[31] + M*(1-tapi2[k]) >= 0
           prob += Vib[34] - tapk[k]**2*Vib[31] - M*(1-tapi2[k]) <= 0
           prob += Vib[34] - tapk[k]**2*Vib[31] + M*(1-tapi2[k]) >= 0
           prob += Vic[34] - tapk[k]**2*Vic[31] - M*(1-tapi2[k]) <= 0
           prob += Vic[34] - tapk[k]**2*Vic[31] + M*(1-tapi2[k]) >= 0
           
           prob += Via[42] - tapk[k]**2*Via[38] - M*(1-tapi3[k]) <= 0
           prob += Via[42] - tapk[k]**2*Via[38] + M*(1-tapi3[k]) >= 0
           prob += Vib[42] - tapk[k]**2*Vib[38] - M*(1-tapi3[k]) <= 0
           prob += Vib[42] - tapk[k]**2*Vib[38] + M*(1-tapi3[k]) >= 0
           prob += Vic[42] - tapk[k]**2*Vic[38] - M*(1-tapi3[k]) <= 0
           prob += Vic[42] - tapk[k]**2*Vic[38] + M*(1-tapi3[k]) >= 0
           
           prob += Via[1551] - tapk[k]**2*Via[1525] - M*(1-tapi4[k]) <= 0
           prob += Via[1551] - tapk[k]**2*Via[1525] + M*(1-tapi4[k]) >= 0
           prob += Vib[1551] - tapk[k]**2*Vib[1525] - M*(1-tapi4[k]) <= 0
           prob += Vib[1551] - tapk[k]**2*Vib[1525] + M*(1-tapi4[k]) >= 0
           prob += Vic[1551] - tapk[k]**2*Vic[1525] - M*(1-tapi4[k]) <= 0
           prob += Vic[1551] - tapk[k]**2*Vic[1525] + M*(1-tapi4[k]) >= 0    
           
           prob += Via[2044] - tapk[k]**2*Via[2023] - M*(1-tapi5[k]) <= 0
           prob += Via[2044] - tapk[k]**2*Via[2023] + M*(1-tapi5[k]) >= 0
           prob += Vib[2044] - tapk[k]**2*Vib[2023] - M*(1-tapi5[k]) <= 0
           prob += Vib[2044] - tapk[k]**2*Vib[2023] + M*(1-tapi5[k]) >= 0
           prob += Vic[2044] - tapk[k]**2*Vic[2023] - M*(1-tapi5[k]) <= 0
           prob += Vic[2044] - tapk[k]**2*Vic[2023] + M*(1-tapi5[k]) >= 0
           
           prob += Via[1015] - tapk[k]**2*Via[998] - M*(1-tapi6[k]) <= 0
           prob += Via[1015] - tapk[k]**2*Via[998] + M*(1-tapi6[k]) >= 0
           prob += Vib[1015] - tapk[k]**2*Vib[998] - M*(1-tapi6[k]) <= 0
           prob += Vib[1015] - tapk[k]**2*Vib[998] + M*(1-tapi6[k]) >= 0
           prob += Vic[1015] - tapk[k]**2*Vic[998] - M*(1-tapi6[k]) <= 0
           prob += Vic[1015] - tapk[k]**2*Vic[998] + M*(1-tapi6[k]) >= 0
        

        print ('Solving the VVO problem..........')
        # Call solver 
        prob.solve()
        # prob.solve(CPLEX(msg=0))
        prob.writeLP("Check.lp")
        print ("Status:", LpStatus[prob.status])
        print(Pija[0].varValue, Pijb[0].varValue, Pijc[0].varValue )
        print(Pija[0].varValue + Pijb[0].varValue + Pijc[0].varValue)
        print ('..........')
        print(Qija[0].varValue, Qijb[0].varValue, Qijc[0].varValue )
        print(Qija[0].varValue + Qijb[0].varValue + Qijc[0].varValue)
        print ('..........')

        # Each substation power flow
        print(' Substation #1:', Pija[4].varValue, Pijb[4].varValue, Pijc[4].varValue )
        print(' Substation #2:', Pija[27].varValue, Pijb[27].varValue, Pijc[27].varValue )
        print(' Substation #3:', Pija[34].varValue, Pijb[34].varValue, Pijc[34].varValue )
        print ('..........')
        print(' Tie Switch Status:')        
        for k in range(len(No)):
            print(xij[No[k]].varValue)
        
        taps = []
        for i in range(tap_r1):
            if tapi1[i].varValue == 1:
                print(i,tapi1[i].varValue)
                taps.append(k-17)

            if tapi2[i].varValue == 1:
                print(i,tapi2[i].varValue)
                taps.append(k-17)
                
            if tapi3[i].varValue == 1:
                print(i,tapi3[i].varValue)
                taps.append(k-17)
               
            if tapi4[i].varValue == 1:
                print(i,tapi4[i].varValue)
                taps.append(k-17)
               
            if tapi5[i].varValue == 1:
                print(i,tapi5[i].varValue)
                taps.append(k-17)
               
            if tapi6[i].varValue == 1:
                print(i,tapi6[i].varValue)
                taps.append(k-17)
               
        status_c = [swia[36].varValue,swib[36].varValue,swic[36].varValue,swia[624].varValue,swib[624].varValue,swic[624].varValue,\
              swia[1841].varValue,swib[1841].varValue,swic[1841].varValue,swia[513].varValue,swib[513].varValue,swic[513].varValue]
        status_r = taps
        return status_c, status_r        
#         for i in range(tap_r1):
#             if tapi1[i].varValue > 0.9:
#                 print(i,tapi1[i].varValue)
# #        reguind = [7, 9, 31, 34,38,42, 1525,1551, 2023,2044,998, 1015]
#         print(np.sqrt(Via[7].varValue),np.sqrt(Via[9].varValue),np.sqrt(Via[31].varValue),np.sqrt(Via[34].varValue),\
#               np.sqrt(Via[38].varValue),np.sqrt(Via[42].varValue),np.sqrt(Via[1525].varValue),np.sqrt(Via[1551].varValue),\
#               np.sqrt(Via[2023].varValue),np.sqrt(Via[2044].varValue),np.sqrt(Via[998].varValue),np.sqrt(Via[1015].varValue))
#         print(swia[36].varValue,swib[36].varValue,swic[36].varValue,swia[624].varValue,swib[624].varValue,swic[624].varValue,\
#               swia[1841].varValue,swib[1841].varValue,swic[1841].varValue,swia[513].varValue,swib[513].varValue,swic[513].varValue)