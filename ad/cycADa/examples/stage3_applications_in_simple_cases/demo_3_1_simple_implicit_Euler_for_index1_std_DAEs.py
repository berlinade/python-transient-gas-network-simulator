from ad.cycADa import tape, adFloat, sin, cos, exp, log, inv
from ad.cycADa.examples.stage3_applications_in_simple_cases.demo_3_0_simple_smooth_Newton_method import simple_NewtonSecant_method

from scipy.sparse import csr_matrix
import numpy as np

import matplotlib.pyplot as plt


'''
    This is NOT A HOW TO SOLVE DAEs COMPUTATIONALLY !1!! 
      -> HINT: solving DAEs in python can be done by sundials via e.g. ODES scikit (python interface for sundials)
    
    Actual Purpose of this Demonstration:
    -------------------------------------
    Consider a DAE in so called standard form, i.e. 0 = f(dx, x, t) with initial value setup, i.e. x(t0) = x0.
    For most DAE solvers either you have to provide a linear combination of Jacobians/partial derivative matrices, i.e.
        jac(c, h, x) = (c/h)*(d f)/(d dx) + (d f)/(d x)
    or you have to provide the following two Jacobians/partial derivative matrices
        jac_dfdx = (d f)/(d dx)   -and-   jac_dfx = (d f)/(d x)
    each on there own, such that the solver can build the linear combination (from above) itself. 
    The latter is often required if you use a more elaborated DAE solver for DAEs in proper form, i.e. 
        0 = f(d'(x, t), x, t).
    This demonstration will show how to incorporate the scope-feature of cycADa to realize both alternatives for
    providing Jacobian information from the same DAE-system function but  -WITHOUT-   re-taping. Because
    this a special feature of cycADa and may help in reducing memory and runtime costs. 
    The feature cycADa offers here is called 'tape-scoping'. 
    To keep the demonstration as simple as possible as well as to avoid additional dependencies, we will define a 
    constant time-step-size, implicit Euler for low-dimensional, index 1 problems in standard form.
'''


def _simple_Euler_step(f, jac_of_fdx, jac_of_fx, xi, tip1, h):
    hinv = 1.0/h
    def Euler_sys_func(x):
        args = (x - xi)*hinv, x, tip1

        return f(*args)

    def Euler_jac(x):
        args = (x - xi)*hinv, x, tip1

        return hinv*jac_of_fdx(*args) + jac_of_fx(*args)

    NewtonOut = simple_NewtonSecant_method(Euler_sys_func, Euler_jac, xi)

    return NewtonOut[0]


def simpleEuler_method(f, jac_of_fdx, jac_of_fx, x0, t0, T, h):
    orig_shape_of_x0 = x0.shape
    xi = x0.reshape((-1,))
    N = int((T-t0)/h)

    Xs = [x0]
    Ts = [t0 + i*h for i in range(N)]

    for tip1 in Ts[1:]:
        xi = _simple_Euler_step(f, jac_of_fdx, jac_of_fx, xi, tip1, h)

        Xs.append(xi)

    if Ts[-1] < T:
        h = T - Ts[-1]
        Ts.append(T)

        Xs.append(_simple_Euler_step(f, jac_of_fdx, jac_of_fx, xi, T, h))

    return Ts, Xs


if __name__ == "__main__":
    # define system function of DAE in standart form
    def f(dv, v, t):
        x, y, z = v
        dx, dy, dz = dv

        # the 2nd & 3rd component are a bit artificial,
        # but this example is a demonstration of cycADa and by far NOT A HOW TO SOLVE DAEs COMPUTATIONALLY !1!!
        # -> HINT: solving DAEs in python can be done by sundials via e.g. ODES scikit (python interface for sundials)
        return np.array([dz + x, 1.0 - exp(dx - y), y - z])

    # DAE-IVP essentials
    t0 = 0.0 # initial time point
    T = 4.0*np.pi # end-time
    h = 0.01 # time-step size
    x0 = np.array([np.sin(t0), np.cos(t0), np.cos(t0)]) # initial value

    # define exact solution for the simple DAE-example
    def exact_solution(t):
        cos_t = np.cos(t)
        return np.array([np.sin(t), cos_t, cos_t])

    # initialize tape for 2 scopes
    num_of_scopes = 2  # define 2 scopes
    trace = tape(num_of_scopes, True)

    # in the next block of code 3 types variables will be initialized. The 1st is going to be derived in the 1st scope,
    # only. The 2nd will be derived in the 2nd scope, only. The last will never be derived for in any scope.
    dx_ad = np.array([adFloat(trace, [1, 0]) for _ in range(3)]) # differentiation in scope 0, only
    x_ad = np.array([adFloat(trace, [0, 1]) for _ in range(3)]) # differentiation in sope 1, only
    t_ad = adFloat(trace, [0, 0]) # will never be differentiated for

    f_ad = f(dx_ad, x_ad, t_ad) # overloading
    trace.declare_dependent(f_ad) # tell cycADa what are the dpendent variables

    trace.scope = 0 # go into scope 0
    trace.allocJac() # allocate memory space for Jacobian of (d f)/(d dx) once
    jac_fdx = csr_matrix((trace.data, abs(trace.indices), trace.indptr)) # prepare csr_matrix from allocated space

    trace.scope = 1 # go into scope 1
    trace.allocJac() # allocate memory space for Jacobian of (d f)/(d x) once
    jac_fx = csr_matrix((trace.data, abs(trace.indices), trace.indptr)) # prepare csr_matrix from allocated space

    def f_for_Euler(dx, x, t): # primal evaluation is independent of scoping
        dx = dx.reshape((-1,))
        x = x.reshape((-1,))

        trace(np.concatenate( (dx, x, [t]) ))

        return np.array([f_adi.val for f_adi in f_ad])

    def jac_fdx_for_Euler(dx, x, t):
        dx = dx.reshape((-1,))
        x = x.reshape((-1,))

        trace.scope = 0 # update derivative Matrix in scope 0
        trace.D(np.concatenate( (dx, x, [t]) ))

        return jac_fdx

    def jac_fx_for_Euler(dx, x, t):
        dx = dx.reshape((-1,))
        x = x.reshape((-1,))

        trace.scope = 1 # update derivative Matrix in scope 1
        trace.D(np.concatenate( (dx, x, [t]) ))

        return jac_fx

    # execute Euler's method
    Ts, Xs = simpleEuler_method(f, jac_fdx_for_Euler, jac_fx_for_Euler, x0, t0, T, h)

    # plotting
    plt.subplot(2, 1, 1)
    plt.plot(Ts, Xs, label = "numerical solution of sin/cos")
    plt.plot(Ts, [exact_solution(ti) for ti in Ts], label = "exact solution of sin/cos")

    plt.xlabel = 'domain'
    plt.ylabel = 'range'
    plt.grid()
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(Ts, [abs(exact_solution(ti)[0] - xi[0]) for ti, xi in zip(Ts, Xs)], label = "error in sin")

    plt.xlabel = 'domain'
    plt.ylabel = 'range'
    plt.grid()
    plt.legend()

    plt.show()

    print("script finished")






