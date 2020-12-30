'''
    friction free connection
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t


''' discontinuous modelling '''
class shortPipe(base_edge):

    def __init__(self, name : str, net : network_dae, left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "short-pipe", net = net, dim = 1,
                         left = left, right = right)

        self.assign_topo_info()

    def __call__(self, t, **kwargs):
        pL = self.pL_leftPress
        dpL = self.dpL_leftPress
        pR = self.pR_rightPress
        dpR = self.dpR_rightPress
        # q = self.q_flowThrough
        dq = self.dq_flowThrough

        px = pR - pL

        return 1.0e-10*(dpR - dpL + dq) + px
