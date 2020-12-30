from src_sim.pyGas.netgraph import base_edge, network_dae, node_t
from src_sim.pyGas.resources.profiles import table_lookup
from src_sim.pyGas.resources.auxiliary import obligatory_function

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
        press_diff = pR - pL

        # target value: flow
        # cond = cond_assign(q > bar_ubar_q, press_diff, bar_ubar_q - q)
        cond = bar_ubar_q - q

        # target values: left and right pressure
        max_term = maximum(pR - bar_pR, ubar_pL - pL, pL - pR)
        cond = cond_assign(logical_or(logical_or(pR >= bar_pR, pL <= ubar_pL), pL >= pR),
                           cond_assign(q <= 0.0, q, max_term), cond)

        # cond = cond_assign(q <= 0.0, cond_assign(logical_or(pR > bar_pR, pL < ubar_pL), q, cond), cond)
        # cond = cond_assign(pL >= pR, cond_assign(q <= 0.0, q, press_diff), cond)

        # mode determination
        cond = cond_assign(by_io > 0.01, press_diff, cond)
        cond = cond_assign(io < 0.01, q, cond)

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
        # # target value driven modelling
        # press_diff = pL - pR
        #
        # # target value: flow
        # # cond = bar_ubar_q - q
        # cond = cond_assign(q < bar_ubar_q,
        #                    cond_assign(logical_and(pL >= pR, q >= 0.0),
        #                                minimum(bar_ubar_q - q, press_diff),
        #                                q),
        #                    cond_assign(logical_and(pL >= pR, q >= 0.0),
        #                                bar_ubar_q - q,
        #                                q)) # bar_ubar_q - q)
        #
        # # target values: left upper and right lower pressure
        # max_term = maximum(ubar_pR - pR, pL - bar_pL)
        # cond = cond_assign(logical_or(pR <= ubar_pR, pL >= bar_pL),
        #                    cond_assign(logical_and(pL >= pR, q >= 0.0),
        #                                max_term,
        #                                q),
        #                    cond_assign(pL >= pR,
        #                                cond,
        #                                q))
        #
        # # target values: left lower and right upper pressure
        # max_term = maximum(pR - bar_pR, ubar_pL - pL, pR - pL)
        # cond = cond_assign(logical_or(pR >= bar_pR, pL <= ubar_pL),
        #                    cond_assign(pL >= pR,
        #                                cond_assign(q > 0.0,
        #                                            max_term,
        #                                            q),
        #                                q),
        #                    cond_assign(pL >= pR,
        #                                cond,
        #                                q))
        #
        # # cond = min(cond, press_diff) # cond_assign(logical_or(q < 0.0, pR > pL), press_diff, cond)
        #
        # # cond = cond_assign(q <= 0.0, cond_assign(logical_or(pR > bar_pR, pL < ubar_pL), q, cond), cond)
        # # cond = cond_assign(logical_or(pR >= pL, q <= 0.0), cond_assign(pR >= pL, q, cond), cond)
        # # cond = cond_assign(bar_ubar_q <= 0.0, q, cond)




        cond = cond_assign(pL >= pR,
                           minimum(bar_ubar_q - q, pL - pR),
                           q)

        cond = cond_assign(logical_or(pR <= ubar_pR, pL >= bar_pL),
                           cond_assign(q < bar_ubar_q,
                                       cond,
                                       maximum(ubar_pR - pR, pL - bar_pL)),
                           cond)

        cond = cond_assign(logical_or(logical_or(pR >= bar_pR, pL <= ubar_pL), pL <= pR),
                           cond_assign(logical_or(q <= bar_ubar_q, logical_or(pR <= ubar_pR, pL >= bar_pL)),
                                       maximum(pR - bar_pR, ubar_pL - pL, pR - pL),
                                       cond),
                           cond)

        cond = cond_assign(q == 0.0, cond_assign(logical_or(logical_or(pL < ubar_pL, pR > bar_pR), pL < pR),
                                                 q,
                                                 cond),
                           cond_assign(q < 0.0,
                                       q,
                                       cond))

        # cond = minimum(bar_ubar_q - q, pL - pR)
        #
        # cond = cond_assign(logical_or(pR <= ubar_pR, pL >= bar_pL),
        #                    cond_assign(q < bar_ubar_q,
        #                                cond,
        #                                maximum(ubar_pR - pR, pL - bar_pL)),
        #                    cond)
        #
        # cond = cond_assign(logical_or(pR >= bar_pR, pL <= ubar_pL),
        #                    cond_assign(logical_or(q <= bar_ubar_q, logical_or(pR <= ubar_pR, pL >= bar_pL)),
        #                                maximum(pR - bar_pR, ubar_pL - pL),
        #                                cond),
        #                    cond)

        # mode determination
        cond = cond_assign(by_io > 0.01, pR - pL, cond) # not needed due to shortpipe condition
        cond = cond_assign(io < 0.01, q, cond)

        '''
            return statement
        '''
        return cond
