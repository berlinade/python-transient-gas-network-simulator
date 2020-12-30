'''
    reader for [INI]tial value [C]ondition
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import network_dae, base_edge, node
from simulator.resources.units import pressure_to_bar, flow_to_kilogramm_per_second
from simulator.resources.auxiliary import DimensionError
from simulator.readerWriter.read_config_yaml import configuration

import numpy as np

import csv

from typing import Union, List


def create_inic(net : network_dae, dictInic : Union[List, None] = None,
                deadPressure : float = 50.0, deadPressure_unit : str = 'bar',
                deadFlow : float = 0.0, deadFlow_unit : str = 'kg/s',
                x0 : Union[np.ndarray, None] = None) -> np.ndarray:
    '''
    :param net:
    :param dictInic:
    :param deadPressure: pressure in the dead state [50.0 'bar' is default]
    :param deadPressure_unit:
    :param deadFlow: flow in the dead state [0.0 'kg/s' is default and recommended]
    :param deadFlow_unit:
    :param x0: shape fitting vector to update or None (the latter is default)
    :return:
    '''

    '''
        if no state x0 to update was provided a dead state will be created.
    '''
    deadPressure = pressure_to_bar(deadPressure, deadPressure_unit)
    deadFlow = flow_to_kilogramm_per_second(deadFlow, deadFlow_unit)

    if x0 is None:
        x0 = np.zeros(shape  = (net.dim,))
        for node_types in [net.all_node_types, net.all_hidden_node_types]:
            for node_type in node_types:
                for nodeInstance in net.typeReg[node_type]:
                    x0[nodeInstance.p_press_id] = deadPressure

        for edge_types in [net.all_edge_types, net.all_hidden_edge_types]:
            for edge_type in edge_types:
                for edgeInstance in net.typeReg[edge_type]:
                    x0[edgeInstance.qL_leftFlow_id] = deadFlow
                    x0[edgeInstance.qR_rightFlow_id] = deadFlow
    else:
        if x0.shape[0] != net.dim:
            raise DimensionError("x0 provided doesn't fit dim : {}".format(net.dim))


    '''
        this function can return a dead state if no dictInic is provided. 
        So the following code is executed only if a dictInic was provided
    '''
    if not (dictInic is None):
        # ''' gather norm density '''
        # for dictRow in dictInic:
        #     if dictRow['!'] == '!':
        #         continue
        #
        #     # if dictRow['Object'] == '_SYS' and dictRow['Parameter'] == 'RHO_0':
        #     #     net.gasMix.rho_0 = (float(dictRow['Value']), dictRow['Unit'])

        ''' actually filling out x0 by entries from dictInic (which comes from e.g. a csv) '''
        for dictRow in dictInic:
            if dictRow['!'] == '!':
                continue

            obj   = dictRow['Object']
            param = dictRow['Parameter']
            try:
                val = float(dictRow['Value'])
            except:
                val = dictRow['Value']
            unit  = dictRow['Unit']

            if obj in net.nameReg:
                net_elem_instance : Union[node, base_edge] = net.nameReg[obj]
                if 'node' in net_elem_instance.type:
                    nodeInstance : node = net_elem_instance

                    if param == 'P':
                        x0[nodeInstance.p_press_id] = pressure_to_bar(val, unit)

                elif 'edge' in net_elem_instance.type:
                    edgeInstance : base_edge = net_elem_instance

                    if param == 'M':
                        x0[edgeInstance.qL_leftFlow_id] = flow_to_kilogramm_per_second(val, unit,
                                                                                      density = net.gasMix.rho_0,
                                                                                      density_unit = net.gasMix.rho_0_unit)
                    elif param == 'ML':
                        x0[edgeInstance.qL_leftFlow_id] = flow_to_kilogramm_per_second(val, unit,
                                                                                      density = net.gasMix.rho_0,
                                                                                      density_unit = net.gasMix.rho_0_unit)
                    elif param == 'MR':
                        x0[edgeInstance.qR_rightFlow_id] = flow_to_kilogramm_per_second(val, unit,
                                                                                       density = net.gasMix.rho_0,
                                                                                       density_unit = net.gasMix.rho_0_unit)

        ''' dealing with hidden objects '''
        for edge_type in net.all_hidden_edge_types:
            for edgeInstance in net.typeReg[edge_type]:
                linked_edge : base_edge = net.nameReg[edgeInstance.linked_to]
                if edgeInstance.linked_on == 'left':
                    x0[edgeInstance.qL_leftFlow_id] = x0[linked_edge.qL_leftFlow_id]
                    x0[edgeInstance.qR_rightFlow_id] = x0[linked_edge.qL_leftFlow_id]
                else:
                    x0[edgeInstance.qL_leftFlow_id] = x0[linked_edge.qR_rightFlow_id]
                    x0[edgeInstance.qR_rightFlow_id] = x0[linked_edge.qR_rightFlow_id]

        for node_type in net.all_hidden_node_types:
            for nodeInstance in net.typeReg[node_type]:
                linked_node : node = net.nameReg[nodeInstance.linked_to]
                while hasattr(linked_node, "linked_to"): linked_node = net.nameReg[linked_node.linked_to]
                x0[nodeInstance.p_press_id] = x0[linked_node.p_press_id]

    return x0


def retrieve_inic_csv(config : configuration) -> List:
    with open(config.path_in_inic_csv, mode='r') as eventList:
        eventListRows = csv.DictReader(eventList, delimiter = config.delimiter)

        return list(eventListRows)


''' shortcut '''
def create_inic_csv(net : network_dae, config : configuration,
                    deadPressure : float = 50.0, deadPressure_unit : str = 'bar',
                    deadFlow : float = 0.0, deadFlow_unit : str = 'kg/s',
                    x0 : Union[np.ndarray, None] = None) -> np.ndarray:
    return create_inic(net = net, dictInic = retrieve_inic_csv(config),
                       deadPressure = deadPressure, deadPressure_unit = deadPressure_unit,
                       deadFlow = deadFlow, deadFlow_unit = deadFlow_unit,
                       x0 = x0)
