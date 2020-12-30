'''
    this is a demo/blueprint of a future newton interface
    =====================================================
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np

from paso.util.types_and_errors import Vec_t, CsMatrix_t, Callback_t, LinSolve_t, LinSolveError, NLinSolveError
from paso.util.report_and_option_class import options_base, results_base

from paso.solvers.nlin.sparse_nl_solver.util.general import call_counter, tolfunc_default, callback_default
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.linsolvers import spsolve_simple_wrapper # default option

from paso.differentiation.util.jacobian_csr_handler import jac_csr, Sparsity_pattern_t, CS_pattern_t

from typing import Tuple, Union, Optional, Callable, Any, List

'''
    body
    ====
'''
class lin_solver_cookie(object):
    def __init__(self, linsolver : LinSolve_t): self.solve : LinSolve_t = linsolver


class matrix_row_scaling(object):

    def __init__(self, matrix_func : Callable[[Any], CsMatrix_t], apply_scaling : bool = True):
        self.matrix_func : Callable[[Any], CsMatrix_t] = matrix_func
        self.apply_scaling : bool = apply_scaling

    def __call__(self, *args, **kwargs) -> Tuple[CsMatrix_t, Vec_t]:
        '''
            docu

            :param J_n:
            :return:
        '''
        J_n = self.matrix_func(*args, **kwargs)

        if not self.apply_scaling: return J_n, np.ones(shape = (J_n.shape[0],))

        num_rows, data, indptr = J_n.shape[0], J_n.data, J_n.indptr
        v = np.ones(shape = (num_rows,))
        for idx_row in range(num_rows):
            v[idx_row] /= sum(abs(J_n[idx_row, :].data))
            J_n[idx_row, :] *= v[idx_row]

        return J_n, v


def sparse_nl_solve(fun : Callable[[Vec_t], Vec_t],
                    x0 : Vec_t,
                    jac : Optional[Union[Callable[[Vec_t], CsMatrix_t], Sparsity_pattern_t, CS_pattern_t]] = None,
                    tolfunc_dom : Optional[Callable[[Vec_t], Vec_t]] = None,
                    tolfunc_range : Optional[Callable[[Vec_t], Vec_t]] = None,
                    callback : Optional[Callback_t] = None,
                    linsolver : Optional[LinSolve_t] = None,
                    options : Optional['sparse_newton_options'] = None) -> 'sparse_newton_results':
    '''
        docu

        :param fun:
        :param x0:
        :param jac:
        :param tolfunc_dom:
        :param tolfunc_range:
        :param callback:
        :param linsolver:
        :param options:
        :return:
    '''

    '''
        function-header: input parsing 
        ------------------------------
    '''
    if options is None: options = sparse_newton_options()
    atol_dom : Union[None, float, Vec_t] = options.atol_dom
    rtol_dom : Union[None, float, Vec_t] = options.rtol_dom
    atol_range : Union[None, float, Vec_t] = options.atol_range
    rtol_range : Union[None, float, Vec_t] = options.rtol_range
    atol_root : Union[None, float, Vec_t] = options.atol_root
    max_it : int = options.max_it
    max_times_J_n_constant : Union[None, int] = options.max_times_J_n_constant
    gamma_min : float = options.gamma_min
    no_convergence_is_Error : bool = options.no_convergence_is_Error
    apply_row_scaling : bool = options.apply_row_scaling

    if (atol_dom is None) and (rtol_dom is None) and (atol_range is None) and (rtol_range is None) and (atol_root is None):
        raise NLinSolveError("choose some convergence criterion! Not all of them can be 'None'!")

    if tolfunc_dom is None: tolfunc_dom = tolfunc_default
    if tolfunc_range is None: tolfunc_range = tolfunc_default

    if callback is None: callback = callback_default

    if linsolver is None: linsolver = lin_solver_cookie(linsolver = spsolve_simple_wrapper())
    else: linsolver = lin_solver_cookie(linsolver = linsolver)

    ''' if jac not provided as function by user --> use finite difference approximation '''
    eval_fun = call_counter(fun) # this class will count every time it has been called -> to find 'nfev' later
    if not callable(jac):
        jac_func = jac_csr(fun = eval_fun,
                           shape = (len(eval_fun(x0).reshape(-1,)), len(x0.reshape(-1,))))
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

    eval_orig_jac = call_counter(jac) # this class will count every time it has been called -> to find 'njev' later
    eval_jac = matrix_row_scaling(eval_orig_jac, apply_scaling = apply_row_scaling)


    '''
        function-body: executing Newton iterations 
        ------------------------------------------
    '''
    x_n : Vec_t = x0
    tol_x_n : Vec_t = tolfunc_dom(x_n)

    f_n : Vec_t = eval_fun(x_n)
    tol_f_n : Vec_t = tolfunc_range(f_n)
    tol_f_n_norm : float = np.linalg.norm(tol_f_n)

    J_n, scaling_n = eval_jac(x_n) # J_n : CsMatrix_t, scaling_n : Vec_t
    latest_J_n_change_at_idx : int = 0
    recompute_J_n : bool = False

    success : bool = False
    idx_newton_step : int = 0
    while idx_newton_step < max_it:
        ''' gather some meta info about J_n, i.e. the jacobian '''
        J_n_constant_for : int = idx_newton_step - latest_J_n_change_at_idx
        J_n_is_changed : bool = (J_n_constant_for == 0)

        ''' execute actual Newton step '''
        try:
            dir_x_n = linsolver.solve(A = J_n, b = -scaling_n*f_n,
                                      A_did_change = J_n_is_changed)
            if not isinstance(dir_x_n, np.ndarray): raise NLinSolveError('lin solver returned no array')
        except LinSolveError as e:
            if not J_n_is_changed:
                J_n, scaling_n = eval_jac(x_n) # force jacobian recomputation
                latest_J_n_change_at_idx = idx_newton_step
                continue # repeat this Newton step over again with recomputed jacobian
            else: raise NLinSolveError(f'LinSolveError({e}) has been raised!')

        ''' determining next state of next Newton-step '''
        local_gamma : float = 1.0
        while local_gamma >= gamma_min: # simple or primitive dampening
            x_n1 : Vec_t = x_n + local_gamma*dir_x_n

            ''' compute f(x_n1) and check validity '''
            f_n1 : Vec_t = eval_fun(x_n1)
            if np.isnan(f_n1).any() or np.isinf(f_n1).any():
                local_gamma /= 2.0
                continue # shrink Newton step until x_n1 within dom(fun) and repeat while loop!

            ''' apply tolorance functions onto both quantities: x and f '''
            tol_x_n1 : Vec_t = tolfunc_dom(x_n1)
            tol_f_n1 : Vec_t = tolfunc_range(f_n1)
            tol_f_n1_norm : float = np.linalg.norm(tol_f_n1)

            ''' check whether J_n needs re-computation '''
            if (not (max_times_J_n_constant is None)) and (J_n_constant_for >= max_times_J_n_constant):
                recompute_J_n = True

            mono : float = tol_f_n1_norm - tol_f_n_norm # monotonicity of function value convergence
            if mono >= 0.0:
                if not recompute_J_n:
                    if local_gamma/100.0 > gamma_min:
                        local_gamma /= 100.0 # 100.0 is rather large, but: don't try to often
                        continue # shrink Newton step to improve mono
                    else: recompute_J_n = True # ... otherwise recompute jacobian

            ''' recompute Jacobian '''
            if recompute_J_n: J_n1, scaling_n1 = eval_jac(x_n1)
            else: J_n1, scaling_n1 = J_n, scaling_n

            break # Reaching here means: x in dom(f), (mono < 0 -or- jac recomputed)
        else: raise NLinSolveError('out of domain of fun!')

        ''' tolerance checks '''
        # domain checks
        diff_tol_x : Vec_t = abs(tol_x_n1 - tol_x_n) # abs instead of norm here is correct! tolarances are checked in a vector-valued fashion
        if (not (atol_dom is None)) and (diff_tol_x < atol_dom).all(): cond_atol_dom : bool = True
        else: cond_atol_dom : bool = False
        if (not (rtol_dom is None)) and (diff_tol_x < rtol_dom*tol_x_n).all(): cond_rtol_dom : bool = True
        else: cond_rtol_dom : bool = False

        # range checks
        diff_tol_f : Vec_t = abs(tol_f_n1 - tol_f_n) # abs instead of norm here is correct! tolarances are checked in a vector-valued fashion
        if (not (atol_range is None)) and (diff_tol_f < atol_range).all(): cond_atol_range : bool = True
        else: cond_atol_range : bool = False
        if (not (rtol_range is None)) and (diff_tol_f < rtol_range*tol_f_n).all(): cond_rtol_range : bool = True
        else: cond_rtol_range : bool = False

        # hard root criterion
        if (not (atol_root is None)) and (abs(tol_f_n1) < atol_root).all(): cond_atol_root : bool = True
        else: cond_atol_root : bool = False

        ''' call callback '''
        callback(options,
                 linsolver,
                 idx_newton_step,
                 (x_n1, tol_x_n1, f_n1, tol_f_n1, tol_f_n1_norm, J_n1, scaling_n),
                 (x_n, tol_x_n, f_n, tol_f_n, tol_f_n_norm, J_n, scaling_n1),
                 local_gamma, mono, latest_J_n_change_at_idx, J_n_is_changed,
                 eval_fun, eval_orig_jac, eval_jac,
                 cond_atol_dom, cond_rtol_dom,
                 cond_atol_range, cond_rtol_range,
                 cond_atol_root)

        ''' loop conclusion '''
        idx_newton_step += 1 # increment step idx of Newton iteration

        x_n = x_n1
        tol_x_n = tol_x_n1

        f_n = f_n1
        tol_f_n = tol_f_n1
        tol_f_n_norm = tol_f_n1_norm

        if recompute_J_n:
            recompute_J_n = False # reset
            J_n = J_n1
            scaling_n = scaling_n1
            latest_J_n_change_at_idx = idx_newton_step

        if cond_atol_dom or cond_rtol_dom or cond_atol_range or cond_rtol_range or cond_atol_root: # if any tolrance check is positive ==> Newton succeeded!
            if (not atol_root) or cond_atol_root: # hard
                success = True # Newton succeeded
                break # leave most outer while-loop 'over the newton steps'
    else:
        if no_convergence_is_Error: raise NLinSolveError('Did not converge!') # success remains false!


    ''' 
        function-footer: output preparation
        -----------------------------------
    '''
    report = sparse_newton_results()

    report['x'] = x_n
    report['success'] = success
    report['nfev'] = eval_fun.calls
    report['njev'] = eval_orig_jac.calls
    report['nit'] = idx_newton_step
    report['status'] = 1 if report.success else 0
    report['message'] = f"Newton iteration is considered successful: {report.success}"
    report['fun'] = f_n
    # non used scipy-standard-fields here: 'nhev', 'jac', 'hess'

    return report


class sparse_newton_results(results_base): pass


class sparse_newton_options(options_base):
    '''
        docu
    '''

    def __init__(self, name : str = "sparse Newton options", **kwargs):
        '''
            docu

            :param name:
        '''

        additional_keys : List['str'] = ['name',
                                         'atol_dom', 'rtol_dom',
                                         'atol_range', 'rtol_range',
                                         'atol_root',
                                         'max_it',
                                         'max_times_J_n_constant',
                                         'gamma_min',
                                         'no_convergence_is_Error',
                                         'apply_row_scaling']
        super().__init__(name = name, additional_keys = additional_keys)

        self.atol_dom : Union[None, float, Vec_t] = 1.0e-8
        self.rtol_dom : Union[None, float, Vec_t] = 1.0e-6

        self.atol_range : Union[None, float, Vec_t] = 1.0e-8
        self.rtol_range : Union[None, float, Vec_t] = 1.0e-6

        self.atol_root : Union[None, float, Vec_t] = None

        self.max_it : int = 100

        self.max_times_J_n_constant : Union[None, int] = 4  # None == no max number

        self.gamma_min : float = 1.0e-12

        self.no_convergence_is_Error : bool = True

        self.apply_row_scaling : bool = True
