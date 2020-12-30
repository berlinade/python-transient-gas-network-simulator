'''
    simplified interface that calls necessary functions to setup and simulate a gas network instance
'''

__author__ = ('Tom Streubel',) # alphabetical order of surnames
__credits__ = tuple() # alphabetical order of surnames


'''
    imports
    =======
'''
# from simulator.netgraph import network_dae
# from simulator.elements.activeElementModels.idealActiveUnits import _edge_with_target_values

from simulator.readerWriter.read_config_yaml import configuration
from simulator.readerWriter.read_net_yaml import retrieve_topo_yaml, create_net
from simulator.readerWriter.read_inic_csv import retrieve_inic_csv, create_inic
from simulator.readerWriter.read_scene_csv import set_scenario_csv, retrieve_simulator_credentials

from simulator.readerWriter.write_results_csv import generate_csv
from simulator.readerWriter.write_results_meta_yaml import generate_meta_yaml

from simulator.resources.units import relative_time_to_sec #, pressure_to_bar, flow_to_kilogramm_per_second
from simulator.resources.auxiliary import no_logger

from paso.solvers.dae.ImpEuler import integrate, ImpEuler_integration_options

from logging import Logger

from ad.timer import Timer

import numpy as np
import yaml
from typing import Union, Optional, List, Tuple, Dict


def simulate_gas_network(config : Union[configuration, str],
                         logger : Optional[Logger] = None,
                         imp_euler_options : Optional[ImpEuler_integration_options] = None):
    ''' parse configs (if not parsed already) '''
    if isinstance(config, str): config : configuration = configuration(path_config_yaml = config)

    ''' logger treatment '''
    if logger is None: logger = no_logger()

    ''' read and initialize network topology from *.net.yaml '''
    net_dict = retrieve_topo_yaml(config = config)
    net = create_net(dictTopo = net_dict, config = config, logger = logger)

    ''' read and initialize initial value '''
    inic_list = retrieve_inic_csv(config = config)
    x0 = create_inic(net = net, dictInic = inic_list)

    ''' read scenario '''
    event_dict = set_scenario_csv(net = net, config = config)
    t0, T, H, userDefinedTimePoints = retrieve_simulator_credentials(event_dict = event_dict)
    if H is None: H = relative_time_to_sec(3.0, 'min')

    ''' dump extra files (if choosen) - basically to check/or verify for the user "how" the simulator understood inputs so far '''
    if not (config.file_path_dump is None):
        with open(config.file_path_dump + 'x0.yaml', mode = 'w') as x0_dict_out: yaml.dump(x0.tolist(), x0_dict_out)
        with open(config.file_path_dump + 'event_dict.yaml', mode = 'w') as event_dict_out: yaml.dump(event_dict, event_dict_out)

    ''' execute actual simulation '''
    logger.info('start implicit Euler integration from t0 = {} to T = {}, with H = {}'.format(t0, T, H))
    with Timer('<euler instance simulating gas network>', silent_mode = True) as euler_time:
        if imp_euler_options is None: imp_euler_options = ImpEuler_integration_options()
        imp_euler_options.cycADa = True
        imp_euler_report = integrate(net,
                                     x0 = x0, t0 = t0, T = T, h = H,
                                     integrator_opts = imp_euler_options)
        timeTable = imp_euler_report.Ts
        solution = imp_euler_report.Xs
    logger.info('implicit Euler integration from t0 = {} to T = {}, with H = {}, finished'.format(t0, T, H))
    logger.info('{}: {}'.format(euler_time.name, euler_time.time_msg))
    logger.info('{}: {}'.format(euler_time.name, euler_time.clock_msg))

    ''' post processing of results '''
    logger.info('generate results: {}'.format(config.path_out_results_csv))
    generate_csv(config = config, net = net, timeTable = timeTable, solution = solution)
    logger.info('generation of results: {} complete'.format(config.path_out_results_csv))
    if not (config.path_out_results_meta_yaml is None): # meta result contain information abaout states of active  elements
        logger.info('generate extended info on results: {}'.format(config.path_out_results_meta_yaml))
        generate_meta_yaml(config = config, net = net, timeTable = timeTable)
        logger.info('generation of extended info on results: {} complete'.format(config.path_out_results_meta_yaml))
    else: logger.info('DO NOT generate extended info on results according to config')
    logger.info('simulation complete')

    return timeTable, solution, net


# vector_t = Union[Tuple[float, ...], List[float], np.ndarray]


# def _create_target_violation_logger(net : network_dae, config : configuration):
#     log_at_all = False
#
#     for edge_type in net.all_edge_types:
#         parent_type = None
#         if 'control-valve' in edge_type:
#             parent_type = 'control-valve'
#         elif 'compressor' in edge_type:
#             parent_type = 'compressor'
#
#         if not (parent_type is None):
#             edges_of_type : Union[Tuple[_edge_with_target_values, ...], List[_edge_with_target_values]] = net.typeReg[edge_type]
#
#             for edge in edges_of_type:
#                 thresh_press, thresh_flow = None, None
#
#                 if not config.raw['log_target_value_violations']['suppress_log']:
#                     press = config.raw['log_target_value_violations']['pressure']
#                     thresh_press = pressure_to_bar(press['threshold'], press['unit'])
#                     flow = config.raw['log_target_value_violations']['flow']
#                     thresh_flow = flow_to_kilogramm_per_second(flow['threshold'], flow['unit'])
#                     log_at_all = True
#                 if ('log_target_value_violations_' + parent_type) in config.raw:
#                     if not config.raw['log_target_value_violations_' + parent_type]['suppress_log']:
#                         press = config.raw['log_target_value_violations_' + parent_type]['pressure']
#                         thresh_press = pressure_to_bar(press['threshold'], press['unit'])
#                         flow = config.raw['log_target_value_violations_' + parent_type]['flow']
#                         thresh_flow = flow_to_kilogramm_per_second(flow['threshold'], flow['unit'])
#                         log_at_all = True
#                 if ('log_target_value_violations_' + edge.name) in config.raw:
#                     if not config.raw['log_target_value_violations_' + edge.name]['suppress_log']:
#                         press = config.raw['log_target_value_violations_' + edge.name]['pressure']
#                         thresh_press = pressure_to_bar(press['threshold'], press['unit'])
#                         flow = config.raw['log_target_value_violations_' + edge.name]['flow']
#                         thresh_flow = flow_to_kilogramm_per_second(flow['threshold'], flow['unit'])
#                         log_at_all = True
#
#                 if not (thresh_press is None):
#                     edge.log_target_violations = True # this property doesn't exists in base_edge prior to here!
#                     edge.thresh_press = thresh_press # this property doesn't exists in base_edge prior to here!
#                     edge.thresh_flow = thresh_flow # this property doesn't exists in base_edge prior to here!
#
#     if log_at_all:
#         # violations : Dict[str, Dict[str, Dict[str, Dict[float, float]]]] = {'controlValve' : {}, 'compressor' : {}}
#
#         with open(config.file_path_out + config.name_of_instance + ".target_value_violation_log.log", 'w'): pass
#         violations_log = create_prepared_logger(fileName = config.file_path_out + config.name_of_instance + ".target_value_violation_log.log",
#                                                 logToConsole = False, loggerName = "target_value_violations-log")
#         with open(config.file_path_out + config.name_of_instance + ".activeUnits.log", 'w'): pass
#         active_log = create_prepared_logger(fileName = config.file_path_out + config.name_of_instance + ".activeUnits.log",
#                                             logToConsole = False, loggerName = "active-log")
#
#         def _target_value_violation_logging(f :callable, ti : float, xi : vector_t, h : float, tip1 :float,
#                                             currentProgress : float,
#                                             actual_res : float,
#                                             norm_xi : float):
#             for edge_type in net.all_edge_types:
#                 parent_type = None
#                 if 'control-valve' in edge_type:
#                     parent_type = 'controlValve' # <- as in yaml
#                 elif 'compressor' in edge_type:
#                     parent_type = 'compressor'
#
#                 if not (parent_type is None):
#                     edges_of_type: Union[Tuple[_edge_with_target_values, ...], List[_edge_with_target_values]] = net.typeReg[edge_type]
#
#                     for edge in edges_of_type:
#                         if edge.log_target_violations:
#                             # if not edge.name in violations[parent_type]:
#                             #     violations[parent_type][edge.name] : dict = {'pR' : {}, 'pL' : {}, 'q' : {}, 'pR - pL' : {}}
#
#                             pL = xi[edge.pL_leftPress_id]
#                             pR = xi[edge.pR_rightPress_id]
#                             q = xi[edge.q_flowThrough_id]
#
#
#                             io = edge.io_func(ti)
#                             by_io = min(edge.by_io_func(ti), io)
#
#                             bar_pR = edge.target_upper_pR(ti)
#                             ubar_pR = min(bar_pR, edge.target_lower_pR(ti))
#
#                             bar_pL = max(ubar_pR, edge.target_upper_pL(ti))
#                             ubar_pL = min(bar_pL, edge.target_lower_pL(ti))
#
#                             bar_ubar_q = max(0.0, edge.target_q(ti))
#
#
#                             io_future = edge.io_func(ti)
#                             by_io_future = min(edge.by_io_func(ti), io)
#
#                             bar_pR_future = edge.target_upper_pR(ti)
#                             ubar_pR_future = min(bar_pR, edge.target_lower_pR(ti))
#
#                             bar_pL_future = max(ubar_pR, edge.target_upper_pL(ti))
#                             ubar_pL_future = min(bar_pL, edge.target_lower_pL(ti))
#
#                             bar_ubar_q_future = max(0.0, edge.target_q(ti))
#
#
#                             active_log_template = "ti:{} - {}| io[{:.2f}>>{:.2f}]  by_io[{:.2f}>>{:.2f}]  pL[{:.2f}>>{:.2f} | {:.2f} | {:.2f}>>{:.2f}]  pR[{:.2f}>>{:.2f} | {:.2f} | {:.2f}>>{:.2f}]  q[{:.2f} | set: {:.2f}>>{:.2f}]>"
#                             active_log.info(active_log_template.format(ti, str(edge),
#                                                                        io, io_future,
#                                                                        by_io, by_io_future,
#                                                                        ubar_pL, ubar_pL_future, pL, bar_pL,
#                                                                        bar_pL_future,
#                                                                        ubar_pR, ubar_pR_future, pR, bar_pR,
#                                                                        bar_pR_future,
#                                                                        q, bar_ubar_q, bar_ubar_q_future))
#
#                             if (io >= 0.01) and (by_io < 0.01):
#                                 if pL > (bar_pL + edge.thresh_press):
#                                     # violations[parent_type][edge.name]['pL'][float(ti)] = float(pL - bar_pL)
#                                     pass
#                                 elif pL < max(0.0, ubar_pL - edge.thresh_press):
#                                     # violations[parent_type][edge.name]['pL'][float(ti)] = float(pL - ubar_pL)
#                                     violations_log.info("ti:{} - {}|  pL[{} | {} | {}]  pR[{} | {} | {}]  q[{} | target: {}]> msg: left pressure".format(ti, str(edge), ubar_pL, pL, bar_pL, ubar_pR, pR, bar_pR, q, bar_ubar_q))
#
#                                 if pR > (bar_pR + edge.thresh_press):
#                                     # violations[parent_type][edge.name]['pR'][float(ti)] = float(pR - bar_pR)
#                                     violations_log.info("ti:{} - {}|  pL[{} | {} | {}]  pR[{} | {} | {}]  q[{} | target: {}]> msg: right pressure".format(ti, str(edge), ubar_pL, pL, bar_pL, ubar_pR, pR, bar_pR, q, bar_ubar_q))
#                                 elif pR < max(0.0, ubar_pR - edge.thresh_press):
#                                     # violations[parent_type][edge.name]['pR'][float(ti)] = float(pR - ubar_pR)
#                                     pass
#
#                                 if q > (bar_ubar_q + edge.thresh_press):
#                                     # violations[parent_type][edge.name]['q'][float(ti)] = float(q - bar_ubar_q)
#                                     pass
#                                 elif q < max(0.0, bar_ubar_q - edge.thresh_press):
#                                     # violations[parent_type][edge.name]['q'][float(ti)] = float(q - bar_ubar_q)
#                                     pass
#
#                                 if (parent_type == 'controlValve') and ((pR - pL) > edge.thresh_press):
#                                     # violations[parent_type][edge.name]['pR - pL'][float(ti)] = float(pR - pL)
#                                     violations_log.info("ti:{} - {}|  pL[{} | {} | {}]  pR[{} | {} | {}]  q[{} | target: {}]> msg: cv condition".format(ti, str(edge), ubar_pL, pL, bar_pL, ubar_pR, pR, bar_pR, q, bar_ubar_q))
#                                 elif (parent_type == 'compressor') and ((pR - pL) < -edge.thresh_press):
#                                     # violations[parent_type][edge.name]['pR - pL'][float(ti)] = float(pR - pL)
#                                     violations_log.info("ti:{} - {}|  pL[{} | {} | {}]  pR[{} | {} | {}]  q[{} | target: {}]> msg: cs condition".format(ti, str(edge), ubar_pL, pL, bar_pL, ubar_pR, pR, bar_pR, q, bar_ubar_q))
#
#         def _save_target_value_violation_logging():
#             # with open(config.file_path_out + config.name_of_instance + "target_value_violation_log.yaml", mode = 'w') as yaml_log:
#             #     yaml.dump(violations, yaml_log, indent = 4, default_flow_style = None)
#             pass
#
#         return _target_value_violation_logging, _save_target_value_violation_logging, log_at_all
#     return (lambda *args, **kwargs: None), (lambda *args, **kwargs: None), log_at_all
