'''
    valve
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t
from simulator.resources.profiles import default_io

from ad.cycADa import cond_assign


''' discontinuous modelling '''
class valve(base_edge):

    def __init__(self, name : str, net : network_dae, left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "common-valve", net = net, dim = 1,
                         left = left, right = right)

        self.assign_topo_info()

        self.io_func = default_io

    def __call__(self, t, **kwargs):
        pL = self.pL_leftPress
        pR = self.pR_rightPress
        q = self.q_flowThrough

        px = pR - pL

        io = self.io_func(t)

        return cond_assign(io > 0.0, px, q)


''' continuous modelling '''
# class valve(base_edge):
#
#     def __init__(self, name : str, net : network_dae, left : node_t, right : node_t):
#         super().__init__(name = name, edge_type = "valve", net = net, dim = 1,
#                          left = left, right = right)
#
#         self.io_func = default_io
#
#     def __call__(self, t, **kwargs):
#         pL = self.pL_leftPress
#         pR = self.pR_rightPress
#         q = self.q_flowThrough
#
#         px = pR - pL
#
#         io = self.io_func(t)
#
#         return io*px - (1.0 - io)*q


''' differential modelling - requires adaption to post refactored code! '''
# class valve(singleFlow_arc):
#
#     def __init__(self, nL, nR, name = '-1', alias = 'generic'):
#         super(valve, self).__init__(nL, nR, dim = 1, name = name, alias = alias)
#
#         self.IO_func = IO_default_func
#
#     def __call__(self, t, **kwargs):
#         pL = self.pL_leftPress # self.network.input[self.pL_idx]
#         dpL = self.dpL_leftPress
#         pR = self.pR_rightPress # self.network.input[self.pR_idx]
#         dpR = self.dpR_rightPress
#         q = self.q_flowThrough # self.network.input[self.qL_idx]
#         dq = self.dq_flowThrough # self.network.dinput[self.qL_idx]
#
#         px = pL - pR
#
#         io = self.IO_func(t)
#
#         return 1.0e-10*(dpR - dpL + dq) - (io*px - (1.0 - io)*q) # dq - (io*10000.0*px - q)
