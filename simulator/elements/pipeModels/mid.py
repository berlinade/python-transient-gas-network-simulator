'''
    pipe following mid-point-scheme of spatial discretization

    spatially discretized pipe equation by midpoint scheme

    short description: - replace spatial derivatives p_x(t, x) or q_(t, x) by finite differences
                         (p(t, 1) - p(t, 0))/pipeLength or (q(t, 1) - q(t, 0))/pipeLength respectively.
                       - replace all spatially parametrized time derivatives p_t(t, x) or q_t(t, x) by
                         (p_t(t, 1) - p_t(t, 0))/2 or (q_t(1, x) - q_t(0, x))/2 respectively.
                       - use a midpoint formula for the RHS f(p(t, x), q(t, x), t), i.e.
                         f( [p(t, 1) + p(t, 0)]/2, [q(t, 1) + q(t, 0)]/2, t )

    note: p(t, 0) might also refered as p_L(t) (left pressure) and p(t, 1) as p_R(t) (right pressure) in literature
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t
from simulator.resources.auxiliary import ModellingError

from ad.cycADa import signSquare


class pipeMid(base_edge):

    def __init__(self, name : str, net : network_dae,
                 left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "pipe-mid", net = net, dim = 2, left = left, right = right)

    def _midEval(self, R_val, L_val):
        return (R_val + L_val)/2.0

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

        pMid = self._midEval(pR, pL)

        qMid = self._midEval(qR, qL)

        zModelValMid = self.zModel(pMid)

        zMid, BzMid = [self.scaled_kappa*entry for entry in zModelValMid]

        zpMid = zMid/pMid

        dpMid = self._midEval(dpR, dpL)
        dqMid = self._midEval(dqR, dqL)

        BzMid_over_length = BzMid/self.length # mid weighted bracket term 'Bz'

        return dpMid + BzMid_over_length*(qR - qL), \
               dqMid + A_over_length*(pR - pL) + fric_coeff*zpMid*signSquare(qMid) + slope_coeff/zpMid
