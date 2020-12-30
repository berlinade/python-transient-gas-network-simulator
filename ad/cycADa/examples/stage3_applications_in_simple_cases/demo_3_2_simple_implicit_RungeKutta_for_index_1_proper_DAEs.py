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
    This demonstration shows how cycADa can be incorporated into a one-step multi-stage solver for properly formulated 
    DAEs: 0 = f(d'(x, t), x, t). There will be no 'scoping' (see demo_simple_implicit_Euler_for_index1_std_DAEs.py) 
    necessary. 
    One last note: This approach is analogously applicable to BDF or other multi-step methods but slightly more easy.
'''


# Radau IIA (5th order method)
c0 = np.sqrt(6.0)
c = np.array([2.0/5.0 - c0/10.0, 2.0/5.0 + c0/10.0, 1.0])
A = np.array([[ 11.0/45.0 - 7.0*c0/360.0,    37.0/225.0 - 169.0*c0/1800.0, -2.0/225.0 + c0/75.0],
              [37.0/225.0 + 169.0*c0/1800.0,  11.0/45.0 + 7.0*c0/360.0,    -2.0/225.0 - c0/75.0],
              [   4.0/9.0 - c0/36.0,            4.0/9.0 + c0/36,                       1.0/9.0]])
A_inv = np.linalg.inv(A)

num_stages = len(c)


def _inner_RK_template(f, d, X, x_check, t_check, h, dim_x_check):
    inner_t = [t_check + h*ci for ci in c]
    X = X.reshape((dim_x_check, -1))
    dx_check = d(x_check, t_check)
    dX = [d(X[:, j], tj) for j, tj in enumerate(inner_t)]

    out = np.zeros(shape = (dim_x_check, num_stages), dtype = X.dtype)

    for i, ti in enumerate(inner_t):
        sum_j = A_inv[i, 0]*(dX[0] - dx_check)
        for j, tj in enumerate(inner_t[1:], start = 1):
            sum_j += A_inv[i, j]*(dX[j] - dx_check)
        for k in range(len(sum_j)):
            sum_j[k] /= h

        out[:, i] = f(sum_j, X[:, i], ti)

    return out.reshape((-1,))


def _RK_step(t, F_ad, reference_point_for_cycADa, jac_mat_f,
             ti, dim_X, dim_x, Xi, xi, h):
    '''
        prepare time dependent system function of RK step
    '''
    def inner_RK(X):
        reference_point_for_cycADa[:dim_X] = X
        reference_point_for_cycADa[dim_X:dim_X + dim_x] = xi
        reference_point_for_cycADa[-2:] = ti, h

        t(reference_point_for_cycADa)

        return np.array([F_ad_i.val for F_ad_i in F_ad])

    def inner_RK_jac(X):
        reference_point_for_cycADa[:dim_X] = X
        reference_point_for_cycADa[dim_X:dim_X + dim_x] = xi
        reference_point_for_cycADa[-2:] = ti, h

        t.D(reference_point_for_cycADa)

        return jac_mat_f

    Xi = simple_NewtonSecant_method(inner_RK, inner_RK_jac, Xi)[0]
    xi = (Xi.reshape( (dim_x, -1) ))[:, -1]

    return xi, Xi


def simple_RK(f, d, x0, t0, T, h):
    dim_x = len(x0)
    dim_X = num_stages*dim_x
    Xi = np.array([x0 for _ in range(num_stages)])
    xi = x0
    N = int((T-t0)/h)

    Xs = [x0]
    Ts = [t0 + i*h for i in range(N)]

    '''
        prepare and overloading of RK_template
    '''
    t = tape()
    X_ad = np.array([adFloat(t, [True]) for _ in range(dim_X)])
    x_ad = np.array([adFloat(t, [False]) for _ in range(dim_x)])
    t_ad = adFloat(t, [False])
    h_ad = adFloat(t, [False])
    reference_point_for_cycADa = np.zeros(shape = (dim_X + dim_x + 2,))
    F_ad = _inner_RK_template(f, d, X_ad, x_ad, t_ad, h_ad, dim_x)
    t.declare_dependent(F_ad)
    t.allocJac() # allocate memory space for Jacobian once
    jac_mat_f = csr_matrix((t.data, abs(t.indices), t.indptr))

    '''
        time iteration
    '''
    for ti in Ts[:-1]:
        xi, Xi = _RK_step(t, F_ad, reference_point_for_cycADa, jac_mat_f,
                          ti, dim_X, dim_x, Xi, xi, h)

        Xs.append(xi)

    if Ts[-1] < T:
        h = T - Ts[-1]
        Ts.append(T)

        Xs.append(_RK_step(t, F_ad, reference_point_for_cycADa, jac_mat_f,
                           Ts[-2], dim_X, dim_x, Xi, xi, h)[0])

    return Ts, Xs


if __name__ == "__main__":
    def f(dv, v, t):
        x, y, z = v
        dx, dz = dv

        # the 2nd & 3rd component are a bit artificial,
        # but this example is a demonstration of cycADa and by far NOT A HOW TO SOLVE DAEs COMPUTATIONALLY !1!!
        # -> HINT: solving DAEs in python can be done by sundials via e.g. ODES scikit (python interface for sundials)
        return np.array([dz + x, dx - y, exp(y - z) - 1.0])

    def d(v, t):
        x, y, z = v
        return np.array([x, z])

    # DAE-IVP essentials
    t0 = 0.0 # initial time point
    T = 4.0*np.pi # end-time
    h = 0.1 # time-step size
    x0 = np.array([np.sin(t0), np.cos(t0), np.cos(t0)]) # initial value

    # define exact solution for the simple DAE-example
    def exact_solution(t):
        cos_t = np.cos(t)
        return np.array([np.sin(t), cos_t, cos_t])

    # execute Euler's method
    Ts, Xs = simple_RK(f, d, x0, t0, T, h)

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
