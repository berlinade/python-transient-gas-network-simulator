'''
    reader for net topology
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import network_dae, base_edge, node

from simulator.resources.auxiliary import NetDescriptionError
from simulator.resources.profiles import table_lookup
from simulator.resources.units import pressure_to_bar, flow_to_kilogramm_per_second

from simulator.gasPhysics.mixtures import gas_mixture
from simulator.gasPhysics.z_factors import z_register, zModel_t
from simulator.gasPhysics.friction_factors import fric_register

from simulator.elements.valve import valve
from simulator.elements.pipeModels import internal_pipe, pipe_models
from simulator.elements.resistorModels import resistor_models
from simulator.elements.activeElementModels.idealActiveUnits import idealCompressor, idealControlValve, _edge_with_target_values
from simulator.elements.specialPassiveElements.checkValve import checkValve

from simulator.readerWriter.read_config_yaml import configuration

from logging import Logger

import yaml

from typing import Tuple


def _topoKeys(edgesPerType : dict) -> Tuple[str, str]:
    leftRightScheme = False
    fromToScheme    = False

    for elementList in edgesPerType.values():
        if not isinstance(elementList, (list, tuple)):
            raise NetDescriptionError("edges within their subgroups (pipe, resistor, ...) have to be lists or tuples!")

        for entry in elementList:
            thereIsLeft = ('left' in entry)
            thereIsTo   = ('to' in entry)

            if thereIsLeft != ('right' in entry): # if there is left, then there has a right to be, too
                raise NetDescriptionError("an edge has a property left but not right!")
            if thereIsTo != ('from' in entry): # if there is a to, then there has a from to be, too
                raise NetDescriptionError("an edge has a property to but not from!")

            if thereIsLeft == thereIsTo: # != acts as exclusive or, i.e. exactly one of the aguments has to true
                raise NetDescriptionError("an edge has both left and from!")

            if thereIsLeft and fromToScheme: # every element has to stick to the same consistent scheme
                raise NetDescriptionError("there are edges having from-to and others have left-right properties!")
            if thereIsTo and leftRightScheme:
                raise NetDescriptionError("there are edges having from-to and others have left-right properties!")

            if thereIsLeft:
                leftRightScheme = True
            else:
                fromToScheme = True

    if leftRightScheme:
        return 'left', 'right'

    return 'from', 'to'

def _retrieveGasMixture(dictInstance : dict) -> gas_mixture:
    return gas_mixture( pc      = dictInstance['pc']['value'],      pc_unit = dictInstance['pc']['unit'],
                        Tc      = dictInstance['Tc']['value'],      Tc_unit = dictInstance['Tc']['unit'],
                        molMass = dictInstance['molMass']['value'], molMass_unit = dictInstance['molMass']['unit'],
                        T       = dictInstance['T']['value'],       T_unit = dictInstance['T']['unit'],
                        rho_0   = dictInstance['rho_0']['value'],   rho_0_unit = dictInstance['rho_0']['unit'])

def _get_gasMix_and_zModel(net, dict_elem):
    try: gasMix = _retrieveGasMixture(dict_elem)
    except KeyError: gasMix = net.gasMix
    try: zModel = z_register[dict_elem['zModel']['value']]
    except KeyError: zModel = net.zModel

    return gasMix, zModel

def _create_hidden_nodes_and_links(orig_left : str, orig_right : str,
                                   name : str,
                                   net : network_dae,
                                   internal_pipe_length_tuple : Tuple[float, str],
                                   internal_pipe_diameter_tuple : Tuple[float, str],
                                   gasMix : gas_mixture, zModel : zModel_t) -> Tuple[str, str]:
    left = "left-hidden-internal-pipe-node" + "|edge-" + name + "|left-node-" + orig_left
    right = "right-hidden-internal-pipe-node" + "|edge-" + name + "|right-node-" + orig_right
    left_pi = "left-hidden-internal-pipe" + "|edge-" + name + "|left-node-" + orig_left
    right_pi = "right-hidden-internal-pipe" + "|edge-" + name + "|right-node-" + orig_right

    left_hidden: node = node(name = left, net = net, _type_prefix="hidden|")
    left_hidden.assign_topo_info(behaviour = 1,
                                 height_inTuple = (net.nameReg[orig_left].height, 'm'))
    left_hidden.linked_to = orig_left # create new field (nodes usually don't have) here
    left_hidden.linked_on = "left" # create new field (nodes usually don't have) here

    right_hidden: node = node(name = right, net = net, _type_prefix = "hidden|")
    right_hidden.assign_topo_info(behaviour = 1,
                                  height_inTuple = (net.nameReg[orig_right].height, 'm'))
    right_hidden.linked_to = orig_right # create new field (nodes usually don't have) here
    right_hidden.linked_on = "right" # create new field (nodes usually don't have) here

    hidden_pipe_left: base_edge = internal_pipe(name = left_pi, net = net,
                                                left = (orig_left, 1), right = (left, 1))
    hidden_pipe_left.assign_topo_info(gasMix = gasMix,
                                      zModel = zModel,
                                      length_inTuple = internal_pipe_length_tuple,
                                      diameter_inTuple = internal_pipe_diameter_tuple)
    hidden_pipe_left.linked_to = name # create new field (edges usually don't have) here
    hidden_pipe_left.linked_on = 'left' # create new field (edges usually don't have) here

    hidden_pipe_right: base_edge = internal_pipe(name = right_pi, net = net,
                                                 left = (right, 1), right = (orig_right, 1))
    hidden_pipe_right.assign_topo_info(gasMix = gasMix,
                                       zModel = zModel,
                                       length_inTuple = internal_pipe_length_tuple,
                                       diameter_inTuple = internal_pipe_diameter_tuple)
    hidden_pipe_right.linked_to = name # create new field (edges usually don't have) here
    hidden_pipe_right.linked_on = 'right' # create new field (edges usually don't have) here

    return left, right

def _create_hidden_nodes_and_resistors(orig_left : str, orig_right : str,
                                       name : str,
                                       net : network_dae,
                                       dict_elem : dict,
                                       dictTopo : dict,
                                       gasMix : gas_mixture, zModel : zModel_t) -> Tuple[str, str]:
    try:
        dragFactorLeft = dict_elem.get('dragFactorIn', {'value' : 0.0})['value']
        dragFactorRight = dict_elem.get('dragFactorOut', {'value' : 0.0})['value']
        if (dragFactorLeft > 0.0) or (dragFactorRight > 0.0):
            diameterTuple = (dict_elem['diameter']['value'], dict_elem['diameter']['unit'])
        else: diameterTuple = tuple()
    except KeyError:
        raise NetDescriptionError("<arc: {}> has either no value or unit for length or dragFactor!".format(name))

    try: resiModelTag = dict_elem['pModel']['value']
    except KeyError: resiModelTag = dictTopo['pModel']
    try: resiModel = resistor_models[resiModelTag]  # resiModelTag in ['box', 'LR', 'mid']
    except KeyError: raise NetDescriptionError("<arc: {}> could not recognize resistor model".format(name))

    if dragFactorLeft > 0.0:
        left = "left-hidden-from-resistor-node" + "|edge-" + name + "|left-node-" + orig_left
        left_re = "left-hidden-from-resistor" + "|edge-" + name + "|left-node-" + orig_left

        left_hidden: node = node(name = left, net = net, _type_prefix = "hidden|")
        left_hidden.assign_topo_info(behaviour = 1,
                                     height_inTuple = (net.nameReg[orig_left].height, 'm'))
        left_hidden.linked_to = orig_left  # create new field (nodes usually don't have) here
        left_hidden.linked_on = "left"  # create new field (nodes usually don't have) here

        resiLeft : base_edge = resiModel(name = left_re, net = net,
                                         left = (orig_left, 1),
                                         right = (left, 1),
                                         _type_prefix = "hidden|")

        resiLeft.assign_topo_info(gasMix = gasMix,
                                  zModel = zModel,
                                  diameter_inTuple = diameterTuple,
                                  drag_factor = dragFactorLeft)

        resiLeft.linked_to = name # create new field (edges usually don't have) here
        resiLeft.linked_on = "left" # create new field (edges usually don't have) here
    else: left = orig_left

    if dragFactorRight > 0.0:
        right = "right-hidden-to-resistor-node" + "|edge-" + name + "|right-node-" + orig_right
        right_re = "right-hidden-to-resistor" + "|edge-" + name + "|right-node-" + orig_right

        right_hidden: node = node(name = right, net = net, _type_prefix = "hidden|")
        right_hidden.assign_topo_info(behaviour = 1,
                                      height_inTuple = (net.nameReg[orig_right].height, 'm'))
        right_hidden.linked_to = orig_right # create new field (nodes usually don't have) here
        right_hidden.linked_on = "right" # create new field (nodes usually don't have) here

        resiRight : base_edge = resiModel(name = right_re, net = net,
                                          left = (right, 1),
                                          right = (orig_right, 1),
                                          _type_prefix = "hidden|")

        resiRight.assign_topo_info(gasMix = gasMix,
                                   zModel = zModel,
                                   diameter_inTuple = diameterTuple,
                                   drag_factor = dragFactorRight)

        resiRight.linked_to = name # create new field (edges usually don't have) here
        resiRight.linked_on = "right" # create new field (edges usually don't have) here
    else: right = orig_right

    return left, right

def _override_internal_pipe_tuple(obj_name : str, config : configuration,
                                  internal_pipe_length_tuple : Tuple[float, str],
                                  internal_pipe_diameter_tuple : Tuple[float, str]):
    ''' active elements '''
    for key, val in config.raw.items():
        if ("internal_pipe" in key) and (obj_name in key):
            internal_pipe_length_tuple = val['length'], val['length_unit']
            internal_pipe_diameter_tuple = val['diameter'], val['diameter_unit']

    return (internal_pipe_length_tuple,
            internal_pipe_diameter_tuple)

def _lock_target_values(element : _edge_with_target_values, config : configuration):
    element_partial_type = None
    for potential_element_type in ['control-valve', 'compressor']:
        if potential_element_type in element.type:
            element_partial_type = potential_element_type
    if element_partial_type is None:
        raise NetDescriptionError("target values can be locked for edge-types in ['compressor', 'control-valve']!")

    target_values_to_lock = None

    # if 'deactivate_target_values' in config.raw:
    for key, val in config.raw.items():
        if ('deactivate_target_values' in key):
            if (element_partial_type in key) and (target_values_to_lock is None):
                target_values_to_lock = val
            elif (element.name in key):
                target_values_to_lock = val

    if not (target_values_to_lock is None):
        if target_values_to_lock['target_upper_pR'] in ["off", "None", None, 0, "0", "deactivate"]:
            element.target_upper_pR = table_lookup([-1.0], [pressure_to_bar(1000.0, 'bar')])
            element.target_upper_pR_locked = True
        if target_values_to_lock['target_lower_pR'] in ["off", "None", None, 0, "0", "deactivate"]:
            element.target_lower_pR = table_lookup([-1.0], [pressure_to_bar(0.0, 'bar')])
            element.target_lower_pR_locked = True
        if target_values_to_lock['target_upper_pL'] in ["off", "None", None, 0, "0", "deactivate"]:
            element.target_upper_pL = table_lookup([-1.0], [pressure_to_bar(1000.0, 'bar')])
            element.target_upper_pL_locked = True
        if target_values_to_lock['target_lower_pL'] in ["off", "None", None, 0, "0", "deactivate"]:
            element.target_lower_pL = table_lookup([-1.0], [pressure_to_bar(0.0, 'bar')])
            element.target_lower_pL_locked = True
        if target_values_to_lock['target_q'] in ["off", "None", None, 0, "0", "deactivate"]:
            if element_partial_type == 'control-valve':
                element.target_q = table_lookup([-1.0], [flow_to_kilogramm_per_second(10000.0, 'kg/s')])
            else:
                element.target_q = table_lookup([-1.0], [flow_to_kilogramm_per_second(0.0, 'kg/s')])
            element.target_q_locked = True
        if target_values_to_lock['use_bypass_instead_of_active']:
            element.by_io_func = table_lookup([-1.0], [1.0])
            element.by_io_func_locked = True

def _deprecation_alias_checks(dict_instance : dict,
                              logger : Logger,
                              do_log : bool) -> bool:
    """
        dealing with deprecations and aliases
    """

    if "model" in dict_instance:
        dict_instance["pModel"] = dict_instance["model"]
        if not do_log:
            logger.warning("NetDescriptionWarning - used deprecated 'model'-tag in *.net.yaml instead of 'pipeModel'")
            pulled_deprecation_warning_pModel_tag_already = True
        del dict_instance["model"]
    if "edgeModel" in dict_instance: dict_instance["pModel"] = dict_instance["edgeModel"]
    if "arcModel" in dict_instance: dict_instance["pModel"] = dict_instance["arcModel"]
    if "resistorModel" in dict_instance: dict_instance["pModel"] = dict_instance["resistorModel"]
    if "pipeModel" in dict_instance: dict_instance["pModel"] = dict_instance["pipeModel"]
    if "fModel" in dict_instance: dict_instance["frictionModel"] = dict_instance["fModel"]
    if "compressibilityFactorModel" in dict_instance: dict_instance["zModel"] = dict_instance["compressibilityFactorModel"]

    return do_log

def create_net(dictTopo : dict, config : configuration, logger : Logger) -> network_dae:
    '''
        :param dictTopo:
        :param config:
        :return:
    '''

    '''
        defining additional params for active elements
    '''
    try: internal_pipe_confg_vlv = config.raw['internal_pipes_common-valve']
    except KeyError: internal_pipe_confg_vlv = config.raw['internal_pipes']
    internal_pipe_vlv_length_tuple = (internal_pipe_confg_vlv['length'], internal_pipe_confg_vlv['length_unit'])
    internal_pipe_vlv_diameter_tuple = (internal_pipe_confg_vlv['diameter'], internal_pipe_confg_vlv['diameter_unit'])

    try: internal_pipe_confg_cvlv = config.raw['internal_pipes_control-valve']
    except KeyError: internal_pipe_confg_cvlv = config.raw['internal_pipes']
    internal_pipe_cvlv_length_tuple = (internal_pipe_confg_cvlv['length'], internal_pipe_confg_cvlv['length_unit'])
    internal_pipe_cvlv_diameter_tuple = (internal_pipe_confg_cvlv['diameter'], internal_pipe_confg_cvlv['diameter_unit'])

    try: internal_pipe_confg_cu = config.raw['internal_pipes_compressor']
    except KeyError: internal_pipe_confg_cu = config.raw['internal_pipes']
    internal_pipe_cu_length_tuple = (internal_pipe_confg_cu['length'], internal_pipe_confg_cu['length_unit'])
    internal_pipe_cu_diameter_tuple = (internal_pipe_confg_cu['diameter'], internal_pipe_confg_cu['diameter_unit'])

    try: internal_pipe_confg_ch = config.raw['internal_pipes_check-valve']
    except KeyError: internal_pipe_confg_ch = config.raw['internal_pipes']
    internal_pipe_ch_length_tuple = (internal_pipe_confg_ch['length'], internal_pipe_confg_ch['length_unit'])
    internal_pipe_ch_diameter_tuple = (internal_pipe_confg_ch['diameter'], internal_pipe_confg_ch['diameter_unit'])

    try: internal_pipe_confg_sp = config.raw['internal_pipes_short-pipe']
    except KeyError: internal_pipe_confg_sp = config.raw['internal_pipes']
    internal_pipe_sp_length_tuple = (internal_pipe_confg_sp['length'], internal_pipe_confg_sp['length_unit'])
    internal_pipe_sp_diameter_tuple = (internal_pipe_confg_sp['diameter'], internal_pipe_confg_sp['diameter_unit'])


    '''
        basic checks
    '''
    net = network_dae(name = dictTopo.get('name', 'generic'))

    pulled_deprecation_warning_pModel_tag_already = False

    pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictTopo,
                                                                              logger = logger,
                                                                              do_log = pulled_deprecation_warning_pModel_tag_already)

    try: net.gasMix = _retrieveGasMixture(dictTopo)
    except KeyError: raise NetDescriptionError("there was no general proper gasMix description for the net itself!")
    try: net.zModel = z_register[dictTopo['zModel']]
    except KeyError: raise NetDescriptionError("there was no zModel declared for the net itself!")
    try: net.fModel = fric_register[dictTopo['frictionModel']]
    except KeyError: raise NetDescriptionError("there was no friction Model declared for the net itself!")

    try: edgesPerType = dictTopo['arcsPerType']
    except KeyError: raise NetDescriptionError("'arcsPerType' was missing in dictTopo")
    try: nodesPerType = dictTopo['nodesPerType']
    except KeyError: raise NetDescriptionError("'nodesPerType' was missing in dictTopo")


    '''
        preprocessing nodes
    '''
    dictSources   = nodesPerType.get('source', [])
    dictInnodes   = nodesPerType.get('innode', [])
    dictSinks     = nodesPerType.get('sink', [])

    for dictnodes in [dictSources, dictInnodes, dictSinks]:
        for dictnode in dictnodes:
            nodeInstance : node = node(dictnode['id']['value'], net = net, dim = 1)

            nodeInstance.assign_topo_info(height_inTuple = (dictnode['height']['value'], dictnode['height']['unit']),
                                          coor = (dictnode['x']['value'], dictnode['y']['value']))


    '''
        create all edges
    '''
    left, right = _topoKeys(edgesPerType)

    dictPipes  = edgesPerType.get('pipe', [])
    dictRstrs  = edgesPerType.get('resistor', [])
    dictVlvs   = edgesPerType.get('valve', [])
    dictcvlvs  = edgesPerType.get('controlValve', [])
    dictCUs    = edgesPerType.get('compressor', [])
    dictChecks = edgesPerType.get('checkValve', [])
    dictshorts = edgesPerType.get('shortPipe', []) # primarily for meteringStation

    ''' Pipes '''
    for dictPipe in dictPipes:
        pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictPipe,
                                                                                  logger = logger,
                                                                                  do_log = pulled_deprecation_warning_pModel_tag_already)

        ''' actual pipe generation '''
        try: pipeName = dictPipe['id']['value']
        except KeyError: raise NetDescriptionError('pipe has no id/name!')
        try: pipeModelTag = dictPipe['pModel']['value']
        except KeyError: pipeModelTag = dictTopo['pModel']
        try: pipeModel = pipe_models[pipeModelTag]  # pipeModelTag in ['box', 'LR', 'mid']
        except KeyError: raise NetDescriptionError("<pipe: {}> could not recognize pipe model".format(pipeName))

        pipeInstance : base_edge = pipeModel(name = pipeName, net = net,
                                             left = (dictPipe[left]['value'], 1),
                                             right = (dictPipe[right]['value'], 1))

        pipeGasMix, pipeZModel = _get_gasMix_and_zModel(net, dictPipe)
        try: pipeFricModel = fric_register[dictPipe['frictionModel']['value']]
        except KeyError: pipeFricModel = net.fModel
        try:
            pipeLengthTuple = (dictPipe['length']['value'], dictPipe['length']['unit'])
            pipeRoughTuple = (dictPipe['roughness']['value'], dictPipe['roughness']['unit'])
            pipeDiameterTuple = (dictPipe['diameter']['value'], dictPipe['diameter']['unit'])
        except KeyError: raise NetDescriptionError("<pipe: {}> has either no value or unit for length, roughness or diameter!".format(pipeName))

        pipeInstance.assign_topo_info(gasMix = pipeGasMix,
                                      fModel = pipeFricModel,
                                      zModel = pipeZModel,
                                      length_inTuple = pipeLengthTuple,
                                      diameter_inTuple = pipeDiameterTuple,
                                      roughness_inTuple = pipeRoughTuple)

    ''' Resistors '''
    for dictResi in dictRstrs:
        pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictResi,
                                                                                  logger = logger,
                                                                                  do_log = pulled_deprecation_warning_pModel_tag_already)

        try: resiName = dictResi['id']['value']
        except KeyError: raise NetDescriptionError('resistor has no id/name!')
        try: resiModelTag = dictResi['pModel']['val']
        except KeyError: resiModelTag = dictTopo['pModel']
        try: resiModel = resistor_models[resiModelTag]  # resiModelTag in ['box', 'LR', 'mid']
        except KeyError: raise NetDescriptionError("<resistor: {}> could not recognize resistor model".format(resiName))

        resiInstance : base_edge = resiModel(name = resiName, net = net,
                                             left = (dictResi[left]['value'], 1),
                                             right = (dictResi[right]['value'], 1))

        resiGasMix, resiZModel = _get_gasMix_and_zModel(net, dictResi)
        try:
            resiDiameterTuple = (dictResi['diameter']['value'], dictResi['diameter']['unit'])
            resiDragFactor = dictResi['dragFactor']['value']
        except KeyError: raise NetDescriptionError("<resistor: {}> has either no value or unit for length or dragFactor!".format(resiName))

        resiInstance.assign_topo_info(gasMix = resiGasMix,
                                      zModel = resiZModel,
                                      diameter_inTuple = resiDiameterTuple,
                                      drag_factor = resiDragFactor)

    ''' Valves '''
    for dictVlv in dictVlvs:
        try: vlvName = dictVlv['id']['value']
        except KeyError: raise NetDescriptionError('valve has no id/name!')

        (internal_length, internal_diam) = _override_internal_pipe_tuple(vlvName, config,
                                                                         internal_pipe_vlv_length_tuple,
                                                                         internal_pipe_vlv_diameter_tuple)

        vlv_left : str = dictVlv[left]['value']
        vlv_right : str = dictVlv[right]['value']
        vlv_gasMix, vlv_zModel = _get_gasMix_and_zModel(net, dictVlv)
        if (internal_length[0] > 0.0) and (internal_diam[0] > 0.0):
            vlv_left, vlv_right = _create_hidden_nodes_and_links(orig_left = vlv_left, orig_right = vlv_right,
                                                                 name = vlvName, net = net,
                                                                 internal_pipe_length_tuple = internal_length,
                                                                 internal_pipe_diameter_tuple = internal_diam,
                                                                 gasMix = vlv_gasMix, zModel = vlv_zModel)
        vlvInstance : base_edge = valve(name = vlvName, net = net,
                                        left = (vlv_left, 1), right = (vlv_right, 1))
        vlvInstance.trueLeft, vlvInstance.trueRight = dictVlv[left]['value'], dictVlv[right]['value']

    ''' short pipes '''
    for dictshort in dictshorts:
        pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictshort,
                                                                                  logger = logger,
                                                                                  do_log = pulled_deprecation_warning_pModel_tag_already)

        try: shortName = dictshort['id']['value']
        except KeyError: raise NetDescriptionError('short-pipe has no id/name!')

        (internal_length, internal_diam) = _override_internal_pipe_tuple(shortName, config,
                                                                         internal_pipe_sp_length_tuple,
                                                                         internal_pipe_sp_diameter_tuple)

        sp_left : str = dictshort[left]['value']
        sp_right : str = dictshort[right]['value']
        sp_gasMix, sp_zModel = _get_gasMix_and_zModel(net, dictshort)
        if (internal_length[0] > 0.0) and (internal_diam[0] > 0.0):
            sp_left, sp_right = _create_hidden_nodes_and_links(orig_left = sp_left, orig_right = sp_right,
                                                               name = shortName, net = net,
                                                               internal_pipe_length_tuple = internal_length,
                                                               internal_pipe_diameter_tuple = internal_diam,
                                                               gasMix = sp_gasMix, zModel = sp_zModel)
        sp_left, sp_right = _create_hidden_nodes_and_resistors(orig_left = sp_left, orig_right = sp_right,
                                                               name = shortName, net = net,
                                                               dict_elem = dictshort,
                                                               dictTopo = dictTopo,
                                                               gasMix = sp_gasMix, zModel = sp_zModel)
        shortInstance : base_edge = valve(name = shortName, net = net,
                                          left = (sp_left, 1), right = (sp_right, 1))
        shortInstance.trueLeft, shortInstance.trueRight = dictshort[left]['value'], dictshort[right]['value']

    ''' Control Valves and/or ideal control valve units '''
    for dictcvlv in dictcvlvs:
        pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictcvlv,
                                                                                  logger = logger,
                                                                                  do_log = pulled_deprecation_warning_pModel_tag_already)

        try: cvlvName = dictcvlv['id']['value']
        except KeyError: raise NetDescriptionError('control valve has no id/name!')

        (internal_length, internal_diam) = _override_internal_pipe_tuple(cvlvName, config,
                                                                         internal_pipe_cvlv_length_tuple,
                                                                         internal_pipe_cvlv_diameter_tuple)

        cvlv_left : str = dictcvlv[left]['value']
        cvlv_right : str = dictcvlv[right]['value']
        cvlv_gasMix, cvlv_zModel = _get_gasMix_and_zModel(net, dictcvlv)
        if (internal_length[0] > 0.0) and (internal_diam[0] > 0.0):
            cvlv_left, cvlv_right = _create_hidden_nodes_and_links(orig_left = cvlv_left, orig_right = cvlv_right,
                                                                   name = cvlvName, net = net,
                                                                   internal_pipe_length_tuple = internal_length,
                                                                   internal_pipe_diameter_tuple = internal_diam,
                                                                   gasMix = cvlv_gasMix, zModel = cvlv_zModel)
        cvlv_left, cvlv_right = _create_hidden_nodes_and_resistors(orig_left = cvlv_left, orig_right = cvlv_right,
                                                                   name = cvlvName, net = net,
                                                                   dict_elem = dictcvlv,
                                                                   dictTopo = dictTopo,
                                                                   gasMix = cvlv_gasMix, zModel = cvlv_zModel)
        cvlvInstance : idealControlValve = idealControlValve(name = cvlvName, net = net,
                                                             left = (cvlv_left, 1), right = (cvlv_right, 1))
        _lock_target_values(element = cvlvInstance, config = config)
        cvlvInstance.trueLeft, cvlvInstance.trueRight = dictcvlv[left]['value'], dictcvlv[right]['value']

    ''' Compressor Stations and/or ideal compressing units '''
    for dictCU in dictCUs:
        pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictCU,
                                                                                  logger = logger,
                                                                                  do_log = pulled_deprecation_warning_pModel_tag_already)

        try: cuName = dictCU['id']['value']
        except KeyError: raise NetDescriptionError('compressor has no id/name!')

        (internal_length, internal_diam) = _override_internal_pipe_tuple(cuName, config,
                                                                         internal_pipe_cu_length_tuple,
                                                                         internal_pipe_cu_diameter_tuple)

        cu_left : str = dictCU[left]['value']
        cu_right : str = dictCU[right]['value']
        cu_gasMix, cu_zModel = _get_gasMix_and_zModel(net, dictCU)
        if (internal_length[0] > 0.0) and (internal_diam[0] > 0.0):
            cu_left, cu_right = _create_hidden_nodes_and_links(orig_left = cu_left, orig_right = cu_right,
                                                               name = cuName, net = net,
                                                               internal_pipe_length_tuple = internal_length,
                                                               internal_pipe_diameter_tuple = internal_diam,
                                                               gasMix = cu_gasMix, zModel = cu_zModel)
        cu_left, cu_right = _create_hidden_nodes_and_resistors(orig_left = cu_left, orig_right = cu_right,
                                                               name = cuName, net = net,
                                                               dict_elem = dictCU,
                                                               dictTopo = dictTopo,
                                                               gasMix = cu_gasMix, zModel = cu_zModel)
        cuInstance : idealCompressor = idealCompressor(name = cuName, net = net,
                                                       left = (cu_left, 1), right = (cu_right, 1))
        _lock_target_values(element = cuInstance, config = config)
        cuInstance.trueLeft, cuInstance.trueRight = dictCU[left]['value'], dictCU[right]['value']

    ''' check Valves '''
    for dictCheck in dictChecks:
        pulled_deprecation_warning_pModel_tag_already = _deprecation_alias_checks(dict_instance = dictCheck,
                                                                                  logger = logger,
                                                                                  do_log = pulled_deprecation_warning_pModel_tag_already)

        try: checkName = dictCheck['id']['value']
        except KeyError: raise NetDescriptionError('check valve has no id/name!')

        (internal_length, internal_diam) = _override_internal_pipe_tuple(checkName, config,
                                                                         internal_pipe_ch_length_tuple,
                                                                         internal_pipe_ch_diameter_tuple)

        ch_left : str = dictCheck[left]['value']
        ch_right : str = dictCheck[right]['value']
        ch_gasMix, ch_zModel = _get_gasMix_and_zModel(net, dictCheck)
        if (internal_length[0] > 0.0) and (internal_diam[0] > 0.0):
            ch_left, ch_right = _create_hidden_nodes_and_links(orig_left = ch_left, orig_right = ch_right,
                                                               name = checkName, net = net,
                                                               internal_pipe_length_tuple = internal_length,
                                                               internal_pipe_diameter_tuple = internal_diam,
                                                               gasMix = ch_gasMix, zModel = ch_zModel)
        ch_left, ch_right = _create_hidden_nodes_and_resistors(orig_left = ch_left, orig_right = ch_right,
                                                               name = checkName, net = net,
                                                               dict_elem = dictCheck,
                                                               dictTopo = dictTopo,
                                                               gasMix = ch_gasMix, zModel = ch_zModel)
        chInstance : base_edge = checkValve(name = checkName, net = net,
                                             left = (ch_left, 1), right = (ch_right, 1))
        chInstance.trueLeft, chInstance.trueRight = dictCheck[left]['value'], dictCheck[right]['value']

    return net


def retrieve_topo_yaml(config : configuration) -> dict:
    with open(config.path_in_net_yaml, mode = 'r') as net_yaml:
        return yaml.load(net_yaml, Loader = yaml.FullLoader)


''' shortcut '''
def create_net_yaml(config : configuration, logger : Logger) -> network_dae:
    return create_net(retrieve_topo_yaml(config), config = config, logger = logger)
