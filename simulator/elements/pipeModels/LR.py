'''
    pipe following so called LR-scheme of spatial discretization

    spatially discretized pipe equation by L-R or Left-Right scheme

    short description: - replace spatial derivatives p_x(t, x) or q_(t, x) by finite differences
                         (p(t, 1) - p(t, 0))/pipeLength or (q(t, 1) - q(t, 0))/pipeLength respectively.
                       - replace all spatially parametrized time derivatives p_t(t, x) by p_t(t, 1) (the RIGHT pressure [see note below])
                         or q_t(t, x) by q_t(t, 0) (the LEFT flow [see note below])
                       - replace any other occurences of pressures p(t, x) by p(t, 1) (the RIGHT pressure [see note below]) or
                         q(t, x) by q(t, 0) (the LEFT flow [see note below])

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


class pipeLR(base_edge):

    def __init__(self, name : str, net : network_dae,
                 left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "pipe-LR", net = net, dim = 2, left = left, right = right)

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

        # zL, BzL = [self.scaled_kappa*entry for entry in self.zModel(pL)] # unneeded
        zR, BzR = [self.scaled_kappa*entry for entry in self.zModel(pR)]

        # zpL = zL/pL
        # zpR = zR/pR

        BzR_over_length = BzR/self.length # weighted bracket term

        # return dpR + BzR_over_length*(qR - qL), \
        #        dqL + A_over_length*(pR - pL) + fric_coeff*zpR*signSquare(qL) + slope_coeff/zpR

        pR_square = pR*pR

        return dpR + BzR_over_length*(qR - qL), \
               pR*dqL + A_over_length*(pR_square - pR*pL) + fric_coeff*zR*signSquare(qL) + pR_square*slope_coeff/zR
