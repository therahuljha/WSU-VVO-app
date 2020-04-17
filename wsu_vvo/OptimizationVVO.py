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
   
    def VVO9500 (self, Linepar, LoadData,open_switch,xmfr):    
        
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
        CVRP = 1.0
        CVRQ = 1.0
        tap_r1 = 33
        loadmult = 1
        bkva = 1000.0
            
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
        Via = LpVariable.dicts("xVa", ((i) for i in range(nNodes) ), lowBound=0.81, upBound=1.1025, cat='Continous')
        Vib = LpVariable.dicts("xVb", ((i) for i in range(nNodes) ), lowBound=0.81, upBound=1.1025, cat='Continous')
        Vic = LpVariable.dicts("xVc", ((i) for i in range(nNodes) ), lowBound=0.81, upBound=1.1025, cat='Continous')
        tapi1 = LpVariable.dicts("xtap1", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi2 = LpVariable.dicts("xtap2", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi3 = LpVariable.dicts("xtap3", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi4 = LpVariable.dicts("xtap4", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi5 = LpVariable.dicts("xtap5", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        tapi6 = LpVariable.dicts("xtap6", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi7 = LpVariable.dicts("xtap7", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi8 = LpVariable.dicts("xtap8", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi9 = LpVariable.dicts("xtap9", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi10 = LpVariable.dicts("xtap10", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi11 = LpVariable.dicts("xtap11", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi12 = LpVariable.dicts("xtap12", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi13 = LpVariable.dicts("xtap13", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi14 = LpVariable.dicts("xtap14", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi15 = LpVariable.dicts("xtap15", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi16 = LpVariable.dicts("xtap16", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi17 = LpVariable.dicts("xtap17", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        # tapi18 = LpVariable.dicts("xtap18", ((i) for i in range(tap_r1) ), lowBound=0, upBound=1, cat='Binary')
        swia = LpVariable.dicts("xswa", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        swib = LpVariable.dicts("xswb", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        swic = LpVariable.dicts("xswc", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        # QPVa = LpVariable.dicts("xQPVa", ((i) for i in range(nNodes) ), lowBound=-1, upBound=1, cat='Continous')
        # QPVb = LpVariable.dicts("xQPVb", ((i) for i in range(nNodes) ), lowBound=-1, upBound=1, cat='Continous')
        # QPVc = LpVariable.dicts("xQPVc", ((i) for i in range(nNodes) ), lowBound=-1, upBound=1, cat='Continous')

   
        # Optimization problem objective definitions
        # Minimize the power flow from feeder        
             
        prob = LpProblem("CVRSW",LpMinimize)
        prob += Pija[0]+Pijb[0]+Pijc[0] 
        sub = [4, 27, 34]
        # prob += Pija[4]+Pijb[4]+Pijc[4] + Pija[27]+Pijb[27]+Pijc[27] + Pija[34]+Pijb[34]+Pijc[34]

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
            demandPpv = 0.
            demandSpv = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'A':
                    demandP += d['kW']/bkva
                    demandQ += d['kVaR']/bkva
                    demandQc += d['kVaR_C']/bkva
                    demandPpv += d['kW_pv']/bkva
                    demandSpv += d['kVA_pv']/bkva
            prob += lpSum(Pija[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Via[indb] == \
                    lpSum(Pija[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2) + demandPpv
            prob += lpSum(Qija[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Via[indb] == \
                    lpSum(Qija[ch[j]] for j in M) + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swia[indb]  
            # prob += lpSum(Qija[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Via[indb] == \
            #         lpSum(Qija[ch[j]] for j in M) + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swia[indb]  + (np.sqrt(demandSpv**2 - demandPpv**2))*QPVa[indb]

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
            demandPpv = 0.
            demandSpv = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'B':
                    demandP += d['kW']/bkva
                    demandQ += d['kVaR']/bkva
                    demandQc += d['kVaR_C']/bkva
                    demandPpv += d['kW_pv']/bkva
                    demandSpv += d['kVA_pv']/bkva
            prob += lpSum(Pijb[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Vib[indb] == \
                    lpSum(Pijb[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2) + demandPpv
            prob += lpSum(Qijb[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vib[indb] == \
                    lpSum(Qijb[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swib[indb] 
            # prob += lpSum(Qijb[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vib[indb] == \
            #         lpSum(Qijb[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swib[indb] + (np.sqrt(demandSpv**2 - demandPpv**2))*QPVb[indb]

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
            demandPpv = 0.
            demandSpv = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'C':
                    demandP += d['kW']/bkva
                    demandQ += d['kVaR']/bkva
                    demandQc += d['kVaR_C']/bkva
                    demandPpv += d['kW_pv']/bkva
                    demandSpv += d['kVA_pv']/bkva
            prob += lpSum(Pijc[pa[j]] for j in N) - loadmult*(demandP)*(CVRP/2)*Vic[indb] == \
                    lpSum(Pijc[ch[j]] for j in M) + loadmult*(demandP)*(1-CVRP/2) + demandPpv
            prob += lpSum(Qijc[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vic[indb] == \
                    lpSum(Qijc[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swic[indb] 
            # prob += lpSum(Qijc[pa[j]] for j in N) - loadmult*(demandQ)*(CVRQ/2)*Vic[indb] == \
            #         lpSum(Qijc[ch[j]] for j in M)  + loadmult*(demandQ)*(1-CVRQ/2) - demandQc*swic[indb] + (np.sqrt(demandSpv**2 - demandPpv**2))*QPVc[indb]

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

        ## regulator index
        indr  = [8, 33, 41, 1550, 2043, 1014]

        # Phase A
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = Rmatrix[0], Xmatrix[0], Rmatrix[1], Xmatrix[1], Rmatrix[2], Xmatrix[2]
            # Write voltage constraints
            if l['is_Switch'] == 1:
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1)*Qijc[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1)*Qijc[k] + M*(1-xij[k]) >= 0
            elif l['index'] not in indr : 
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1)*Qijc[k] == 0

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
                2*r_bb*length/(unit*base_Z*1)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1)*Qijc[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1)*Qijc[k] + M*(1-xij[k]) >= 0
            elif l['index'] not in indr : 
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1)*Qijc[k] == 0

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
                2*r_cc*length/(unit*base_Z*1)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1)*Qijb[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1)*Qijb[k] + M*(1-xij[k]) >= 0
            elif l['index'] not in indr : 
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1)*Qijb[k] == 0
        
        # Initialize source bus at 1.05 p.u. V^2 = 1.1025
        # prob += Via[0] == 1.1025
        # prob += Vib[0] == 1.1025
        # prob += Vic[0] == 1.1025
        prob += Via[0] == 1.0
        prob += Vib[0] == 1.0
        prob += Vic[0] == 1.0


        # No reverse real power flow in substation
        sub = [4, 27, 34]
        for s in sub:
            prob += Pija[s] >= 0
            prob += Pijb[s] >= 0
            prob += Pijc[s] >= 0
        
        No = open_switch

        for t in No:
            prob += xij[t]==0
        
        
        ## 3 regulator at substation and 3 are along the feeder

        ## tap1+tap2+....tap33 ==1 only one tap position will be 1 , other 0
        
    
        prob += lpSum([tapi1[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi2[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi3[i] for i in range(tap_r1)]) == 1 
        prob += lpSum([tapi4[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi5[i] for i in range(tap_r1)]) == 1  
        prob += lpSum([tapi6[i] for i in range(tap_r1)]) == 1  
        
        # prob += lpSum([tapi7[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi8[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi9[i] for i in range(tap_r1)]) == 1 
        # prob += lpSum([tapi10[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi11[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi12[i] for i in range(tap_r1)]) == 1 
        
        # prob += lpSum([tapi13[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi14[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi15[i] for i in range(tap_r1)]) == 1 
        # prob += lpSum([tapi16[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi17[i] for i in range(tap_r1)]) == 1  
        # prob += lpSum([tapi18[i] for i in range(tap_r1)]) == 1 

        
        ## v2 - tap^2*v1 ==0
      
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
        #    prob += Via[9] - tapk[k]**2*Via[7] - M*(1-tapi1[k]) <= 0
        #    prob += Via[9] - tapk[k]**2*Via[7] + M*(1-tapi1[k]) >= 0
        #    prob += Vib[9] - tapk[k]**2*Vib[7] - M*(1-tapi2[k]) <= 0
        #    prob += Vib[9] - tapk[k]**2*Vib[7] + M*(1-tapi2[k]) >= 0
        #    prob += Vic[9] - tapk[k]**2*Vic[7] - M*(1-tapi3[k]) <= 0
        #    prob += Vic[9] - tapk[k]**2*Vic[7] + M*(1-tapi3[k]) >= 0
           
        #    prob += Via[34] - tapk[k]**2*Via[31] - M*(1-tapi4[k]) <= 0    
        #    prob += Via[34] - tapk[k]**2*Via[31] + M*(1-tapi4[k]) >= 0
        #    prob += Vib[34] - tapk[k]**2*Vib[31] - M*(1-tapi5[k]) <= 0
        #    prob += Vib[34] - tapk[k]**2*Vib[31] + M*(1-tapi5[k]) >= 0
        #    prob += Vic[34] - tapk[k]**2*Vic[31] - M*(1-tapi6[k]) <= 0
        #    prob += Vic[34] - tapk[k]**2*Vic[31] + M*(1-tapi6[k]) >= 0
           
        #    prob += Via[42] - tapk[k]**2*Via[38] - M*(1-tapi7[k]) <= 0
        #    prob += Via[42] - tapk[k]**2*Via[38] + M*(1-tapi7[k]) >= 0
        #    prob += Vib[42] - tapk[k]**2*Vib[38] - M*(1-tapi8[k]) <= 0
        #    prob += Vib[42] - tapk[k]**2*Vib[38] + M*(1-tapi8[k]) >= 0
        #    prob += Vic[42] - tapk[k]**2*Vic[38] - M*(1-tapi9[k]) <= 0
        #    prob += Vic[42] - tapk[k]**2*Vic[38] + M*(1-tapi9[k]) >= 0
           
        #    prob += Via[1551] - tapk[k]**2*Via[1525] - M*(1-tapi10[k]) <= 0
        #    prob += Via[1551] - tapk[k]**2*Via[1525] + M*(1-tapi10[k]) >= 0
        #    prob += Vib[1551] - tapk[k]**2*Vib[1525] - M*(1-tapi11[k]) <= 0
        #    prob += Vib[1551] - tapk[k]**2*Vib[1525] + M*(1-tapi11[k]) >= 0
        #    prob += Vic[1551] - tapk[k]**2*Vic[1525] - M*(1-tapi12[k]) <= 0
        #    prob += Vic[1551] - tapk[k]**2*Vic[1525] + M*(1-tapi12[k]) >= 0    
           
        #    prob += Via[2044] - tapk[k]**2*Via[2023] - M*(1-tapi13[k]) <= 0
        #    prob += Via[2044] - tapk[k]**2*Via[2023] + M*(1-tapi13[k]) >= 0
        #    prob += Vib[2044] - tapk[k]**2*Vib[2023] - M*(1-tapi14[k]) <= 0
        #    prob += Vib[2044] - tapk[k]**2*Vib[2023] + M*(1-tapi14[k]) >= 0
        #    prob += Vic[2044] - tapk[k]**2*Vic[2023] - M*(1-tapi15[k]) <= 0
        #    prob += Vic[2044] - tapk[k]**2*Vic[2023] + M*(1-tapi15[k]) >= 0
           
        #    prob += Via[1015] - tapk[k]**2*Via[998] - M*(1-tapi16[k]) <= 0
        #    prob += Via[1015] - tapk[k]**2*Via[998] + M*(1-tapi16[k]) >= 0
        #    prob += Vib[1015] - tapk[k]**2*Vib[998] - M*(1-tapi17[k]) <= 0
        #    prob += Vib[1015] - tapk[k]**2*Vib[998] + M*(1-tapi17[k]) >= 0
        #    prob += Vic[1015] - tapk[k]**2*Vic[998] - M*(1-tapi18[k]) <= 0
        #    prob += Vic[1015] - tapk[k]**2*Vic[998] + M*(1-tapi18[k]) >= 0
        

        print ('Solving the VVO problem..........')
        # Call solver 
        # prob.solve()
        print("using Pulp solver")
        prob.solve(pulp.PULP_CBC_CMD(msg=True))
            # prob.solve()
        prob.writeLP("Check.lp")


        # print("using Cplex solver")
        # prob.solve(CPLEX(msg=1))
        # print ("Status:", LpStatus[prob.status])

        for i in range(tap_r1):
            if tapi1[i].varValue >= 0.9:
                tap1 = (i-17)

            if tapi2[i].varValue >= 0.9:
                tap2 = (i-17)
            
            if tapi3[i].varValue >= 0.9:
                tap3 = (i-17)
                        
            if tapi4[i].varValue >= 0.9:
                tap4 = (i-17)
        
            if tapi5[i].varValue >= 0.9:
                tap5 = (i-17)
        
            if tapi6[i].varValue >= 0.9:
                tap6 = (i-17)

        status_c = [swia[1841].varValue,swib[1841].varValue,swic[1841].varValue, swia[624].varValue,swib[624].varValue,swic[624].varValue,\
        swia[36].varValue,swib[36].varValue,swic[36].varValue, swia[513].varValue,swib[513].varValue,swic[513].varValue]

        status_r = [tap5, tap5, tap3,tap1, tap3, tap6, tap2, tap2, tap2, tap5, tap3, tap1, tap6, tap4, tap4, tap4, tap1, tap6]

        flag = 1
        # return status_c, status_r, Qpvcontrol, flag
        return status_c, status_r, flag
            
#         try:
#             # prob.solve(CPLEX_CMD(msg=1,options=['set mip tolerances mipgap 0.05']))
#             # prob.writeLP("Check.lp")
#             # print ("Status:", LpStatus[prob.status])
#             print("using Pulp solver")
#             prob.solve(pulp.PULP_CBC_CMD(msg=True))
#                 # prob.solve()
#             prob.writeLP("Check.lp")
#                 # print ("Status:", LpStatus[prob.status])
#             # print("using Cplex solver")
#             # prob.solve(CPLEX(msg=1))
#             # prob.writeLP("Check.lp")
#             # print ("Status:", LpStatus[prob.status])
                        
#         except:
#             try:
#                 print("using Pulp solver")
#                 prob.solve(pulp.PULP_CBC_CMD(msg=True))
#                 # prob.solve()
#                 prob.writeLP("Check.lp")
#                 print ("Status:", LpStatus[prob.status])
#             except:
#                 print("Solution not found")
        
#         try:
            
#             # status_c = [swia[1841].varValue,swib[1841].varValue,swic[1841].varValue, swia[624].varValue,swib[624].varValue,swic[624].varValue,\
#             #     swia[36].varValue,swib[36].varValue,swic[36].varValue, swia[513].varValue,swib[513].varValue,swic[513].varValue]
            
#             # print(status_c)
#             # print('\n .........................')
            
#             # taps = []
#             for i in range(tap_r1):
#                 if tapi1[i].varValue >= 0.9:
# #                    print(i,tapi1[i].varValue)
#                     tap1 = (i-17)
#                     # taps.append(i-17)
#                     # taps.append(i-17)

#                 if tapi2[i].varValue >= 0.9:
#                     # print(i,tapi2[i].varValue)
#                     tap2 = (i-17)
                    
                    
#                 if tapi3[i].varValue >= 0.9:
#                     # print(i,tapi3[i].varValue)
#                     tap3 = (i-17)
                                
#                 if tapi4[i].varValue >= 0.9:
#                     # print(i,tapi4[i].varValue)
#                     tap4 = (i-17)
                
#                 if tapi5[i].varValue >= 0.9:
#                     # print(i,tapi5[i].varValue)
#                     tap5 = (i-17)
                
#                 if tapi6[i].varValue >= 0.9:
#                     # print(i,tapi6[i].varValue)?
#                     tap6 = (i-17)

#                 # if tapi7[i].varValue >= 0.9:
#                 #     tap7 = (i-17)
            
#                 # if tapi8[i].varValue >= 0.9:
#                 #     tap8 = (i-17)

#                 # if tapi9[i].varValue >= 0.9:
#                 #     tap9 = (i-17)
#                 # # print(tapi10)
#                 # if tapi10[i].varValue >= 0.9:
#                 #     tap10 = (i-17)

#                 # if tapi11[i].varValue >= 0.9:
#                 #     tap11 = (i-17)

#                 # if tapi12[i].varValue >= 0.9:
#                 #     tap12 = (i-17)

#                 # if tapi13[i].varValue >= 0.9:
#                 #     tap13 = (i-17)

#                 # if tapi14[i].varValue >= 0.9:
#                 #     tap14 = (i-17)

#                 # if tapi15[i].varValue >= 0.9:
#                 #     tap15 = (i-17)

#                 # if tapi16[i].varValue >= 0.9:
#                 #     tap16 = (i-17)

#                 # if tapi17[i].varValue >= 0.9:
#                 #     tap17 = (i-17)

#                 # if tapi18[i].varValue >= 0.9:
#                 #     tap18 = (i-17)


#             # Qpvcontrol = []
#             # for i in range(nNodes):
#             #     demandPpv = 0.
#             #     demandSpv = 0.            
#             #     for l in LoadData:
#             #         if l['bus'] == Nodes[i]:
#             #             demandPpv += d['kW_pv']
#             #             demandSpv += d['kVA_pv']
#             #             break

#             #     if QPVa[i].varValue != None:
#             #         # print((np.sqrt(demandSpv**2 - demandPpv**2))*(QPVa[i].varValue))
#             #         value = (np.sqrt(demandSpv**2 - demandPpv**2))*(QPVa[i].varValue)
#             #         # store = [value, l['bus']]
#             #         message = dict(bus = l['bus'],
#             #                         mrid = 'abc',
#             #                         val = value)
#             #         # print(store)
#             #         Qpvcontrol.append(message)

#             #     if QPVb[i].varValue != None:
#             #         # print((np.sqrt(demandSpv**2 - demandPpv**2))*(QPVb[i].varValue))
#             #         value = (np.sqrt(demandSpv**2 - demandPpv**2))*(QPVb[i].varValue)
#             #         message = dict(bus = l['bus'],
#             #                         mrid = 'abc',
#             #                         val = value)
#             #         Qpvcontrol.append(message)

#             #     if QPVc[i].varValue != None:
#             #         # print((np.sqrt(demandSpv**2 - demandPpv**2))*(QPVa[i].varValue))
#             #         value = (np.sqrt(demandSpv**2 - demandPpv**2))*(QPVc[i].varValue)
#             #         message = dict(bus = l['bus'],
#             #                         mrid = 'abc',
#             #                         val = value)
#             #         Qpvcontrol.append(message)

#             # for ld in Qpvcontrol:
#             #     node = ld['bus']
#             #     # print(node)
#             #     # Find this node in Xfrm primary
#             #     for tr in xmfr:
#             #         pri = tr['bus1']
#             #         # print(pri)
#             #         seci = tr['bus2']
#             #         # print(pseci)
#             #         if pri == node.lower():
#             #             ld['bus'] = 's'+tr['bus2']                    # Transfer this Qcontrol to secondary and change the node name
                        
                
#             # status_c = [swia[1841].varValue,swib[1841].varValue,swic[1841].varValue, swia[624].varValue,swib[624].varValue,swic[624].varValue,\
#             #       swia[36].varValue,swib[36].varValue,swic[36].varValue, swia[513].varValue,swib[513].varValue,swic[513].varValue]

#             # status_c = [swia[36].varValue,swib[36].varValue,swic[36].varValue,swia[624].varValue,swib[624].varValue,swic[624].varValue,\
#             #       swia[1841].varValue,swib[1841].varValue,swic[1841].varValue,swia[513].varValue,swib[513].varValue,swic[513].varValue]

#             # status_r = [tap1, tap2, tap3, tap4, tap5, tap6, tap7, tap8, tap9, tap10, tap11, tap12, tap13, tap14, tap15, tap16, tap17, tap18]
#             # status_r = [tap1, tap1, tap1, tap2, tap2, tap2, tap3, tap3, tap3, tap4, tap4, tap4, tap5, tap5, tap5, tap6, tap6, tap6]
#             status_r = [tap5, tap5, tap3,tap1, tap3, tap6, tap2, tap2, tap2, tap5, tap3, tap1, tap6, tap4, tap4, tap4, tap1, tap6]
#             # if swia[1841].varValue >0.5:
#             #     cap1 =1
#             # else:
#             #     cap1=0
             
#             # if swib[1841].varValue >0.5:
#             #     cap2 =1
#             # else:
#             #     cap2=0

#             # if swic[1841].varValue >0.5:
#             #     cap3 =1
#             # else:
#             #     cap3=0

#             # if swia[624].varValue >0.5:
#             #     cap4 =1
#             # else:
#             #     cap4=0

#             # if swib[624].varValue >0.5:
#             #     cap5 =1
#             # else:
#             #     cap5=0

#             # if swic[624].varValue >0.5:
#             #     cap6 =1
#             # else:
#             #     cap6=0

#             # if swia[36].varValue >0.5:
#             #     cap7 =1
#             # else:
#             #     cap7 =0

#             # if swib[36].varValue >0.5:
#             #     cap8 =1
#             # else:
#             #     cap8=0

#             # if swic[36].varValue >0.5:
#             #     cap9 =1
#             # else:
#             #     cap9=0

#             # if swia[513].varValue >0.5:
#             #     cap10 =1
#             # else:
#             #     cap10=0

#             # if swib[513].varValue >0.5:
#             #     cap11 =1
#             # else:
#             #     cap11=0
                
#             # if swic[513].varValue >0.5:
#             #     cap12 =1
#             # else:
#             #     cap12=0

#             status_c = [cap1,cap2,cap3, cap4, cap5,cap6,cap7,cap8,cap9, cap10,cap11,cap12]
            # print(status_r)

        #     flag = 1
        #     # return status_c, status_r, Qpvcontrol, flag
        #     return status_c, status_r, flag
        # except:
        #     status_c = []
        #     status_r = []
        #     flag = 0
        #     # Qpvcontrol = []
        #     # return status_c, status_r, Qpvcontrol, flag
        #     return status_c, status_r, flag
