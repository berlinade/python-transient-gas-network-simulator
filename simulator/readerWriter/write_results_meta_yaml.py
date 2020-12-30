'''
    writer to write out states and configurations of active elements (useful for Viewer)
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import network_dae
from simulator.elements import valve
from simulator.elements.activeElementModels.idealActiveUnits import idealCompressor, idealControlValve
from simulator.readerWriter.read_config_yaml import configuration
from simulator.resources.units import validate_unit, density_to_kilogramm_per_m_cube
from simulator.readerWriter.write_results_csv import data_array_t

import yaml

from typing import Union


def generate_meta_yaml(config : configuration, net : network_dae, timeTable : data_array_t):
    yamlDict = {"name": net.name,
                "rho_0 (norm density)": density_to_kilogramm_per_m_cube(net.gasMix.rho_0,
                                                                        net.gasMix.rho_0_unit),
                "timeTable": [float(ti) for ti in timeTable],
                "valve" : {},
                "controlValve" : {},
                "compressorStation" : {},
                "unit" : {'pressure' : validate_unit('bar', 'pressure'),
                          'flow' : validate_unit('kg/s', 'flow'),
                          'norm density' : validate_unit('kg/m^3', 'density')}}

    for element in net.components:
        if 'common-valve' in element.type: #for vlvInstance in netInstance.topoCookieArcs['vlvs']:
            element : valve = element
            yamlDict["valve"][element.name] = {'opening-states' : [float(element.io_func(ti)) for ti in timeTable]}

        if ('control-valve' in element.type) or ('compressor' in element.type):
            if 'control-valve' in element.type: yaml_type = 'controlValve'
            else: yaml_type = 'compressorStation'

            element : Union[idealCompressor, idealControlValve] = element

            yamlDict[yaml_type][element.name] = {'opening-states' : [float(element.io_func(ti)) for ti in timeTable],
                                                 'bypass-states' : [min(float(element.io_func(ti)),
                                                                        float(element.by_io_func(ti))) for ti in timeTable]}

            for func, funcName in [(element.target_lower_pL, 'p_target_lower_pL'),
                                   (element.target_upper_pL, 'p_target_upper_pL'),
                                   (element.target_lower_pR, 'p_target_lower_pR'),
                                   (element.target_upper_pR, 'p_target_upper_pR'),
                                   (element.target_q, 'q_target_q')]:
                yamlDict[yaml_type][element.name][funcName] = [float(func(ti)) for ti in timeTable]

    with open(config.path_out_results_meta_yaml, 'w') as out_yaml:
        yaml.dump(yamlDict, out_yaml, indent = 4, default_flow_style = None)
