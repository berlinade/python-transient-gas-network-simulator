'''
    reader for simulation scenario
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import network_dae, node, base_edge, base_element
from simulator.resources.units import relative_date_to_sec, flow_to_kilogramm_per_second, \
                                      pressure_to_bar, relative_time_to_sec, speed_to_meter_per_second
from simulator.resources.profiles import table_lookup
from simulator.resources.auxiliary import SceneDescriptionError
from simulator.readerWriter.read_config_yaml import configuration

import csv

from typing import List, Optional, Dict


def retrieve_scene_csv(config : configuration) -> List[Dict[str, str]]:
    with open(config.path_in_scene_csv, mode = 'r') as scene_csv:
        return list(csv.DictReader(scene_csv, delimiter = config.delimiter))


def _convert_time_str_2_float(time_as_str : str) -> float:
    '''
        :param time_as_str:
        :return:
    '''

    time_as_float_tuple : List[float] = [float(entry) for entry in time_as_str.split(':')]

    days, hours, minutes, seconds = 0.0, 0.0, 0.0, 0.0

    if len(time_as_float_tuple) == 1:
        seconds = time_as_float_tuple[0]
    elif len(time_as_float_tuple) == 2:
        hours = time_as_float_tuple[0]
        minutes = time_as_float_tuple[1]
    elif len(time_as_float_tuple) == 3:
        hours = time_as_float_tuple[0]
        minutes = time_as_float_tuple[1]
        seconds = time_as_float_tuple[2]
    elif len(time_as_float_tuple) == 4:
        days = time_as_float_tuple[0]
        hours = time_as_float_tuple[1]
        minutes = time_as_float_tuple[2]
        seconds = time_as_float_tuple[3]
    else:
        err_msg = 'time format not understood: {}!'.format(time_as_str)
        err_msg += 'Expected: Days:hours:minutes:seconds -or- hours:minutes:seconds -or- hours:minutes -or- seconds'
        raise SceneDescriptionError(err_msg)

    return relative_date_to_sec(days, hours, minutes, seconds)

def _append_events(obj : str, out_event_dict : dict, newEntries : dict):
    if not (obj in out_event_dict):
        out_event_dict[obj] = {}

    for key, val in newEntries.items():
        if not (key in out_event_dict[obj]):
            out_event_dict[obj][key] = [val]
        else:
            out_event_dict[obj][key].append(val)

def parse_scene_csv(net : network_dae,
                    in_event_list : List[Dict[str, str]]) -> dict:
    '''
        :param net:
        :param in_event_list:
        :return:
    '''

    out_event_dict = {}

    out_event_dict['_SYS'] = {}
    out_event_dict['_SYS']['CHECKPOINT'] = []
    out_event_dict['_SYS']['ENDOFSIMULATION'] = None
    out_event_dict['_SYS']['DT'] = None

    for dictRow in in_event_list:
        if dictRow['!'] == '!':
            continue

        # if dictRow['Object'] == '_SYS' and dictRow['Parameter'] == 'RHO_0':
        #     rho_0 = net.gasMix.rho_0
        #     net.gasMix.rho_0 = (float(dictRow['Value']), dictRow['Unit'])
        #     if rho_0 != net.gasMix.rho_0:
        #         raise SceneDescriptionError("net {} already had an unequal norm density!".format(str(net)))

    for dictRow in in_event_list:
        if dictRow['!'] == '!':
            continue

        obj   = dictRow['Object']
        param = dictRow['Parameter']
        try: val = float(dictRow['Value'])
        except ValueError: val = dictRow['Value']
        unit  = dictRow['Unit']
        if dictRow['Time'] != '':
            time = _convert_time_str_2_float(dictRow['Time'])

        if obj == '_SYS':
            if param == 'DT':
                out_event_dict[obj][param] = relative_time_to_sec(val, unit)
            if param == 'CHECKPOINT':
                out_event_dict[obj][param].append(time)
            elif param == 'ENDOFSIMULATION':
                if out_event_dict[obj][param] is None:
                    out_event_dict[obj][param] = time
                else:
                    raise SceneDescriptionError("'ENDOFSIMULATION' appeared twice!")
        else:
            try: element : base_element = net.nameReg[obj]
            except KeyError: raise SceneDescriptionError("did not recognize {} as 'Object'from event_list!".format(obj))

            if "node" in element.type:
                if param == 'Q':
                    if (obj in out_event_dict) and ('pset' in out_event_dict[obj]):
                        raise SceneDescriptionError('{} can either be a p_node xor q_node!'.format(str(element)))

                    q_in_out = flow_to_kilogramm_per_second(val, unit, density = net.gasMix.rho_0, density_unit = net.gasMix.rho_0_unit)
                    _append_events(obj, out_event_dict, {'t'         : time,
                                                         'qInOut'    : q_in_out,
                                                         'behaviour' : 1})

                elif param == 'P':
                    if (obj in out_event_dict) and ('qInOut' in out_event_dict[obj]):
                        raise SceneDescriptionError('{} can either be a p_node xor q_node!'.format(str(element)))

                    _append_events(obj, out_event_dict, {'t'         : time,
                                                         'pset'      : pressure_to_bar(val, unit),
                                                         'behaviour' : 0})

            elif ("common-valve" in element.type) and (param in ['ON', 'OFF']):
                _append_events(obj, out_event_dict, {'t'  : time,
                                                     'io' : 1.0 if param != 'OFF' else 0.0})

            elif ("compressor" in element.type) or ("control-valve" in element.type):
                if param == 'OFF':
                    _append_events(obj, out_event_dict, {'t_io' : time,
                                                         'io'   : 0.0})
                    _append_events(obj, out_event_dict, {'t_by_io' : time,
                                                         'by_io'   : 0.0})
                elif param == 'BP': # i.e. 'BYPASS'
                    _append_events(obj, out_event_dict, {'t_io' : time,
                                                         'io'   : 1.0})
                    _append_events(obj, out_event_dict, {'t_by_io' : time,
                                                         'by_io'   : 1.0})
                elif (param == 'CONF') and (val == 'FREE'):
                    _append_events(obj, out_event_dict, {'t_io' : time,
                                                         'io'   : 1.0})
                    _append_events(obj, out_event_dict, {'t_by_io' : time,
                                                         'by_io'   : 0.0})

                elif param == 'TARGET_UPPER_PR':
                    _append_events(obj, out_event_dict, {'t_target_upper_pR': time,
                                                         'target_upper_pR'  : max(0.0, pressure_to_bar(val, unit))})
                elif param == 'TARGET_LOWER_PR':
                    _append_events(obj, out_event_dict, {'t_target_lower_pR': time,
                                                         'target_lower_pR'  : max(0.0, pressure_to_bar(val, unit))})
                elif param == 'TARGET_UPPER_PL':
                    _append_events(obj, out_event_dict, {'t_target_upper_pL' : time,
                                                         'target_upper_pL'   : max(0.0, pressure_to_bar(val, unit))})
                elif param == 'TARGET_LOWER_PL':
                    _append_events(obj, out_event_dict, {'t_target_lower_pL' : time,
                                                         'target_lower_pL'   : max(0.0, pressure_to_bar(val, unit))})
                elif param == 'TARGET_Q':
                    _append_events(obj, out_event_dict, {'t_target_q' : time,
                                                         'target_q'   : max(0.0, flow_to_kilogramm_per_second(val, unit,
                                                                                                              density = net.gasMix.rho_0,
                                                                                                              density_unit = net.gasMix.rho_0_unit))})

    if out_event_dict['_SYS']['ENDOFSIMULATION'] is None:
        raise SceneDescriptionError("There was no 'ENDOFSIMULATION' in in_event_list!")

    return out_event_dict


def _profile_configuration(profile_tag : str, config : configuration, alternate_profile_conf : Optional[dict] = None):
    try:
        profile_conf = {'mode': config.raw[profile_tag]['mode'],
                        'smoothing_offset': relative_time_to_sec(config.raw[profile_tag]['smoothing_offset'],
                                                                 config.raw[profile_tag]['smoothing_offset_unit']),
                        'horizon': (relative_time_to_sec(config.raw[profile_tag]['horizon'][0],
                                                         config.raw[profile_tag]['horizon_unit']),
                                    relative_time_to_sec(config.raw[profile_tag]['horizon'][1],
                                                         config.raw[profile_tag]['horizon_unit']))}
    except KeyError:
        profile_conf = alternate_profile_conf

    return profile_conf

def set_scenario(net : network_dae, event_dict : dict, config : configuration):
    profile_conf = _profile_configuration('profiles_all', config)
    node_profile_conf = _profile_configuration('profiles_node', config, profile_conf)
    vlv_profile_conf = _profile_configuration('profiles_common-valve', config, profile_conf)
    cvlv_profile_conf = _profile_configuration('profiles_control-valve', config, profile_conf)
    cu_profile_conf = _profile_configuration('profiles_compressor', config, profile_conf)

    for obj, obj_events in event_dict.items():
        if obj == "_SYS": continue

        try: element : base_element = net.nameReg[obj]
        except KeyError: raise SceneDescriptionError("did not recognize {} as 'Object' from event_dict!".format(obj))

        obj_profile_conf = None
        for key, val in config.raw.items():
            if ("profiles" in key) and (obj in key):
                obj_profile_conf = _profile_configuration(key, config)

        if 'node' in element.type:
            if obj_profile_conf is None: obj_profile_conf = node_profile_conf

            times = obj_events['t']
            behaviour = obj_events['behaviour'][0]

            element.behaviour = behaviour
            if behaviour == 0:
                pressures = obj_events['pset']
                element.pBoundFunc = table_lookup(times, pressures, **obj_profile_conf)
            elif behaviour == 1:
                in_out_flows = obj_events['qInOut']
                element.qBoundFunc = table_lookup(times, in_out_flows, **obj_profile_conf)
            else:
                raise SceneDescriptionError("behaviour couldn't be determined properly from event_dict")

        elif 'common-valve' in element.type:
            if obj_profile_conf is None: obj_profile_conf = vlv_profile_conf

            times = obj_events['t']
            io = obj_events['io']

            element.io_func = table_lookup(times, io, **obj_profile_conf)

        elif ('control-valve' in element.type) or ('compressor' in element.type):
            if obj_profile_conf is None:
                if 'control-valve' in element.type:
                    obj_profile_conf = cvlv_profile_conf
                else: # ==> 'compressor' in element.type
                    obj_profile_conf = cu_profile_conf

            t_io    = obj_events['t_io']
            io      = obj_events['io']
            element.io_func = table_lookup(t_io, io, **obj_profile_conf)

            t_by_io = obj_events.get('t_by_io', [0.0])
            by_io   = obj_events.get('by_io', [1.0])
            element.by_io_func = table_lookup(t_by_io, by_io, **obj_profile_conf)

            t_target_upper_pR = obj_events.get('t_target_upper_pR', [0.0])
            target_upper_pR   = obj_events.get('target_upper_pR', [pressure_to_bar(1000.0, 'bar')])
            element.target_upper_pR = table_lookup(t_target_upper_pR, target_upper_pR, **obj_profile_conf)

            t_target_lower_pR = obj_events.get('t_target_lower_pR', [0.0])
            target_lower_pR   = obj_events.get('target_lower_pR', [pressure_to_bar(0.0, 'bar')])
            element.target_lower_pR = table_lookup(t_target_lower_pR, target_lower_pR, **obj_profile_conf)

            t_target_upper_pL = obj_events.get('t_target_upper_pL', [0.0])
            target_upper_pL   = obj_events.get('target_upper_pL', [pressure_to_bar(1000.0, 'bar')])
            element.target_upper_pL = table_lookup(t_target_upper_pL, target_upper_pL, **obj_profile_conf)

            t_target_lower_pL = obj_events.get('t_target_lower_pL', [0.0])
            target_lower_pL   = obj_events.get('target_lower_pL', [pressure_to_bar(0.0, 'bar')])
            element.target_lower_pL = table_lookup(t_target_lower_pL, target_lower_pL, **obj_profile_conf)

            t_target_q        = obj_events.get('t_target_q', [0.0])
            target_q          = obj_events.get('target_q', [flow_to_kilogramm_per_second(10000.0, 'kg/s')])
            element.target_q = table_lookup(t_target_q, target_q, **obj_profile_conf)


def set_scenario_csv(net : network_dae, config : configuration) -> dict:
    event_list = retrieve_scene_csv(config = config)
    event_dict = parse_scene_csv(net = net, in_event_list = event_list)
    set_scenario(net = net, event_dict = event_dict, config = config)

    return event_dict


def retrieve_simulator_credentials(event_dict : dict):
    t0 = 0.0
    try: T = event_dict['_SYS']['ENDOFSIMULATION']
    except KeyError: raise SceneDescriptionError("There was no 'ENDOFSIMULATION' in event_dict!")
    try: H = event_dict['_SYS']['DT']
    except KeyError: H = None
    try: userDefinedTimePoints = event_dict['_SYS']['CHECKPOINT']
    except KeyError: userDefinedTimePoints = []

    return t0, T, H, userDefinedTimePoints
