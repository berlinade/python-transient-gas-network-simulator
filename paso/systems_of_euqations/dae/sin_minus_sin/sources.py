'''
    simple DAE example
'''


import numpy as np

from paso.differentiation.util.math_aux import create_ufunc_handler, maximum, minimum


ufunc_handler = create_ufunc_handler()

try:
    from ad.cycADa import sin as _cy_sin_func, cos as _cy_cos_func, exp as _cy_exp_func

    ufunc_handler.sin_func = _cy_sin_func
    ufunc_handler.cos_func = _cy_cos_func
except (ModuleNotFoundError, ImportError) as e:
    print(e)
    print("[Note]: Did not found cycADa and loaded pure numpy version of sin, cos, exp, log!")


def f(dv, v, t):
    dx, dy = dv
    x, y = v

    cos = ufunc_handler.cos_func

    return np.array([dx - cos(t), x + y])

def sol(t):
    sin = ufunc_handler.sin_func

    return np.array([sin(t), -sin(t)])

t0, T = 0.0, 4.0*np.pi
v0 = sol(t0)
