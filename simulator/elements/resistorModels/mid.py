'''
    resistor following mid-point scheme of spatial discretization
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t

from ad.cycADa import signSquare


class resistorMid(base_edge):

    def __init__(self, name : str, net : network_dae,
                 left : node_t, right : node_t, _type_prefix : str = ""):
        super().__init__(name = name, edge_type = "resistor-mid",
                         net = net, dim = 1,
                         left = left, right = right,
                         _type_prefix = _type_prefix)

    def _midEval(self, R_val, L_val):
        return (R_val + L_val)/2.0

    def __call__(self, t, **kwargs):
        A_over_length = self.scaled_area_over_length
        fric_coeff    = self.drag_factor/2.0

        pL = self.pL_leftPress
        pR = self.pR_rightPress

        q  = self.q_flowThrough

        pMid = self._midEval(pR, pL)

        zMid = self.scaled_kappa*self.zModel(pMid, bracket_eval = False) # == self.right.zModel(pMid)

        zpMid = zMid/pMid

        return A_over_length*(pR - pL) + fric_coeff*zpMid*signSquare(q)
