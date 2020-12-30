'''
    prepared callback functions/examples
    ====================================

    It is highly recommended to provide your own callback functions for homotopy (if needed et all),
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

from paso.util.types_and_errors import Vec_t, CsMatrix_t, Callback_t

from paso.solvers.nlin.sparse_nl_solver.util.general import call_counter
from paso.solvers.nlin.sparse_nl_solver.homotopy.core import homotopy_options, homotopy_results, nlin_solver_cookie

from paso.util.analysis import table_print

from typing import Tuple, List, Optional, Callable


'''
    body
    ====
'''
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
                                             ("success", str, 18),
                                             ("success in a row", int, max(16, self.int_space)),
                                             ("mu", float, self.float_space),
                                             ("mu_reset", float, self.float_space),
                                             ("mu_step", float, self.float_space),
                                             ("nfev", int, self.int_space),
                                             ("njev", int, self.int_space)]
        self.table_print.parse()

        self.first_call : bool = True

    def __call__(self,
                 options : homotopy_options,
                 report_mu : homotopy_results,
                 nlinsolver : nlin_solver_cookie,  # allows the callback to exchange the nlinsolver
                 idx_homotopy_step : int,
                 success : bool,
                 subsequent_succs : int,
                 homotopy_completion : bool,
                 x_n1 : Vec_t,
                 x_n : Vec_t,
                 mu : float, mu_reset : float, mu_step : float,
                 eval_fun : call_counter, eval_jac : call_counter) -> None:
        nfev = eval_fun.calls
        njev = eval_jac.calls

        if self.first_call:
            self.table_print.create_table_header()
            self.first_call = False

        last_row : bool = False
        if homotopy_completion: last_row = True

        self.table_print.create_row(idx_homotopy_step,
                                    'True' if success else 'False',
                                    subsequent_succs,
                                    mu, mu_reset, mu_step,
                                    nfev, njev,
                                    last_row = last_row)


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
