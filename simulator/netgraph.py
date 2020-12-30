'''
    realize graph structure of gas network simulator
'''

__author__ = ('Tom Streubel',) # alphabetical order of surnames
__credits__ = tuple() # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np
from typing import Union, Tuple, Optional, List

from simulator.resources.auxiliary import ModellingError
from simulator.resources.units import length_to_meter, acceleration_to_m_per_s_2, pressure_to_pascal
from simulator.gasPhysics.mixtures import gas_mixture
from simulator.gasPhysics.z_factors import zModel_t
from simulator.gasPhysics.friction_factors import fModel_t


class network_dae(object):

    def __init__(self, name = 'generic'):
        self.name = name

        self.dim  = 0

        self.components : List[Union[node, base_edge]] = []

        self.nameReg = {}
        self.typeReg = {}

        self.all_node_types = [] # without hidden ones
        self.all_hidden_node_types = []

        self.all_edge_types = [] # without hidden ones
        self.all_hidden_edge_types = []

        self.all_types = [] # without hidden ones
        self.all_hidden_types = []

        self._gasMix : Optional[gas_mixture] = None
        self._gasMix_update_id = 0

        self._zModel : Optional[zModel_t] = None # real gas factor
        self._zModel_update_id = 0

        self._fModel : Optional[fModel_t] = None # frictionModel
        self._fModel_update_id = 0

        self.input : Optional[np.ndarray] = None
        self.dinput : Optional[np.ndarray] = None

    @property
    def gasMix(self) -> gas_mixture:
        if self.gasMix_update_id == 0:
            raise ModellingError("gasMix was requested from the net but never set before!")
        return self._gasMix

    @property
    def gasMix_update_id(self):
        return self._gasMix_update_id

    @gasMix.setter
    def gasMix(self, gasMix : gas_mixture):
        self._gasMix_update_id += 1
        self._gasMix = gasMix

    @property
    def zModel(self) -> zModel_t:
        if self.zModel_update_id == 0:
            raise ModellingError("zModel was requested from the net but never set before!")
        return self._zModel

    @property
    def zModel_update_id(self):
        return self._zModel_update_id

    @zModel.setter
    def zModel(self, zModel : zModel_t):
        self._zModel_update_id += 1
        self._zModel = zModel

    @property
    def fModel(self) -> fModel_t:
        if self.fModel_update_id == 0:
            raise ModellingError("frictionModel was requested from the net but never set before!")
        return self._fModel

    @property
    def fModel_update_id(self):
        return self._fModel_update_id

    @fModel.setter
    def fModel(self, fModel : fModel_t):
        self._fModel_update_id += 1
        self._fModel = fModel

    def append(self, obj : "base_element"):
        obj.block_idx = self.dim
        self.dim += obj.dim

        self.components.append(obj)

        if not (obj.name in self.nameReg):
            self.nameReg[obj.name] = obj
        else:
            raise ModellingError("An Element by name: {} was already part of the network!".format(obj.name))

        if not (obj.type in self.typeReg): self.typeReg[obj.type] = []
        self.typeReg[obj.type].append(obj)
        if (not (obj.type in self.all_types)) and (not (obj.type in self.all_hidden_types)):
            if not ('hidden' in obj.type): self.all_types.append(obj.type)
            else: self.all_hidden_types.append(obj.type)
            if "node" in obj.type:
                if not ('hidden' in obj.type): self.all_node_types.append(obj.type)
                else: self.all_hidden_node_types.append(obj.type)
            else:
                if not ('hidden' in obj.type): self.all_edge_types.append(obj.type)
                else: self.all_hidden_edge_types.append(obj.type)

    def __call__(self, dx : np.ndarray, x : np.ndarray, t : float, **kwargs):
        self.input  = x
        self.dinput = dx

        output = np.empty_like(x, dtype = x.dtype)

        for edge_types in [self.all_edge_types, self.all_hidden_edge_types]:
            for edge_type in edge_types:
                for edgeInstance in self.typeReg[edge_type]:
                    var_ids = np.array(edgeInstance.var_ids, dtype = np.intp)
                    output[var_ids] = edgeInstance(t, **kwargs)
        for node_types in [self.all_node_types, self.all_hidden_node_types]:
            for node_type in node_types:
                for nodeInstance in self.typeReg[node_type]:
                    var_ids = np.array(nodeInstance.var_ids, dtype = np.intp)
                    output[var_ids] = nodeInstance(t, **kwargs)

        return output


class base_element(object):

    def __init__(self, name : str, element_type : str, net : network_dae, dim : int):
        '''
            :param name:
            :param element_type:
            :param net:
            :param dim:
        '''

        self.name = name
        self.type = element_type

        self.block_idx = None # will be set by net.append
        self.dim = dim

        self.net = net
        self.net.append(self)

    def variable_id(self, idx):
        if idx >= self.dim:
            raise IndexError('{} out of bounds! idx: {} has to be < dim: {}!'.format(str(self), idx, self.dim))

        return self.block_idx + idx

    def variable(self, idx):
        return self.net.input[self.variable_id(idx)]

    def dvariable(self, idx):
        return self.net.dinput[self.variable_id(idx)]

    @property
    def var_ids(self):
        return [self.variable_id(idx) for idx in range(self.dim)]

    def __str__(self):
        return "<elem name: {} | type: {}>".format(self.name, self.type)

    def __repr__(self):
        return self.__str__()


class node(base_element):

    def __init__(self, name : str, net : network_dae, dim : int = 1, _type_prefix : str = ""):
        '''
            :param name:
            :param net:
            :param dim:
        '''

        super().__init__(name = name, element_type = _type_prefix + 'node', net = net, dim = dim)

        '''
            gas physical values
        '''
        self.height = None

        '''
            topology or data structural related information
        '''
        self.coor_x = None
        self.coor_y = None

        self.left_edges = []
        self.right_edges = []

        self._behaviour = None
        self._callFunc = None
        self.pBoundFunc = None
        self.qBoundFunc = lambda *args, **kwargs: 0.0
        self.behaviour = 0.5

    def assign_topo_info(self,
                         behaviour : int = None,
                         height_inTuple : Tuple[float, str] = (0.0, 'm'),
                         coor : Tuple[float, float] = (None, None)):
        self.behaviour = behaviour
        self.height = length_to_meter(*height_inTuple)
        self.coor_x, self.coor_y = coor

    @property
    def p_press_id(self):
        return self.variable_id(0)

    @property
    def p_press(self):
        return self.variable(0)

    @property
    def dp_press(self):
        return self.dvariable(0)

    @property
    def behaviour(self):
        return self._behaviour

    @behaviour.setter
    def behaviour(self, new_behav):
        if new_behav is None:
            pass
        else:
            self._behaviour = new_behav

            if new_behav == 0: self._callFunc = self.pCond
            else: self._callFunc = self.qCond

    def pCond(self, t):
        return self.p_press - self.pBoundFunc(t)

    def qCond(self, t):
        result = self.qBoundFunc(t)

        for edgeR in self.right_edges:
            result += edgeR.qR_rightFlow
        for edgeL in self.left_edges:
            result -= edgeL.qL_leftFlow

        return result

    def __call__(self, t, **kwargs):
        return self._callFunc(t)


node_t = Union[node, Tuple[str, int]]


class base_edge(base_element):

    def __init__(self, name : str, edge_type : str, net : network_dae, dim : int,
                 left : node_t, right : node_t, _type_prefix : str = ""):
        '''
            :param name:
            :param edge_type:
            :param net:
            :param dim:
            :param left:
            :param right:
        '''

        super().__init__(name = name, element_type = _type_prefix + 'edge-' + edge_type, net = net, dim = dim)

        if isinstance(left, tuple) and isinstance(left[0], str):
            if left[0] in self.net.nameReg:
                self.left = self.net.nameReg[left[0]]
            else:
                self.left = node(name = left[0], net = net, dim = left[1])
        else:
            self.left = left
        self.left.left_edges.append(self)

        if isinstance(right, tuple) and isinstance(right[0], str):
            if right[0] in self.net.nameReg:
                self.right = self.net.nameReg[right[0]]
            else:
                self.right = node(name = right[0], net = net, dim = right[1])
        else:
            self.right = right
        self.right.right_edges.append(self)

        self.scale = pressure_to_pascal(1.0, 'bar') # == 1.0e5

        self._length = None
        self._diameter = None
        self._diameter_reset = None                   # indicator when kappa & lambda need to be re-computed
        self._roughness = None
        self._roughness_reset = None                  # indicator when lambda need to be re-computed
        self.slopeFactor = None                       # automatically computed from length
        self.scaled_area = None                       # automatically computed from diameter
        self.area = None                              # automatically computed from diameter
        self.scaled_area_over_length = None           # automatically computed from BOTH diameter and length

        self._gasMix = None                           # gasMix - if never set inherited by self.net.gasMix
        self._gasMix_reset = None                     # indicator when kappa need to be re-computed
        self._last_gasMix_update_id_of_the_net = None # necessary to determine when self._gasMix_reset need to be set True

        self._fModel = None                           # frictionModel - if never set inherited by self.net.fModel
        self._fModel_reset = None                     # indicator when lambda need to be re-computed
        self._last_fModel_update_id_of_the_net = None # necessary to determine when self._fModel_reset need to be set True

        self._zModel = None                           # real gas factor - if never set inherited by self.net.zModel
        self._zModel_factory = None

        self._kappa = None                            # automatically computed from various dependencies
        self._scaled_kappa = None                     # automatically computed from various dependencies

        self._lam = None                     # lambda & automatically computed from various dependencies
        self._frictionCoefficient = None              # automatically computed from various dependencies
        self.drag_factor = None                       # for resistors

        self._single_flow = None # pipes usually offer left and right flows; whereas other edge types only have one
        if ("pipe" in self.type) and (self.dim > 1): # a simple heuristic!
            self.single_flow = False
        else:
            self.single_flow = True

    @property
    def single_flow(self):
        return self._single_flow

    @single_flow.setter
    def single_flow(self, new_state : bool):
        if (not new_state) and self.dim < 2:
            err_msg = "{} cannot provide 2 flow variables qL, qR with dim: {} < 2!".format(str(self), self.dim)
            raise ModellingError(err_msg)

        self._single_flow = new_state

    def assign_topo_info(self,
                         gasMix = None,
                         fModel = None,
                         zModel = None,
                         length_inTuple : Tuple[float, str] = (1.0, 'm'),
                         diameter_inTuple : Tuple[float, str] = (1.0, 'm'),
                         roughness_inTuple : Tuple[float, str] = (1.0, 'm'),
                         drag_factor : float = 1.0):
        self.gasMix      = gasMix
        self.fModel      = fModel
        self.zModel      = zModel
        self.length      = length_inTuple # computes slope of edge
        self.diameter    = diameter_inTuple # computes area
        self.roughness   = roughness_inTuple
        self.drag_factor = drag_factor

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length_inTuple : Tuple[float, str]):
        length, length_unit = length_inTuple

        if length <= 0.0:
            raise ModellingError("{} edge length need to be strictly positive!".format(str(self)))

        self._length = length_to_meter(length, length_unit)

        hx = (self.right.height - self.left.height)/self.length
        g = acceleration_to_m_per_s_2(9.80665, "m/s^2")
        self.slopeFactor = g*hx

        self._compute_scaled_area_over_length()

    @property
    def diameter(self):
        return self._diameter

    @diameter.setter
    def diameter(self, diameter_inTuple : Tuple[float, str]):
        diameter, diameter_unit = diameter_inTuple

        if diameter <= 0.0:
            raise ModellingError("{} edge diameter need to be strictly positive!".format(str(self)))

        self._diameter = length_to_meter(diameter, diameter_unit)
        self._diameter_reset = True
        self.area = np.pi*((self.diameter/2.0)**2.0)
        self.scaled_area = self.scale*self.area

        self._compute_scaled_area_over_length()

    def _compute_scaled_area_over_length(self):
        if (not (self.length is None)) and (not (self.diameter is None)):
            self.scaled_area_over_length = self.scaled_area/self.length

    @property
    def roughness(self):
        return self._roughness

    @roughness.setter
    def roughness(self, roughness_inTuple : Tuple[float, str]):
        roughness, roughness_unit = roughness_inTuple

        self._roughness = length_to_meter(roughness, roughness_unit)
        self._roughness_reset = True

    @property
    def gasMix(self):
        if self._gasMix is None:
            current_gasMix_update_id_of_the_net = self.net.gasMix_update_id
            if self._last_gasMix_update_id_of_the_net != current_gasMix_update_id_of_the_net:
                self._gasMix_reset = True
                self._last_gasMix_update_id_of_the_net = current_gasMix_update_id_of_the_net
            return self.net.gasMix
        return self._gasMix

    @gasMix.setter
    def gasMix(self, gasMix):
        self._gasMix = gasMix
        self._gasMix_reset = True

    @property
    def fModel(self):
        if self._fModel is None:
            current_fModel_update_id_of_the_net = self.net.fModel_update_id
            if self._last_fModel_update_id_of_the_net != current_fModel_update_id_of_the_net:
                self._fModel_reset = True
                self._last_fModel_update_id_of_the_net = current_fModel_update_id_of_the_net
            return self.net.fModel
        return self._fModel

    @fModel.setter
    def fModel(self, fModel):
        self._fModel = fModel
        self._fModel_reset = True

    def _recompute_kappa_and_lam_if_necessary(self):
        if (self._diameter_reset is None) or (self._gasMix_reset is None):
            err_msg = "{} lam, kappa or scaled_kappa are available when gasMix and zModel are available!".format(str(self))
            raise ModellingError(err_msg)

        if self._diameter_reset or self._gasMix_reset:
            self._kappa = (self.gasMix.Rs*self.gasMix.T)
            self._scaled_kappa = self._kappa/self.scaled_area
            self._kappa = self._kappa/self.area

        if self._roughness_reset or self._diameter_reset or self._fModel_reset:
            self._lam = self.fModel(self.roughness, self.diameter)
            self._frictionCoefficient = self._lam/(2.0*self.diameter)

        self._zModel = self._zModel_factory(self._gasMix)

        self._diameter_reset = False
        self._gasMix_reset = False
        self._fModel_reset = False
        self._roughness_reset = False

    @property
    def zModel(self):
        if self._zModel_factory is None:
            return self.net.zModel(self.gasMix)

        self._recompute_kappa_and_lam_if_necessary()
        return self._zModel

    @zModel.setter
    def zModel(self, zModel_factory):
        self._zModel_factory = zModel_factory

    @property
    def kappa(self):
        self._recompute_kappa_and_lam_if_necessary()
        return self._kappa

    @property
    def scaled_kappa(self):
        self._recompute_kappa_and_lam_if_necessary()
        return self._scaled_kappa

    @property
    def lam(self):
        self._recompute_kappa_and_lam_if_necessary()
        return self._lam

    @property
    def frictionCoefficient(self):
        self._recompute_kappa_and_lam_if_necessary()
        return self._frictionCoefficient

    @property
    def pL_leftPress_id(self):
        return self.left.p_press_id

    @property
    def pL_leftPress(self):
        return self.left.p_press

    @property
    def dpL_leftPress(self):
        return self.left.dp_press

    @property
    def pR_rightPress_id(self):
        return self.right.p_press_id

    @property
    def pR_rightPress(self):
        return self.right.p_press

    @property
    def dpR_rightPress(self):
        return self.right.dp_press

    @property
    def qL_leftFlow_id(self):
        return self.variable_id(0)

    @property
    def qL_leftFlow(self):
        return self.variable(0)

    @property
    def dqL_leftFlow(self):
        return self.dvariable(0)

    @property
    def qR_rightFlow_id(self):
        if self.single_flow:
            idx = 0
        else:
            idx = 1

        return self.variable_id(idx)

    @property
    def qR_rightFlow(self):
        if self.single_flow:
            idx = 0
        else:
            idx = 1

        return self.variable(idx)

    @property
    def dqR_rightFlow(self):
        if self.single_flow:
            idx = 0
        else:
            idx = 1

        return self.dvariable(idx)

    @property
    def q_flowThrough_id(self):
        if self.single_flow:
            return self.variable_id(0)
        raise ModellingError("{} q_flowThrough_id is ambiguous for a 2 flow edge type".format(str(self)))

    @property
    def q_flowThrough(self):
        if self.single_flow:
            return self.variable(0)
        raise ModellingError("{} q_flowThrough is ambiguous for a 2 flow edge type".format(str(self)))

    @property
    def dq_flowThrough(self):
        if self.single_flow:
            return self.dvariable(0)
        raise ModellingError("{} dq_flowThrough_id is ambiguous for a 2 flow edge type".format(str(self)))
