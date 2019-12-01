# -*- coding: utf-8 -*-
"""
Created on Fri no 22 11:17:12 2019
@author: rjha
"""
import json
import numpy as np
import math

class PowerData(object):
    """
    WSU VVO, Get load data from feeder
    """
    def __init__(self, msr_mrids_load, sim_output,xmfr):
        self.meas_load = msr_mrids_load
        self.output = sim_output
        self.xmfr = xmfr
        
    def demand(self):
        data1 = self.meas_load
        data2 = self.output
        # data2 = json.loads(data2.replace("\'",""))
        meas_value = data2['message']['measurements']     
        timestamp = data2["message"] ["timestamp"]

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
                                kVaR_C = 0)
                Demand.append(message)    

        # Combine the dictionary from S1 and S2 to balanced load. 
        # VA measumrement has two different loads on S1 and S2 phase
        for i, l in enumerate(Demand):
            if i % 2 == 0:
                d1 = Demand[i]
                d2 = Demand[i+1]
                l['kW'] = d1['kW'] + d2['kW']
                l['kVaR'] = d1['kVaR'] + d2['kVaR']

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
        for d in Demand:
            sP += d['kW']
            sQ += d['kVaR']
        print('The total real and reactive demand is:', sP, sQ)
        
        with open('PlatformD.json', 'w') as json_file:
            json.dump(Demand, json_file)

        
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
                kVaR_C = cap_kvar_value [i])
            Demand.append(cap1)

        return Demand

        # Transferring the load to Primary side for solving the restoration. No triplex line in optimization model