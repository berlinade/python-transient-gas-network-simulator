'''
    implicit Euler
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import numpy as np

### solvers
from scipy.optimize import root, least_squares
from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve, sparse_newton_options, \
                                                           NLinSolveError
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.linsolvers import spilu_simple_wrapper, spsolve_simple_wrapper, splu_simple_wrapper
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.callbacks import callback_print_progress, callback_matrix_spy

from paso.util.report_and_option_class import integration_report, integration_options
from paso.util.basics import force_array
from paso.util.types_and_errors import Vec_t, CsMatrix_t
from paso.differentiation.util.wrapper_cycADa import cycADa_wrapper

from typing import Callable, Optional, Union, List

'''
    body
'''
def ImpEulerStep(sys_func : Callable[[Vec_t, Vec_t, float], Vec_t], x_n : Vec_t,
                 t_n : float, h : float,
                 atol : float = 1.e-8, rtol : float = 1.0e-5,
                 maxit : int = 20,
                 use_scipy : Optional[Union[bool, str]] = None,
                 use_cycADa : Optional[bool] = False,
                 *args, **kwargs):
    dim_x : int = len(x_n)
    t_n1 = t_n + h

    def inner_step_func(x_n1): return sys_func((x_n1 - x_n)/h, x_n1, t_n1)

    if use_cycADa: _inner_step_func, _inner_step_Dfunc = cycADa_wrapper(inner_step_func, dim_x)
    else: _inner_step_func, _inner_step_Dfunc = inner_step_func, None

    ''' solve nonlinear root problem '''
    if (isinstance(use_scipy, bool) and (not use_scipy)) or (use_scipy is None):
        options_sn_inst = sparse_newton_options(atol_range = atol, atol_dom = atol,
                                                rtol_range = rtol, rtol_dom = rtol,
                                                atol_root = atol, max_it = maxit)
        report = sparse_nl_solve(_inner_step_func,
                                 jac = _inner_step_Dfunc,
                                 x0 = x_n,
                                 options = options_sn_inst,
                                 linsolver = spsolve_simple_wrapper()) #,
                                 # callback = callback_matrix_spy()) #,
                                 # callback = callback_print_progress())
    elif (isinstance(use_scipy, bool) and use_scipy) or (isinstance(use_scipy, str) and (use_scipy == 'least_squares')):
        report = least_squares(inner_step_func, x0 = x_n,
                               ftol = 1.0e-12, xtol = 1.0e-12, gtol = 1.0e-12)
    elif isinstance(use_scipy, str) and (use_scipy == 'root'):
        report = root(inner_step_func, x0 = x_n)
    else: raise Exception('?')

    success = report.success
    x_n1 = report.x

    return t_n1, x_n1, success, inner_step_func


def integrate(sys_func : Callable[[Vec_t, Vec_t, float], Vec_t],
              x0 : Vec_t,
              t0 : float = 0.0, T : float = 1.0,
              h : Optional[float] = None,
              callback : Optional[Callable] = lambda *args, **kwargs: None,
              integrator_opts = None):
    '''
    ImplEuler

    :param sys_func:
    :param x0:
    :param t0:
    :param T:
    :param h:
    :param callback:
    :param integrator_opts:
    :return:
    '''

    ''' parsing '''
    if integrator_opts is None: integrator_opts = ImpEuler_integration_options()

    _h_thresh = min(1.0e-14, T - t0)
    h_grid = max(min(T - t0, integrator_opts.h_grid or T - t0), _h_thresh)
    t_grid_start = t0 + integrator_opts.grid_offset
    h_max = max(min(T - t0, integrator_opts.h_max or T - t0, h_grid), _h_thresh)
    h_min = max(min(h_max, integrator_opts.h_min), _h_thresh)
    if h is None: h_start : float = (T-t0)/100.0
    else: h_start : float = h
    if not integrator_opts.one_step: h_start : float = max(min(h_max, h_start), h_min)

    x0 = force_array(x0, force_1D = True)
    if len(x0.shape) != 1: raise AssertionError("error")
    f0 = sys_func(np.zeros(shape = x0.shape), x0, t0)
    if len(f0.shape) != 1: raise AssertionError("error")
    # dim_x = len(x0)
    # dim_f = len(f0) # == dim_x

    customPts = [ti for ti in integrator_opts.custom_time_points if (ti > t0) and (ti < T)]
    customPts.extend([T + 2.0*h_max])
    customPts = iter(customPts)

    ''' step loop '''
    Ts : List[float] = [t0]
    Hs : List[Union[None, float]] = [None]
    Xs : List[Vec_t] = [x0]

    simul_loop : bool = True
    simul_loop_idx : int = -1

    tt = t_grid_start + (c_tt := 1)*h_grid
    if tt > (customPt := next(customPts)) - h_min:
        tt = customPt
    h = h_start
    h_mem = h_start
    nl_solvings_since_last_fail : int = 0
    h_shrink_factor : float = 2.02
    h_growth_factor : float = 3.1
    h_factor_ratio : float = 1.0

    while simul_loop:
        simul_loop_idx += 1

        if integrator_opts.one_step: simul_loop = False
        else:
            ''' bring h closer to h_mem (if nl solver has no current issues) '''
            if nl_solvings_since_last_fail > min(20, h_factor_ratio):
                if abs(h - h_mem) > _h_thresh:
                    print(f"\t>>> try to move h: {h} to h_mem: {h_mem}", end=" ")
                    if (h > h_mem) and (h > h_min):
                        h = max(h_min, h_mem, h/h_shrink_factor)
                        h_factor_ratio *= h_shrink_factor
                    elif (h < h_mem) and (h < h_max):
                        h = min(h_max, h_mem, h*h_growth_factor)
                        h_factor_ratio /= h_growth_factor
                    print(f"and choose h (new): {h}.")
                else: h_factor_ratio = 1.0

            ''' check h_mem or h would lead beyond integration interval '''
            if (Ts[-1] + h) >= (T - h_min):
                h = max(T - Ts[-1], h_min)
                h_mem = min(h_mem, h)
            elif (Ts[-1] + h_mem) >= (T - h_min): # i.e. h < h_mem anyway because of if before
                h_mem = max(T - Ts[-1], h_min)
            elif (Ts[-1] + h) >= (tt - h_min): # check for grid or custom points
                h = max(tt - Ts[-1], h_min)
                tt = t_grid_start + (c_tt := (c_tt + 1))*h_grid
                if tt > customPt - h_min:
                    tt = customPt
                    customPt = next(customPts)

        '''
            step execution
        '''
        advance_step = False
        try:
            out = ImpEulerStep(sys_func = sys_func,
                               x_n = Xs[-1], t_n = Ts[-1], h = h,
                               atol = integrator_opts.atol_range,
                               rtol = integrator_opts.rtol_range,
                               use_scipy = False,
                               use_cycADa = integrator_opts.cycADa)
            t_new, x_new, success, inner_step_func = out

            print(success, np.linalg.norm(inner_step_func(x_new)))
            if not success: raise RuntimeError
            advance_step = True
            nl_solvings_since_last_fail += 1
        except (RuntimeError, NLinSolveError) as e: # the following code deals with nl-solver issues only and should not be confused with step size control
            if h <= h_min: raise e

            t_new, x_new = None, None
            nl_solvings_since_last_fail = 0
            print(f"\t>>> nl solver failed with {e} ==> Try again - reduce h from: {h}", end = " ")
            h = max(h_min, h/h_shrink_factor)
            h_factor_ratio *= h_shrink_factor
            print(f"to: {h}! (h_mem: {h_mem})")

        '''
            step size control   
        '''
        # TODO: implement step size control by manipulating h_mem!

        '''
            step conclusion
        '''
        if advance_step:
            Ts.append(t_new)
            Hs.append(h)
            Xs.append(x_new)

            if Ts[-1] >= (T - h_min): simul_loop = False

            callback(Ts, Hs, Xs)

            print(f"{100.0*((Ts[-1] - t0)/(T - t0)):>7.2f}%", end = " | ")
            print(f"i : {simul_loop_idx + 1:>2d}", end = " | ")
            print(f"t_n1 = {t_new}")

    simul_report = integration_report()
    simul_report.Ts = Ts
    simul_report.Hs = Hs
    simul_report.Xs = Xs
    simul_report.msg = "ImpEuler integration complete"

    return simul_report


'''
    options dict definition and setting default values.
'''
class ImpEuler_integration_options(integration_options):

    def __init__(self):
        self.additional_keys = ['cycADa']

        super().__init__(name = "ImpEuler integrator options")

        self.cycADa : bool = False
