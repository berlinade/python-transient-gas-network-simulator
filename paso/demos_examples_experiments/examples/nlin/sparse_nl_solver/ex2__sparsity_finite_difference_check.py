import numpy as np

from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve, sparse_newton_options
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.linsolvers import spilu_simple_wrapper
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.callbacks import callback_print_progress, \
                                                                           callback_matrix_spy, \
                                                                           callback_of_callbacks


def fun(x, create_pattern = False):
    dim_x = len(x)

    out = np.zeros(shape = (dim_x,))

    out[0] = x[-1] + x[1]*np.sin(x[0]/10.0) - 0.1
    if create_pattern: pattern = [[dim_x - 1, 0, 1]]
    else: pattern = None
    for i in range(1, dim_x - 1):
        out[i] = x[i - 1] + ((-1.0)**i)*x[i + 1]*np.sin(x[i]/10.0)
        if create_pattern: pattern.append([i - 1, i, i + 1])
    out[-1] = x[-2] + x[0]*np.cos(x[-1]/10.0)
    if create_pattern: pattern.append([dim_x - 2, dim_x - 1, 0])

    if create_pattern: return out, pattern
    return 100.0*out

x0 = (np.pi - 1.0)*np.random.random_sample(size = (50,)) + 1.0
fx0, pattern = fun(x0, True)


''' create options file for newton iteration (optional) '''
nopts = sparse_newton_options()
nopts.max_times_J_n_constant = 10
nopts.max_it = 10000
nopts.no_convergence_is_Error = False

''' try out all possible callbacks available so far '''
callback_print = callback_print_progress() # print out progress to console
callback_spy = callback_matrix_spy(stop_at_each_fig = False) # get a plot of the matrix sprsity pattern
callback = callback_of_callbacks(callback_print, callback_spy) # call all other callbacks

report = sparse_nl_solve(fun = fun, x0 = x0, jac = pattern,
                         linsolver = spilu_simple_wrapper(),
                         callback = callback, options = nopts)

print('')
print(report)
print('')

callback_spy.conclude()


print('script finished!')
