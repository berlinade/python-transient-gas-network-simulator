'''
    prepared callback functions/examples
    ====================================

    It is highly recommended to provide your own callback functions for newton (if needed et all),
    but here are some defaults/examples
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
import sys

import numpy as np

from paso.util.types_and_errors import Vec_t, CsMatrix_t, Callback_t, LinSolve_t
from paso.util.analysis import table_print, matrix_sparsity_pattern_plot

from paso.solvers.nlin.sparse_nl_solver.util.general import call_counter
from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_newton_options

from typing import Tuple, List, Optional, Callable


'''
    body
    ====
'''
class callback_store_all_iterates(object):

    def __init__(self):
        '''
            callback_instance = callback_store_all_iterates()
            -------------------------------------------------

            creates a callback function to store/save all iterates x_n/x_n1 computed by Newton

            note: instances of this class are callable as functions
        '''
        self.Xs : List[Vec_t] = []

    def __call__(self,
                 options : sparse_newton_options,
                 linsolver : LinSolve_t,
                 idx_newton_step: int,
                 state_n1 : Tuple[Vec_t, Vec_t, Vec_t, Vec_t, float, CsMatrix_t, Vec_t],
                 state_n : Tuple[Vec_t, Vec_t, Vec_t, Vec_t, float, CsMatrix_t, Vec_t],
                 local_gamma : float, mono: float, latest_J_n_change_at_idx: int, J_n_is_changed: bool,
                 eval_fun : call_counter, eval_orig_jac : call_counter, eval_jac : Callable,
                 cond_atol_dom: bool, cond_rtol_dom: bool,
                 cond_atol_range: bool, cond_rtol_range: bool,
                 cond_atol_root : bool) -> None:
        (x_n1, tol_x_n1, f_n1, tol_f_n1, tol_f_n1_norm, J_n1, scaling_n1) = state_n1
        (x_n, tol_x_n, f_n, tol_f_n, tol_f_n_norm, J_n, scaling_n) = state_n

        if len(self.Xs) == 0: self.Xs.append(x_n)
        self.Xs.append(x_n1)


class callback_print_progress(object):

    def __init__(self, float_space : int = 15, int_space : int = 6, file_path_and_name : Optional[str] = None):
        '''
            callback_instance = callback_print_progress(float_space : int = 15,
                                                        int_space : int = 6,
                                                        file_path_and_name : Optional[str] = None)
            --------------------------------------------------------------------------------------

            creates a callback function to generate a print statement for each itearation which either is printed to
            the console or to a user-specified file

            :param float_space: digit width/length for the mantissa-representation of floats (e.g. the residuals)
            :param int_space: digit width/length for the representation of ints (e.g. newton step idx)
            :param file_path_and_name: path and filename for logging/textual reporting (if file is not yet existent it
                                       will be created there)

            note: instances of this class are callable as functions
        '''

        self.float_space : int = max(13, float_space)
        self.int_space : int = max(5, int_space)

        self.table_print = table_print(file_path_and_name = file_path_and_name)

        self.table_print.header_signature = [("#iter", int, self.int_space),
                                             ("||t(x_n1) - t(x_n)||", float, self.float_space),
                                             ("||t(f_n1) - t(f_n)||", float, self.float_space),
                                             ("||t(f_n1)||", float, self.float_space),
                                             ("gamma", float, self.float_space),
                                             ("mono", float, self.float_space),
                                             ("Jac changed", str, 11),
                                             ("nfev", int, self.int_space),
                                             ("njev", int, self.int_space)]
        self.table_print.parse()

        self.first_call : bool = True

    def __call__(self,
                 options : sparse_newton_options,
                 linsolver : LinSolve_t,
                 idx_newton_step : int,
                 state_n1 : Tuple[Vec_t, Vec_t, Vec_t, Vec_t, float, CsMatrix_t, Vec_t],
                 state_n : Tuple[Vec_t, Vec_t, Vec_t, Vec_t, float, CsMatrix_t, Vec_t],
                 local_gamma : float, mono : float, latest_J_n_change_at_idx : int, J_n_is_changed : bool,
                 eval_fun : call_counter, eval_orig_jac : call_counter, eval_jac : Callable,
                 cond_atol_dom : bool, cond_rtol_dom : bool,
                 cond_atol_range : bool, cond_rtol_range : bool,
                 cond_atol_root : bool) -> None:
        (x_n1, tol_x_n1, f_n1, tol_f_n1, tol_f_n1_norm, J_n1, scaling_n1) = state_n1
        (x_n, tol_x_n, f_n, tol_f_n, tol_f_n_norm, J_n, scaling_n) = state_n

        nfev = eval_fun.calls
        njev = eval_orig_jac.calls

        if self.first_call:
            self.table_print.create_table_header()
            self.first_call = False

        last_row : bool = False
        if cond_atol_dom or cond_rtol_dom or cond_atol_range or cond_rtol_range or cond_atol_root: # copy of newton convergence criterion
            if (not options.atol_root) or cond_atol_root: last_row = True

        self.table_print.create_row(idx_newton_step,
                                    np.linalg.norm(tol_x_n1 - tol_x_n),
                                    np.linalg.norm(tol_f_n1 - tol_f_n),
                                    tol_f_n1_norm,
                                    local_gamma, mono,
                                    "yes" if J_n_is_changed else " - ",
                                    nfev, njev,
                                    last_row = last_row)


class callback_matrix_spy(object):

    def __init__(self, stop_at_each_fig : bool = True):
        '''
            callback_instance = callback_matrix_spy(stop_at_each_fig : bool = False)
            ------------------------------------------------------------------------

            creates a callback function to plot the sparsity pattern of the jacobian whenever it changed

            :param stop_at_each_fig: if True a plot is generated and Newton is put to a hold until the plot is closed or
                                     if False all plots a generated after each one another while Newton continues

            note: instances of this class are callable as functions
        '''

        import matplotlib.pyplot as plt

        self.plt = plt
        self.stop_at_each_fig : bool = stop_at_each_fig

    def __call__(self,
                 options : sparse_newton_options,
                 linsolver : LinSolve_t,
                 idx_newton_step : int,
                 state_n1 : Tuple[Vec_t, Vec_t, Vec_t, Vec_t, float, CsMatrix_t, Vec_t],
                 state_n : Tuple[Vec_t, Vec_t, Vec_t, Vec_t, float, CsMatrix_t, Vec_t],
                 local_gamma : float, mono : float, latest_J_n_change_at_idx : int, J_n_is_changed : bool,
                 eval_fun : call_counter, eval_orig_jac : call_counter, eval_jac : Callable,
                 cond_atol_dom : bool, cond_rtol_dom : bool,
                 cond_atol_range : bool, cond_rtol_range : bool,
                 cond_atol_root : bool) -> None:
        (x_n1, tol_x_n1, f_n1, tol_f_n1, tol_f_n1_norm, J_n1, scaling_n1) = state_n1
        (x_n, tol_x_n, f_n, tol_f_n, tol_f_n_norm, J_n, scaling_n) = state_n

        if J_n_is_changed:
            if self.stop_at_each_fig: matrix_sparsity_pattern_plot(J_n1, draw_or_show = None)
            else: matrix_sparsity_pattern_plot(J_n1, draw_or_show = 'draw')

    def conclude(self): self.plt.show()


class callback_of_callbacks(object):

    def __init__(self, *other_callbacks : Callback_t):
        '''
            callback_instance = callback_of_callbacks(callback_instance1, callback_instance2, ...)
            --------------------------------------------------------------------------------------

            creates a callback function that calls other user specified callback instances. Intended to combine
            other callback functions/instances.

            :param other_callbacks: a tuple of other callback instances

            note: instances of this class are callable as functions
        '''

        self.callbacks = other_callbacks

    def __call__(self, *args, **kwargs) -> None:
        for callback_instance in self.callbacks: callback_instance(*args, **kwargs)
