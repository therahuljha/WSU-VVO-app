# -*- coding: utf-8 -*-
"""
Created on Fri no 22 11:17:12 2019
@author: rjha
"""
import json
import numpy as np
import math
import networkx as nx 

class PowerData(object):
    """
    WSU VVO, Get load data from feeder
    """
    def __init__(self, msr_mrids_load, sim_output,xmfr, obj_msr_inv, LineData,open_switch,nodev):
        self.meas_load = msr_mrids_load
        self.output = sim_output
        self.xmfr = xmfr
        self.LineData = LineData
        self.open_switch = open_switch
        self.obj_msr_inv = obj_msr_inv
        self.nodev = nodev
        
    def demand(self):
        data1 = self.meas_load
        data2 = self.output
        data3 = self.obj_msr_inv
        datanodev = self.nodev
        # data2 = json.loads(data2.replace("\'",""))
        meas_value = data2['message']['measurements']     
        timestamp = data2["message"] ["timestamp"]

        
        datav = datanodev['data']

        sub1=[]
        dpq = [d for d in datav if d['type'] == 'VA']
        for d1 in dpq:
            if  d1['eqname']=='hvmv_sub_connector':
                eqmeasid = d1['measid']
                if eqmeasid in meas_value:
                    pq = meas_value[eqmeasid]
                    sub1.append(0.001 * pq['magnitude'])
        # print(sub1)

        sub2=[]
        dpq = [d for d in datav if d['type'] == 'VA']
        for d1 in dpq:
            if  d1['eqname']=='hvmv69s1s2-1':
                eqmeasid = d1['measid']
                if eqmeasid in meas_value:
                    pq = meas_value[eqmeasid]
                    sub2.append(0.001 * pq['magnitude'])
        # print(sub2)
        
        # totalsubpower = [i+j for i,j in zip(sub1,sub2)]
        # print('total power from substation........')
        # print(totalsubpower)


        ds = [d for d in datav if d['type'] == 'PNV']
        voltage = []
        for d1 in ds:                
            if d1['measid'] in meas_value:
                v = d1['measid']
                volang = meas_value[v]
                # Check phase of load in 9500 node based on last letter
                loadbus = d1['bus']
                phase = d1['phases']
                message = dict(bus = d1['bus'],
                                PNV = [volang['magnitude'], volang['angle']],
                                Phase = phase)
                voltage.append(message) 

        with open('Platform_V.json', 'w') as json_file:
            json.dump(voltage, json_file)
        # print(voltage)

        # Find interested mrids of 9500 Node. We are only interested in VA of the nodes
        # Convert VA to kw and kVAR        
        data1 = data1['data']
        ds = [d for d in data1 if d['type'] != 'PNV']

        Demand = []
        for d1 in ds:                
            if d1['measid'] in meas_value:
                v = d1['measid']
                pq = meas_value[v]
                # Check phase of load in 9500 node based on last letter
                loadbus = d1['bus']
                phase = loadbus[-1].upper()
                phi = (pq['angle'])*math.pi/180
                message = dict(bus = d1['bus'],
                                VA = [pq['magnitude'], pq['angle']],
                                Phase = phase,
                                kW = 0.001 * pq['magnitude']*np.cos(phi),
                                kVaR = 0.001* pq['magnitude']*np.sin(phi),
                                kVaR_C = 0.,
                                kVA_pv = 0.,
                                kW_pv = 0.)
                Demand.append(message)    
        

        # # data3 = data3['data']
        # # print(data3[1])
        # ds = [d for d in data3 if d['type'] != 'PNV']
        pv_out = []
        for d1 in data3:                
            if d1['measid'] in meas_value:
                v = d1['measid']
                pq = meas_value[v]
                # Check phase of load in 9500 node based on last letter
                loadbus = d1['bus']
                phase = loadbus[-1].upper()
                phi = (pq['angle'])*math.pi/180
                message = dict(bus = d1['bus'],
                                VA = [pq['magnitude'], pq['angle']],
                                Phase = phase,
                                kW_pv = 0.001 * pq['magnitude']*np.cos(phi),
                                kVA_pv = 1 * d1['Srated'])
                pv_out.append(message) 
        # print(pv_out)
        with open('pvoutput.json', 'w') as json_file:
            json.dump(pv_out, json_file)

       
        for p in pv_out:
            pv_bus = p['bus']
            for d in Demand:
                if pv_bus == d['bus']:
                    d['kW_pv'] = p['kW_pv']
                    d['kVA_pv'] = p ['kVA_pv']




        # Combine the dictionary from S1 and S2 to balanced load. 
        # VA measumrement has two different loads on S1 and S2 phase
        for i, l in enumerate(Demand):
            if i % 2 == 0:
                d1 = Demand[i]
                d2 = Demand[i+1]
                l['kW'] = d1['kW'] + d2['kW']
                l['kVaR'] = d1['kVaR'] + d2['kVaR']
                l['kW_pv'] = d1['kW_pv'] + d2['kW_pv']
                # l['kVA_pv'] = d1['kVA_pv'] + d2['kVA_pv']


        for ld in Demand:
            node = ld['bus'].strip('s')
            # Find this node in Xfrm to_br
            for tr in self.xmfr:
                sec = tr['bus2']
                if sec == node:
                    # Transfer this load to primary and change the node name
                    ld['bus'] = tr['bus1'].upper()
        
        Demand = [l for d, l in enumerate(Demand) if d % 2 == 0]
        

        sP = 0
        sQ = 0
        sPVp = 0
        for d in Demand:
            sP += d['kW']
            sQ += d['kVaR']
            sPVp += d['kW_pv']
            
        print('The total real and reactive demand and PV active power  is:', sP, sQ, sPVp)
        
        # with open('PlatformD.json', 'w') as json_file:
        #     json.dump(Demand, json_file)

        
        cap_bus_ind = ['R42246', 'R42246', 'R42246', 'R42247' , 'R42247' , 'R42247' , 'R20185' , 'R20185' , 'R20185' ,'R18242', 'R18242','R18242']
        cap_bus_phase = ['A', 'B', 'C','A', 'B', 'C','A', 'B', 'C','A', 'B', 'C']
        cap_kvar_value = [400, 400, 400, 300, 300, 300, 300, 300, 300, 300, 300, 300]

        for i in range(12):
            # print(cap_bus_phase[i])
            cap1 = dict(
                bus = cap_bus_ind[i],
                Phase = cap_bus_phase[i],
                kW = 0,
                kVaR = 0,
                kW_pv = 0,
                kVA_pv = 0,
                kVaR_C = cap_kvar_value [i])
            Demand.append(cap1)  

        G = nx.Graph()
        
        # Note: If required, this nor_open list can be obtained from Platform
        nor_open = ['ln0653457_sw','v7173_48332_sw', 'tsw803273_sw', 'a333_48332_sw','tsw320328_sw',\
                'a8645_48332_sw','tsw568613_sw', 'wf856_48332_sw', 'wg127_48332_sw']  

        for l in self.LineData:
            if l['line'] not in nor_open:
                G.add_edge(l['from_br'], l['to_br'])
        T = list(nx.bfs_tree(G, source = 'SOURCEBUS').edges())
        Nodes = list(nx.bfs_tree(G, source = 'SOURCEBUS').nodes())
       
        G1 = nx.Graph()

         
        for l in self.LineData:
            if l['index'] not in self.open_switch:
                G1.add_edge(l['from_br'], l['to_br'])
        T1 = list(nx.bfs_tree(G1, source = 'SOURCEBUS').edges())
        Nodes1 = list(nx.bfs_tree(G1, source = 'SOURCEBUS').nodes())

        diff_node = list(set(Nodes) - set(Nodes1))
        for l in Demand:
            if l['bus'] in diff_node:
                l['kW'] = 0
                l['kVaR'] = 0
                l['kVaR_C'] = 0
                l['kVA_pv'] = 0
                l['kW_pv'] = 0

        # print(Demand)
        with open('Demand.json', 'w') as json_file:
            json.dump(Demand, json_file)
            
        return Demand


    # def nodevolt(self):
    #     data2 = self.output


    #     meas_value = data2['message']['measurements']     
    #     timestamp = data2["message"] ["timestamp"]





    # def pvinv(self):

    #     data1 = self.inverters
    #     data2 = self.output
    #     # data2 = json.loads(data2.replace("\'",""))
    #     meas_value = data2['message']['measurements']     
    #     timestamp = data2["message"] ["timestamp"]

    #     # Find interested mrids of 9500 Node. We are only interested in VA of the nodes
    #     # First, we deal with only PV in new neighborhood so bus name to be sx200 
    #     data1 = data1['data']
    #     ds = [d for d in data1 if d['type'] != 'PNV' and 'sx200' in d['bus']]
    #     pv_out = []
    #     for d1 in ds:                
    #         if d1['measid'] in meas_value:
    #             v = d1['measid']
    #             pq = meas_value[v]
    #             # Check phase of load in 9500 node based on last letter
    #             loadbus = d1['bus']
    #             phase = loadbus[-1].upper()
    #             phi = (pq['angle'])*math.pi/180
    #             message = dict(bus = d1['bus'],
    #                             VA = [pq['magnitude'], pq['angle']],
    #                             Phase = phase,
    #                             kW = 0.001 * pq['magnitude']*np.cos(phi),
    #                             kVaR = 0.001* pq['magnitude']*np.sin(phi))
    #             pv_out.append(message)    

    #     # Combine the dictionary from S1 and S2 to balanced load. 
    #     # VA measumrement has two different loads on S1 and S2 phase
    #     for i, l in enumerate(pv_out):
    #         if i % 2 == 0:
    #             d1 = pv_out[i]
    #             d2 = pv_out[i+1]
    #             l['kW'] = d1['kW'] + d2['kW']
    #             l['kVaR'] = d1['kVaR'] + d2['kVaR']
    #     pv_out = [l for d, l in enumerate(pv_out) if d % 2 == 0]


    

        # Transferring the load to Primary side for solving the restoration. No triplex line in optimization model
