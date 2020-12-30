'''
    this is a demo/blueprint of a future homotopy interface
    =======================================================
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np

from paso.util.types_and_errors import Vec_t, CsMatrix_t, Callback_t, NLinSolve_t, NLinSolveError
from paso.util.report_and_option_class import options_base, results_base

from paso.solvers.nlin.sparse_nl_solver.util.general import call_counter, callback_default
from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve, sparse_newton_options # default option
from paso.solvers.nlin.sparse_nl_solver.homotopy.predefined.wrapper import create_nav # default option

from paso.differentiation.util.jacobian_csr_handler import jac_csr, Sparsity_pattern_t, CS_pattern_t

from typing import Union, Optional, Callable, Any, List


'''
    body
    ====
'''
class nlin_solver_cookie(object):
    def __init__(self, nlinsolver : NLinSolve_t): self.solve : NLinSolve_t = nlinsolver


def homotopy_solve(fun : Callable[[Vec_t], Vec_t],
                   x0 : Vec_t,
                   jac : Optional[Union[Callable[[Vec_t], CsMatrix_t], Sparsity_pattern_t, CS_pattern_t]] = None,
                   callback : Optional[Callback_t] = None,
                   homotopy_fun : Optional[Any] = None,
                   nlinsolver : Optional[NLinSolve_t] = None,
                   options : Optional['homotopy_options'] = None) -> 'homotopy_results':
    '''
        docu

        :param fun:
        :param x0:
        :param jac:
        :param tolfunc_dom:
        :param tolfunc_range:
        :param callback:
        :param homotopy_fun:
        :param nlinsolver:
        :param options:
        :return:
    '''

    '''
        function-header: input parsing 
        ------------------------------
    '''
    if options is None: options = homotopy_options()
    no_convergence_is_Error : bool = options.no_convergence_is_Error

    if callback is None: callback = callback_default

    if nlinsolver is None:
        options_newton = sparse_newton_options()
        options_newton.no_convergence_is_Error = False
        def nlinsolver_instance(*args, **kwargs): return sparse_nl_solve(*args, options = options_newton, **kwargs)
        nlinsolver = nlinsolver_instance
    nlinsolver = nlin_solver_cookie(nlinsolver = nlinsolver)

    if homotopy_fun is None: homotopy_fun = create_nav

    ''' if jac not provided as function by user --> use finite difference approximation '''
    if not callable(jac):
        jac_func = jac_csr(fun = fun, # these calls to fun doesn't count on nfev since calling jac counts njev!
                           shape = (len(fun(x0).reshape(-1,)), len(x0.reshape(-1,))))
        if isinstance(jac, (list, tuple, dict)):
            if isinstance(jac, dict): jac = (np.array(jac['indices'], copy = False),
                                             np.array(jac['indptr'], copy = False))
            if isinstance(jac[0], np.ndarray):
                jac_func.indices = jac[0]
                jac_func.indptr = jac[1]
                jac_func.update_directions()
            else: jac_func.assign_sparsity_pattern(sparsity_pattern = jac)
        else: jac_func.assign_sparsity_pattern()
        jac = jac_func

    eval_fun = call_counter(fun) # this class will count every time it has been called -> to find 'nfev' later
    eval_jac = call_counter(jac) # this class will count every time it has been called -> to find 'njev' later


    '''
        function-body: executing homotopy iterations 
        --------------------------------------------
    '''
    x_n : Vec_t = x0

    mu : float = 0.0
    mu_reset : float = mu
    mu_step : float = options.mu_step_initial

    mu_step_min : float = options.mu_step_min
    mu_step_max : float = options.mu_step_max
    mu_expansion : float = options.mu_step_factor_expansion
    mu_shrink : float = options.mu_step_factor_shrink

    success : bool = False
    idx_homotopy_step : int = 0
    subsequent_succs : int = 0
    homotopy_completion : bool = False
    while (not homotopy_completion): # idx_homotopy_step < max_it:
        ''' execute actual homotopy step '''
        fun_mu, jac_mu = homotopy_fun(eval_fun, eval_jac, mu = mu, x_current = x_n)

        report_mu = nlinsolver.solve(fun = fun_mu, x0 = x_n, jac = jac_mu)
        x_n1 = report_mu.x
        success = report_mu.success

        ''' evaluate potential success '''
        if success:
            subsequent_succs += 1
            mu_reset = mu
        else: subsequent_succs = 0

        if mu + 1.0e-2*mu_step_min > 1.0: homotopy_completion = True  # overall success!

        ''' call callback '''
        callback(options,
                 report_mu,
                 nlinsolver, # allows the callback to exchange the nlinsolver
                 idx_homotopy_step,
                 success,
                 subsequent_succs,
                 homotopy_completion,
                 x_n1,
                 x_n,
                 mu, mu_reset, mu_step,
                 eval_fun, eval_jac)

        ''' execute homotopy stepping scheme '''
        if success:
            x_n = x_n1
            if subsequent_succs > 1: mu_step = min(mu_expansion*mu_step, mu_step_max)
        else:
            mu_step = max(mu_shrink*mu_step, mu_step_min)
            if mu_step > mu_step_min: mu = mu_reset
            else: break

        ''' loop conclusion '''
        if (mu + mu_step) >= 1.0:
            mu_step = 1.0 - mu
            mu = 1.0
        else: mu += mu_step

        idx_homotopy_step += 1 # increment step idx of Newton iteration

    if no_convergence_is_Error and (not success): raise NLinSolveError('Did not converge!')  # success remains false!

    ''' 
        function-footer: output preparation
        -----------------------------------
    '''
    report = homotopy_results()

    report['x'] = x_n
    report['success'] = success
    report['nfev'] = eval_fun.calls
    report['njev'] = eval_jac.calls
    report['nit'] = idx_homotopy_step
    report['status'] = 1 if report.success else 0
    report['message'] = f"homotopy iteration is considered successful: {report.success}"
    report['fun'] = eval_fun(x_n)
    # non used scipy-standard-fields here: 'nhev', 'jac', 'hess'

    return report


class homotopy_results(results_base): pass


class homotopy_options(options_base):
    '''
        docu
    '''

    def __init__(self, name : str = "homotopy options"):
        '''
            docu

            :param name:
        '''

        additional_keys : List['str'] = ['name',
                                         'max_it',
                                         'mu_step_initial',
                                         'mu_step_min',
                                         'mu_step_max',
                                         'mu_step_factor_expansion',
                                         'mu_step_factor_shrink',
                                         'no_convergence_is_Error']
        super().__init__(name = name, additional_keys = additional_keys)

        self.max_it : int = 100

        self.mu_step_initial : float = 1.0e-1
        self.mu_step_min : float = 1.0e-2
        self.mu_step_max : float = 1.0e-1

        self.mu_step_factor_expansion : float = 1.9
        self.mu_step_factor_shrink : float = 0.5

        self.no_convergence_is_Error : bool = True
