# -------------------------------------------------------------------------------
# Copyright (c) 2017, Battelle Memorial Institute All rights reserved.
# Battelle Memorial Institute (hereinafter Battelle) hereby grants permission to any person or entity
# lawfully obtaining a copy of this software and associated documentation files (hereinafter the
# Software) to redistribute and use the Software in source and binary forms, with or without modification.
# Such person or entity may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and may permit others to do so, subject to the following conditions:
# Redistributions of source code must retain the above copyright notice, this list of conditions and the
# following disclaimers.
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials provided with the distribution.
# Other than as used herein, neither the name Battelle Memorial Institute or Battelle may be used in any
# form whatsoever without the express written consent of Battelle.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# BATTELLE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# General disclaimer for use with OSS licenses
#
# This material was prepared as an account of work sponsored by an agency of the United States Government.
# Neither the United States Government nor the United States Department of Energy, nor Battelle, nor any
# of their employees, nor any jurisdiction or organization that has cooperated in the development of these
# materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for
# the accuracy, completeness, or usefulness or any information, apparatus, product, software, or process
# disclosed, or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer,
# or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United
# States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by BATTELLE for the
# UNITED STATES DEPARTMENT OF ENERGY under Contract DE-AC05-76RL01830
# -------------------------------------------------------------------------------
"""
Created on Jan 19, 2018

@author: Craig Allwardt
"""

__version__ = "0.0.8"

import argparse
import json
import logging
import sys
import time
from get_load import PowerData
from OptimizationVVO import WSUVVO
# from mrid_map import SW_MRID
from legacy_dev_status import LEGACY_DEV
from model_query import MODEL_EQ


from gridappsd import GridAPPSD, DifferenceBuilder, utils, GOSS, topics
from gridappsd.topics import simulation_input_topic, simulation_output_topic, simulation_log_topic, simulation_output_topic

DEFAULT_MESSAGE_PERIOD = 5
message_period = 5

logging.getLogger('stomp.py').setLevel(logging.ERROR)

_log = logging.getLogger(__name__)


class SwitchingActions(object):
    """ A simple class that handles publishing forward and reverse differences

    The object should be used as a callback from a GridAPPSD object so that the
    on_message function will get called each time a message from the simulator.  During
    the execution of on_meessage the `CapacitorToggler` object will publish a
    message to the simulation_input_topic with the forward and reverse difference specified.
    """

    def __init__(self, simulation_id, gridappsd_obj, reg_list, cap_list,  demand, line, xfmr,msr_mrids_demand):
       
        """ Create a ``CapacitorToggler`` object

        This object should be used as a subscription callback from a ``GridAPPSD``
        object.  This class will toggle the capacitors passed to the constructor
        off and on every five messages that are received on the ``fncs_output_topic``.

        Note
        ----
        This class does not subscribe only publishes.

        Parameters
        ----------
        simulation_id: str
            The simulation_id to use for publishing to a topic.
        gridappsd_obj: GridAPPSD
            An instatiated object that is connected to the gridappsd message bus
            usually this should be the same object which subscribes, but that
            isn't required.
        capacitor_list: list(str)
            A list of capacitors mrids to turn on/off
        """
        self._gapps = gridappsd_obj
        self._flag = 0
        # self._Isolate = False
        # self._Restoration = False
        # self.reg_list = reg_list[1:]
        self.reg_list = reg_list
        self._cap_list = cap_list
        self._store = []
        self._message_count = 0
        self._last_toggle_on = False
        self._open_diff = DifferenceBuilder(simulation_id)
        self._close_diff = DifferenceBuilder(simulation_id)
        self._publish_to_topic = simulation_input_topic(simulation_id)
        # self.msr_mrids_loadsw = msr_mrids_loadsw
        self.msr_mrids_demand = msr_mrids_demand
        # self.msr_mrids_cap = msr_mrids_cap
        # self.msr_mrids_reg = msr_mrids_reg
        self.LineData = line
        self.DemandData  = demand
        self.xfmr  = xfmr
        self.TOP = []
        _log.info("Building cappacitor list")

        
    def on_message(self, headers, message):
        """ Handle incoming messages on the simulation_output_topic for the simulation_id

        Parameters
        ----------
        headers: dict
            A dictionary of headers that could be used to determine topic of origin and
            other attributes.
        message: object
            A data structure following the protocol defined in the message structure
            of ``GridAPPSD``.  Most message payloads will be serialized dictionaries, but that is
            not a requirement.
        """
        if 'gridappsd-alarms' in headers['destination']:
            message = json.loads(message.replace("\'",""))
            for m in message:
                print(m['created_by']), m['equipment_name']
            # print(s)

        else:
            self._message_count += 1
            flag_fault = 0
            flag_event = 0

            if self._message_count % message_period == 0:
                print(self.reg_list)
                # calling VVO
                d = PowerData(self.msr_mrids_demand,message)
                platformload = d.demand()
                print('Platform Load is obtained....')
                capreg_st = WSUVVO()
                statusO_c, statusO_r = capreg_st.VVO9500(self.LineData, platformload)
                print('\n \n ........................')
                print('Optimization results')
                print( 'capacitor switch status', statusO_c,)
                print( 'regulator tap position', statusO_r)
                print('........................\n \n')

                # total number of control variables are 18
                ch = []
                for m in range(18):
                    if statusO_c[m] == 0:
                        ch.append(self._cap_list[m])
                no_opt = LEGACY_DEV(self.msr_mrids_cap,self.msr_mrids_reg, message) 
                statusP_c = no_opt.cap_()
                statusP_r = no_opt.reg_()
                print('\n \n ........................')
                print('Platform Status')
                print('capacitor switch status', statusP_c)            
                print('regulator tap position' , statusP_r)
                print('........................\n \n')

                for cap_mrid in ch:
                    self._close_diff.add_difference(cap_mrid, "ShuntCompensator.sections", 0, 1)
                    msg = self._close_diff.get_message()
                    self._gapps.send(self._publish_to_topic, json.dumps(msg))

                ind = 0
                for reg_mrid in self.reg_list:
                    self._close_diff.add_difference(reg_mrid, "TapChanger.step", statusO_r[ind], 0)
                    ind += 1
                    msg = self._close_diff.get_message()
                    self._gapps.send(self._publish_to_topic, json.dumps(msg))


def _main():
    _log.debug("Starting application")
    print("Application starting-------------------------------------------------------")
    global message_period
    parser = argparse.ArgumentParser()
    parser.add_argument("simulation_id",
                        help="Simulation id to use for responses on the message bus.")
    parser.add_argument("request",
                        help="Simulation Request")
    parser.add_argument("--message_period",
                        help="How often the sample app will send open/close capacitor message.",
                        default=DEFAULT_MESSAGE_PERIOD)

    #
    opts = parser.parse_args()
    listening_to_topic = simulation_output_topic(opts.simulation_id)
    print(listening_to_topic)
    message_period = int(opts.message_period)
    sim_request = json.loads(opts.request.replace("\'",""))
    model_mrid = sim_request["power_system_config"]["Line_name"]
    print("\n \n The model running is 9500 node with MRID:")
    print(model_mrid)
         

    _log.debug("Model mrid is: {}".format(model_mrid))
    gapps = GridAPPSD(opts.simulation_id, address=utils.get_gridappsd_address(),
                      username=utils.get_gridappsd_user(), password=utils.get_gridappsd_pass())

    # Get measurement MRIDS for regulators in the feeder
    topic = "goss.gridappsd.process.request.data.powergridmodel"

    # Run queries to get model information
    print('Get Model Information..... \n')   
    query = MODEL_EQ(gapps, model_mrid, topic)
    obj_msr_loadsw, obj_msr_demand = query.meas_mrids()
    print('Get Object MRIDS.... \n')
    switches = query.get_switches_mrids()
    regulator = query.get_regulators_mrids()
    print('regultor is printed')
    capacitor = query.get_capacitors_mrids()
    print('capacitor is printed')
    LoadData, xfmr = query.distLoad()
    query.Inverters()
    sP = 0.
    sQ = 0.
    for l in LoadData:
        sP += float(l['kW'])
        sQ += float(l['kVaR'])       

    print("The Static kW and kVAR of the feeder is:", sP, sQ, "\n")

        # Load Line parameters
    with open('LineData.json', 'r') as read_file:
        line = json.load(read_file)

    print("Initialize..... \n")


    toggler = SwitchingActions(opts.simulation_id, gapps, regulator, capacitor, LoadData, line,xfmr,obj_msr_demand)
    print("Now subscribing")
    gapps.subscribe(listening_to_topic, toggler)
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    _main()
