# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 11:17:12 2019
@author: rjha
"""
import json
import networkx as nx

class Topology(object):
    """
    WSU VVO
    Identify the current topology of the test case
    """
    def __init__(self, msr_mrids_load, switches, sim_output, LineData):
        self.meas_load = msr_mrids_load
        self.output = sim_output
        self.switches = switches
        # self.TOP = TOP
        self.LineData =  LineData
        # self._alarm =  alarm
        # self._faulted = faulted     
        
    def curr_top(self):
        data1 = self.meas_load
        data2 = self.output     
       
        # data2 = json.loads(data2.replace("\'",""))
        timestamp = data2["message"] ["timestamp"]
        meas_value = data2['message']['measurements']
        data2 = data2["message"]["measurements"]
        
        # Find interested mrids. We are only interested in Position of the switches
        ms_id = []
        bus = []     
        data1 = data1['data']
        ds = [d for d in data1 if d['type'] == 'Pos']

        # Store the open switches
        Loadbreak = []
        for d1 in ds:                
            if d1['measid'] in meas_value:
                v = d1['measid']
                p = meas_value[v]
                if p['value'] == 0:
                    Loadbreak.append(d1['eqname'])
        # print('.......................................')
        # print('The total number of open switches:', len(set(Loadbreak)))
        # print(timestamp, set(Loadbreak))

        open_sw = []
        for l in Loadbreak:
            for line in self.LineData:
                if line['line'] == l:
                    open_sw.append(line['index'])
                    break
        
        return open_sw