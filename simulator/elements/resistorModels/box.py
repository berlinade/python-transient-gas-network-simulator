'''
    resistor following so called box-scheme of spatial discretization
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t

from ad.cycADa import signSquare


class resistorBox(base_edge):

    def __init__(self, name : str, net : network_dae,
                 left : node_t, right : node_t, _type_prefix : str = None):
        super().__init__(name = name, edge_type = "resistor-box",
                         net = net, dim = 1,
                         left = left, right = right,
                         _type_prefix = _type_prefix)

    def _trapezoidEval(self, R_val, L_val, func = None):
        if func is None:
            return (R_val + L_val)/2.0
        return (func(R_val) + func(L_val))/2.0

    def __call__(self, t, **kwargs):
        A_over_length = self.scaled_area_over_length
        fric_coeff    = self.drag_factor/2.0

        pL = self.pL_leftPress
        pR = self.pR_rightPress

        q  = self.q_flowThrough

        zL = self.scaled_kappa*self.zModel(pL, bracket_eval = False)
        zR = self.scaled_kappa*self.zModel(pR, bracket_eval = False)

        zpL = zL/pL
        zpR = zR/pR

        zpMid = self._trapezoidEval(zpR, zpL, None)

        return A_over_length*(pR - pL) + fric_coeff*zpMid*signSquare(q)
