'''
    ideal control valves and compressor stations
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
from simulator.netgraph import base_edge, network_dae, node_t
from simulator.resources.profiles import table_lookup
from simulator.resources.auxiliary import obligatory_function

from ad.cycADa import cond_assign, minimum, maximum, logical_and, logical_or


class _edge_with_target_values(base_edge):

    def __init__(self, name : str, edge_type : str, net : network_dae, dim : int,
                 left : node_t, right : node_t):
        super().__init__(name = name, edge_type = edge_type, net = net, dim = dim,
                         left = left, right = right)

        self.assign_topo_info()

        ''' io functions '''
        self.io_func = obligatory_function('io func', str(self))
        self._by_io_func = obligatory_function('bypass io func', str(self))
        self.by_io_func_locked = False

        ''' target functions '''
        self._target_upper_pR = obligatory_function('target upper pR func', str(self))
        self.target_upper_pR_locked = False
        self._target_lower_pR = obligatory_function('target lower pR func', str(self))
        self.target_lower_pR_locked = False

        self._target_upper_pL = obligatory_function('target upper pL func', str(self))
        self.target_upper_pL_locked = False
        self._target_lower_pL = obligatory_function('target lower pL func', str(self))
        self.target_lower_pL_locked = False

        self._target_q = obligatory_function('target q func', str(self))
        self.target_q_locked = False

    @property
    def by_io_func(self):
        return self._by_io_func

    @by_io_func.setter
    def by_io_func(self, new_io_profile : table_lookup):
        if not self.by_io_func_locked:
            self._by_io_func = new_io_profile

    @property
    def target_upper_pR(self):
        return self._target_upper_pR

    @target_upper_pR.setter
    def target_upper_pR(self, new_profile : table_lookup):
        if not self.target_upper_pR_locked:
            self._target_upper_pR = new_profile

    @property
    def target_lower_pR(self):
        return self._target_lower_pR

    @target_lower_pR.setter
    def target_lower_pR(self, new_profile : table_lookup):
        if not self.target_lower_pR_locked:
            self._target_lower_pR = new_profile

    @property
    def target_upper_pL(self):
        return self._target_upper_pL

    @target_upper_pL.setter
    def target_upper_pL(self, new_profile : table_lookup):
        if not self.target_upper_pL_locked:
            self._target_upper_pL = new_profile

    @property
    def target_lower_pL(self):
        return self._target_lower_pL

    @target_lower_pL.setter
    def target_lower_pL(self, new_profile : table_lookup):
        if not self.target_lower_pL_locked:
            self._target_lower_pL = new_profile

    @property
    def target_q(self):
        return self._target_q

    @target_q.setter
    def target_q(self, new_profile : table_lookup):
        if not self.target_q_locked:
            self._target_q = new_profile


class idealCompressor(_edge_with_target_values):

    def __init__(self, name : str, net : network_dae, left : node_t, right : node_t):
        super().__init__(name = name, edge_type = "ideal-compressor", net = net, dim = 1,
                         left = left, right = right)

    def __call__(self, t, **kwargs):
        pL = self.pL_leftPress
        dpL = self.dpL_leftPress
        pR = self.pR_rightPress
        dpR = self.dpR_rightPress
        q = self.q_flowThrough
        dq = self.dq_flowThrough

        io = self.io_func(t)
        by_io = minimum(self.by_io_func(t), io)

        '''
            get target values
        '''
        bar_pR  = self.target_upper_pR(t)
        ubar_pL = minimum(bar_pR, self.target_lower_pL(t))

        bar_ubar_q = self.target_q(t)

        '''
            define conditions and target values
        '''
        cond = bar_ubar_q - q # target flow
        cond = minimum(cond, pL - ubar_pL, bar_pR - pR) # target pressures
        cond = maximum(cond, 1000.0*(pL - pR), -1000.0*q) # principal necessities of compressors

        '''
            mode determination
        '''
        cond = cond_assign(by_io > 0.01, pR - pL, cond)
        cond = cond_assign(io < 0.01, q, cond)

        # cond = cond - 1.0e-3*(dpR - dpL + dq) # may or may not improve solvabillity of this element

        '''
            return statement
        '''
        return cond


class idealControlValve(_edge_with_target_values):

    def __init__(self, name: str, net: network_dae, left: node_t, right: node_t):
        super().__init__(name = name, edge_type = "ideal-control-valve", net = net, dim = 1,
                         left = left, right = right)

    def __call__(self, t, **kwargs):
        pL = self.pL_leftPress
        dpL = self.dpL_leftPress
        pR = self.pR_rightPress
        dpR = self.dpR_rightPress
        q = self.q_flowThrough
        dq = self.dq_flowThrough

        io = self.io_func(t)
        by_io = minimum(self.by_io_func(t), io)

        '''
            get target values
        '''
        bar_pR = self.target_upper_pR(t)
        ubar_pR = minimum(bar_pR, self.target_lower_pR(t))

        bar_pL = maximum(ubar_pR, self.target_upper_pL(t))
        ubar_pL = minimum(bar_pL, self.target_lower_pL(t))

        bar_ubar_q = maximum(0.0, self.target_q(t))


        '''
            define conditions and target values
        '''
        px = 100.0 * (pL - pR) - 0.001
        cond = maximum(0.0, minimum(maximum(bar_ubar_q, 1000.0*(ubar_pR - pR), 1000.0*(pL - bar_pL)),
                                    1000.0*(bar_pR - pR),
                                    1000.0*(pL - ubar_pL),
                                    px)) - q

        # mode determination
        cond = cond_assign(by_io > 0.01, pR - pL, cond) # not needed due to shortpipe condition
        cond = cond_assign(io < 0.01, q, cond)

        '''
            return statement
        '''
        return cond
