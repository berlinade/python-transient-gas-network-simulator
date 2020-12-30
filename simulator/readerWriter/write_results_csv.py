'''
    writer for results
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import network_dae
from simulator.readerWriter.read_config_yaml import configuration
from simulator.resources.units import validate_unit

import csv
import numpy as np
from typing import Union, Tuple, List, Optional


vector_t = Union[float, List[float], Tuple[float, ...], np.ndarray]
data_array_t = Union[List[vector_t], Tuple[vector_t, ...], np.ndarray]


def _generate_csv(csv_path : str, net : network_dae, timeTable : data_array_t, solution : data_array_t,
                  write_pressures : bool = True,
                  write_inner_flows : bool = True, write_boundary_flows : bool = True,
                  write_left_right_flows_for_pipes : bool = True):
    with open(csv_path, 'w', newline = '') as result_csv:
        fieldnames = ['Time', 'Alias', 'Object', 'Parameter', 'Value', 'Unit']

        writer = csv.DictWriter(result_csv, fieldnames = fieldnames, delimiter = ';')

        writer.writeheader()

        for ti, solRow in zip(timeTable, solution):
            for element in net.components:
                if 'hidden' in element.type:
                    continue

                if 'node' in element.type:
                    csvRow = {'Time' : ti,
                              'Alias' : element.name,
                              'Object' : element.name,
                              'Parameter' : 'P',
                              'Value' : solRow[element.p_press_id],
                              'Unit' : validate_unit('bar', 'pressure')}

                    if write_pressures: writer.writerow(csvRow)

                    Q = element.qBoundFunc(ti)

                    csvRow = {'Time' : ti,
                              'Alias' : element.name,
                              'Object' : element.name,
                              'Parameter' : 'Q',
                              'Value' : Q,
                              'Unit' : validate_unit('kg_per_s', 'flow')}

                    if write_boundary_flows: writer.writerow(csvRow)

                elif 'pipe' in element.type:
                    if write_left_right_flows_for_pipes:
                        csvRow = {'Time' : ti,
                                  'Alias' : element.name,
                                  'Object' : element.name,
                                  'Parameter' : 'ML',
                                  'Value' : solRow[element.qL_leftFlow_id],
                                  'Unit' : validate_unit('kg_per_s', 'flow')}

                        if write_inner_flows: writer.writerow(csvRow)

                        csvRow = {'Time' : ti,
                                  'Alias' : element.name,
                                  'Object' : element.name,
                                  'Parameter' : 'MR',
                                  'Value' : solRow[element.qR_rightFlow_id],
                                  'Unit' : validate_unit('kg_per_s', 'flow')}

                        if write_inner_flows: writer.writerow(csvRow)
                    else:
                        csvRow = {'Time' : ti,
                                  'Alias' : element.name,
                                  'Object' : element.name,
                                  'Parameter' : 'M',
                                  'Value' : 0.5*(solRow[element.qL_leftFlow_id] + solRow[element.qR_rightFlow_id]),
                                  'Unit' : validate_unit('kg_per_s', 'flow')}

                        if write_inner_flows: writer.writerow(csvRow)
                else:
                    csvRow = {'Time' : ti,
                              'Alias' : element.name,
                              'Object' : element.name,
                              'Parameter' : 'M',
                              'Value' : solRow[element.q_flowThrough_id],
                              'Unit' : validate_unit('kg_per_s', 'flow')}

                    if write_inner_flows: writer.writerow(csvRow)


def generate_csv(config : configuration, net : network_dae, timeTable : data_array_t, solution : data_array_t):
    _generate_csv(csv_path = config.path_out_results_csv,
                  net = net, timeTable = timeTable, solution = solution,
                  write_left_right_flows_for_pipes = config.write_left_right_flows)

    if config.write_pressures:
        _generate_csv(csv_path = config.path_out_results_pressures_csv,
                      net = net, timeTable = timeTable, solution = solution,
                      write_pressures = True,
                      write_inner_flows = False,
                      write_boundary_flows = False,
                      write_left_right_flows_for_pipes = config.write_left_right_flows)

    if config.write_inner_flows:
        _generate_csv(csv_path = config.path_out_results_inner_flows_csv,
                      net = net, timeTable = timeTable, solution = solution,
                      write_pressures = False,
                      write_inner_flows = True,
                      write_boundary_flows = False,
                      write_left_right_flows_for_pipes = config.write_left_right_flows)

    if config.write_boundary_flows:
        _generate_csv(csv_path = config.path_out_results_boundary_flows_csv,
                      net = net, timeTable = timeTable, solution = solution,
                      write_pressures = False,
                      write_inner_flows = False,
                      write_boundary_flows = True,
                      write_left_right_flows_for_pipes = config.write_left_right_flows)
