'''
    pipe following so called box-scheme of spatial discretization

    spatially discretized pipe equation by implicit box or trapezoidal scheme

    short description: - replace spatial derivatives p_x(t, x) or q_(t, x) by finite differences
                         (p(t, 1) - p(t, 0))/pipeLength or (q(t, 1) - q(t, 0))/pipeLength respectively.
                       - replace all spatially parametrized time derivatives p_t(t, x) or q_t(t, x) by
                         (p_t(t, 1) - p_t(t, 0))/2 or (q_t(1, x) - q_t(0, x))/2 respectively.
                       - use a trapezoidal formula for the RHS f(p(t, x), q(t, x), t), i.e.
                         ( f(p(t, 1), q(t, 1), t) + f(p(t, 0), q(t, 0), t) )/2

    note: p(t, 0) might also refered as p_L(t) (left pressure) and p(t, 1) as p_R(t) (right pressure) in literature
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t

from ad.cycADa import signSquare


class pipeBox(base_edge):

    def __init__(self, name : str, net : network_dae,
                 left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "pipe-box", net = net, dim = 2, left = left, right = right)

    def _trapezoidEval(self, R_val, L_val, func = None):
        if func is None:
            return (R_val + L_val)/2.0
        return (func(R_val) + func(L_val))/2.0

    def __call__(self, t, **kwargs):
        A_over_length = self.scaled_area_over_length
        fric_coeff    = self.frictionCoefficient
        slope_coeff   = self.slopeFactor

        pL  = self.pL_leftPress
        dpL = self.dpL_leftPress
        pR  = self.pR_rightPress
        dpR = self.dpR_rightPress

        qL  = self.qL_leftFlow
        dqL = self.dqL_leftFlow
        qR  = self.qR_rightFlow
        dqR = self.dqR_rightFlow

        zL, BzL = [self.scaled_kappa*entry for entry in self.zModel(pL)]
        zR, BzR = [self.scaled_kappa*entry for entry in self.zModel(pR)]

        zpL = zL/pL
        zpR = zR/pR

        pzMid = self._trapezoidEval(1.0/zpR, 1.0/zpL, None)

        dpMid = self._trapezoidEval(dpR, dpL, None)
        dqMid = self._trapezoidEval(dqR, dqL, None)
        # dqMid = 0.0

        BzTrap_over_length = self._trapezoidEval(BzR, BzL, None)/self.length # trapezoidal weighted bracket term 'Bz'

        nonLinTrap = self._trapezoidEval([zpR, qR],
                                         [zpL, qL],
                                         lambda zpq: zpq[0]*signSquare(zpq[1]))

        return dpMid + BzTrap_over_length*(qR - qL), \
               dqMid + A_over_length*(pR - pL) + fric_coeff*nonLinTrap + slope_coeff*pzMid
