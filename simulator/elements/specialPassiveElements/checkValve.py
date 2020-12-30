'''
    non-return valve
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t

from ad.cycADa import maximum


class checkValve(base_edge):

    def __init__(self, name : str, net : network_dae, left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "check-valve", net = net, dim = 1,
                         left = left, right = right)

        self.assign_topo_info()

    def __call__(self, t, **kwargs):
        pL = self.pL_leftPress
        pR = self.pR_rightPress
        q = self.q_flowThrough

        return maximum(-q, pL - pR)
