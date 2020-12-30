from ad.cycADa import tape, adFloat, sin, cos, exp, log, inv

import scipy.sparse.linalg as spslin
from scipy.sparse import csr_matrix
import numpy as np
import time


def _simple_NewtonSecant_step(f, jac, xi, **opts):
    '''
    implements a step of a full step Newton

    args:
        f - a callable object of the right-hand-side function (RHS) of root problem, i.e. 0 = f(x, *args, **kwargs);
            herby is args a list of optional arugments contained within opts with "args" as keyword and kwargs a
            dictionary of optional arguments contained within opts with "kwargs" as keyword
        jac - a callable object for the computation of Jacobians of the RHS, i.e.
              d/dx f(x, *args, **kwargs) = jac(x, *args, **kwargs);
              the output of jac(<>) is assumed to be an instance of scipy.sparse.csr_matrix;
              jac assumed to take the same args and kwargs as f
        xi - a 1D-numpy array representing the current iterate from where to start the current Newton step
        opts - containier for additonal keywords; currently (including defaults):
               {"args" : None, "kwargs" : None, "permc_spec" : None, "use_umfpack" : True};
               for the keywords "permc_spec" and "use_umfpack" see documentation of scipy.sparse.linalg.spsolve

    solves
        jac(xi, *args, **kwargs)*delta_xi = -f(xi, *args, **kwargs)
        xip1 = xi + delta_xi
    by scipy.sparse.linalg.spsolve

    returns xip1 (read xi plus 1) - a 1D-numpy array representing the next Newton step
    '''

    args = opts.get("args", None)
    kwargs = opts.get("kwargs", None)

    if args is None:
        if kwargs is None:
            A, b = jac(xi), -f(xi)
        else:
            A, b = jac(xi, **kwargs), -f(xi, **kwargs)
    else:
        if kwargs is None:
            A, b = jac(xi, *args), -f(xi, *args)
        else:
            A, b = jac(xi, *args, **kwargs), -f(xi, *args, **kwargs)

    return xi + spslin.spsolve(A, b,
                               permc_spec = opts.get("permc_spec", None),
                               use_umfpack = opts.get("use_umfpack", True))


def simple_NewtonSecant_method(f, jac, x0, **opts):
    '''
    implements a simple full-step Newton method for demonstration of cycADa's abillities to compute derivatives!

    args:
        f - a callable object of the right-hand-side function (RHS) of root problem, i.e. 0 = f(x, *args, **kwargs);
            herby is args a list of optional arugments contained within opts with "args" as keyword and kwargs a
            dictionary of optional arguments contained within opts with "kwargs" as keyword;
        jac - a callable object for the computation of Jacobians of the RHS, i.e.
              d/dx f(x, *args, **kwargs) = jac(x, *args, **kwargs);
              the output of jac(<>) is assumed to be an instance of scipy.sparse.csr_matrix;
              jac assumed to take the same args and kwargs as f
        x0 - a 1D-numpy array representing the starting point of a Newton iteration to compute
        opts - containier for additonal keywords; currently (including defaults):
               {"args" : None, "kwargs" : None, "permc_spec" : None, "use_umfpack" : True, "check_range" : False,
                "atol_dom" : 1.0e-8, "rtol_dom" : 1.0e-6, "atol_range" : 1.0e-8, "rtol_range" : 1.0e-6,
                "callback" : None};
               for the keywords "permc_spec" and "use_umfpack" see documentation of scipy.sparse.linalg.spsolve;
               the keywords "atol_range" and "rtol_range" are used only if "check_range" is True;
               "callback" is assumed to be callable function and takes (xip1, xi, ip1, opts, res, f_res) as args

    solves
        jac(xi, *args, **kwargs)*delta_xi = -f(xi, *args, **kwargs)
        xip1 = xi + delta_xi
    by scipy.sparse.linalg.spsolve repeatedly

    returns:
        xip1 (read xi plus 1) - a 1D-numpy array representinglatest iterate after a certain amount of steps
                                (the latter which is determined by options and whether xip1 met the criterion or the
                                maximum number of iterations have been reached;)
        ip1 (read i plus 1) - an integer representing the latest iteration index
    '''

    orig_shape_of_x0 = x0.shape
    xi = x0.reshape((-1,))

    success_atol_dom, success_rtol_dom, success_atol_range, success_rtol_range = [False]*4
    atol_dom = opts.get("atol_dom", 1.0e-8)
    rtol_dom = opts.get("rtol_dom", 1.0e-6)
    callback = opts.get("callback", None)

    check_range = opts.get("check_range", False)
    if check_range:
        atol_range = opts.get("atol_range", 1.0e-8)
        rtol_range = opts.get("rtol_range", 1.0e-6)

        fi_res = np.linalg.norm(f(x0))
    else:
        f_res = None

    for ip1 in range(1, opts.get("max_i", 55)+1):
        xip1 = _simple_NewtonSecant_step(f, jac, xi, **opts)
        res = np.linalg.norm(xip1 - xi)

        if res <= atol_dom:
            success_atol_dom = True
        if res <= rtol_dom*np.linalg.norm(xi):
            success_rtol_dom = True
        if check_range:
            f_res = np.linalg.norm(f(xip1.reshape(orig_shape_of_x0)))
            if f_res <= atol_range:
                success_atol_range = True
            if f_res <= rtol_range*fi_res:
                success_rtol_range = True
            fi_res = f_res

        if callable(callback):
            callback(xip1, xi, ip1, opts, res, f_res)

        if success_atol_dom or success_rtol_dom or success_atol_range or success_rtol_range:
            break

        xi = xip1

    if check_range:
        return xip1.reshape(orig_shape_of_x0), ip1, \
               success_atol_dom, success_rtol_dom, success_atol_range, success_rtol_range
    return xip1.reshape(orig_shape_of_x0), ip1, \
           success_atol_dom, success_rtol_dom


if __name__ == "__main__":
    def generate_f(dim_f):
        dim_f = int(max(3, dim))

        def f(x):
            orig_shape_of_x = x.shape
            x = x.reshape((-1,))
            out = np.zeros(shape = (dim,), dtype = x.dtype)

            #body of f
            out[0] = x[0] + sin(x[1])
            for i in range(1, dim_f-1):
                out[i] = cos(x[i-1]) + log((x[i] + 1.0)**2.0) - x[i+1]/3.0
            out[-1] = sin(x[-2]) + x[-1]

            return out.reshape(orig_shape_of_x)

        return f

    def finiteDiffMat(x, h = 1.0e-8, Mat = None):
        x = x.reshape((-1,))
        dim_x = len(x)
        if Mat is None:
            Mat = np.zeros(shape = (dim_x, dim_x))
        for i in range(dim_x):
            Mat[:, i] = (f(x + h*np.eye(1, dim_x, i)) - f(x))/h
        return Mat

    dim = 500
    f = generate_f(dim)
    x0 = np.zeros(shape = (dim,))
    zeros_of_len_x = np.zeros(shape = (dim,))

    t = tape(1, True)

    x_ad = np.array([adFloat(t) for _ in range(dim)])
    f_ad = f(x_ad)
    t.declare_dependent(f_ad)

    t.allocJac() # allocate memory space for Jacobian once
    jac_f = csr_matrix((t.data, abs(t.indices), t.indptr)) # prepare csr_matrix from allocated space

    # define primal evaluation of f via cycADa (technically unnecessary, but faster)
    def f_for_NewtonSecant(x, **kwargs):
        orig_shape_of_x = x.shape
        x = x.reshape((-1,))
        t(x)

        return np.array([f_adi.val for f_adi in f_ad]).reshape(orig_shape_of_x)

    def jac_f_for_Newton(x):
        t.D(x, zeros_of_len_x)
        return jac_f # calling t.D has updated jac_f

    NewtonOut = simple_NewtonSecant_method(f_for_NewtonSecant, jac_f_for_Newton, x0)
    xip1 = NewtonOut[0]

    print("Newton:")
    print("ip1: {} | success: {}".format(NewtonOut[1], NewtonOut[2] or NewtonOut[3]))
    print("")
    print("||f_tape(x_ip1)|| = {}".format(np.linalg.norm(f_for_NewtonSecant(xip1))))
    print("||f(x_ip1)||      = {}".format(np.linalg.norm(f(xip1))))
    print("")

    def callback(xip1, xi, ip1, opts, res, f_res):
        opts["kwargs"]["x_old"] = xi

    def jac_f_for_Secant(x, **kwargs):
        xhat, xcheck = x, kwargs["x_old"] # xhat and xcheck are the two reference points of secant expansion
        t.D(0.5*(xhat + xcheck), 0.5*(xhat - xcheck)) # define mid point and radius between xhat and xcheck
        return jac_f # calling t.D has updated jac_f

    SecantOut = simple_NewtonSecant_method(f_for_NewtonSecant, jac_f_for_Secant, x0,
                                           kwargs = {"x_old" : x0}, callback = callback)
    xip1 = SecantOut[0]

    print("Secant:")
    print("ip1: {} | success: {}".format(SecantOut[1], SecantOut[2] or SecantOut[3]))
    print("")
    print("||f_tape(x_ip1)|| = {}".format(np.linalg.norm(f_for_NewtonSecant(xip1))))
    print("||f(x_ip1)||      = {}".format(np.linalg.norm(f(xip1))))
    print("")


    # some simple timing stats about cycADa
    print("some simple timing stats about cycADa:")
    repetitions = 5000

    start = time.time()
    for i in range(repetitions):
        f_for_NewtonSecant(xip1)
    print("{} evaluations of f_tape (dim = {}): {} sec".format(repetitions, dim,
                                                               time.time()-start))

    start = time.time()
    for i in range(repetitions):
        f_for_NewtonSecant(xip1)
        jac_f_for_Newton(xip1)
    print("{} evaluations of f_tape -AND- jac_f_tape (dim = {}): {} sec".format(repetitions, dim,
                                                                                time.time()-start))

    start = time.time()
    for i in range(repetitions):
        f(xip1)
    print("{} evaluations of f (non-vectorized pure python; dim = {}): {} sec".format(repetitions, dim,
                                                                                      time.time()-start))

    print("")


    print("main finished!")
