'''
    name:
        generic nonlinear system of equations number 1 (nr.1)

    description:
        Has no special background.

    smoothness of system function:
        smooth  -and-  nonsmooth (everywhere locally Lipschitzean)

    dimension:
      - domain: 2
      - range: 2

    initial value:
      - x0: initial value can be generated

    solution:
        provided

    note:
        not fit for kynsol without modifications. kynsol requires the sparsity pattern of the jacobian to be fix,
        but when using scipy csr, scipy might change the pattern to eliminate additional 0's in the data. In other
        words: the CSR-matrix structure has to be build by hand!
'''

'''
    major imports
    =============
'''
import numpy as np
import scipy.sparse as sps

from paso.differentiation.util.math_aux import create_ufunc_handler


ufunc_handler = create_ufunc_handler()

try:
    from ad.cycADa import sin as _cy_sin_func, cos as _cy_cos_func, exp as _cy_exp_func

    ufunc_handler.sin_func = _cy_sin_func
    ufunc_handler.cos_func = _cy_cos_func
    ufunc_handler.exp_func = _cy_exp_func
except (ModuleNotFoundError, ImportError) as e:
    print(e)
    print("[Note]: Did not found cycADa and loaded pure numpy version of sin, cos, exp, log!")


'''
    implementation
    ==============
'''
def f_df(x, dx = None):
    derive = (not (dx is None))

    sin = ufunc_handler.sin_func
    exp = ufunc_handler.exp_func
    if derive: cos = ufunc_handler.cos_func

    if not isinstance(x, np.ndarray): x = np.array(x)
    if not x.shape == (2,): raise AssertionError('shape of input has to be (2,)')

    if derive and (not isinstance(dx, np.ndarray)):
        dx = np.array(dx)
        if (not len(dx.shape) < 3) or (not dx.shape[0] == 2):
            raise AssertionError('shape of dinput has to be (2,) or (2, k), with k some positive integer')

    out = np.zeros(shape = x.shape, dtype = x.dtype)
    if derive: dout = np.zeros(shape = dx.shape, dtype = x.dtype)

    v0 = x[0] + x[1]
    if derive: dv0 = dx[0, :] + dx[1, :]

    v1 = 2.0*v0
    if derive: dv1 = 2.0*dv0

    v2 = sin(v0)
    if derive: dv2 = cos(v0)*dv0

    out[0] = v1 + v2
    if derive: dout[0, :] = dv1 + dv2

    v3 = x[0] - x[1]
    if derive: dv3 = dx[0] - dx[1]

    v4 = exp(v3)
    if derive: dv4 = v4*dv3

    out[1] = v4 - 1.0
    if derive: dout[1, :] = dv4

    if derive: return out, dout
    return out


def f_and_jac_f(x):
    dX = np.eye(2, 2)
    fx, jac_fx = f_df(x, dX)
    csr_mat = sps.csr_matrix(jac_fx)
    return fx, csr_mat


x0 = np.array([np.pi, -np.exp(1.1)])

x_sol = np.zeros(shape = (2,))
