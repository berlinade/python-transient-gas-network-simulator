import numpy as np

from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve, sparse_newton_options
from paso.solvers.nlin.sparse_nl_solver.newton.specialised.linsolvers import lsqr_simple_wrapper
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.callbacks import callback_print_progress, \
                                                                           callback_of_callbacks, \
                                                                           callback_store_all_iterates

from scipy.optimize import least_squares


def fun(x):
    x0, x1 = x[0], x[1]

    out = [np.sin(x0 + x1)/2.0 + 2.0*x0 + 3.0*x1, 5 - x0, 4 - x1]

    return np.array(out)

x0 = 5.0*np.ones(shape = (2,))


option = sparse_newton_options()
option.atol_dom = 1.0e-12
option.atol_range = None
option.rtol_dom = None
option.rtol_range = None
option.apply_row_scaling = False # <- better turn this off! This changes the 'weights' of the row equations and therefore alters the position of the optimum
# option.max_times_J_n_constant = 0

cb2 = callback_store_all_iterates()
callback = callback_of_callbacks(callback_print_progress(), cb2) #, callback_matrix_spy())

report = sparse_nl_solve(fun = fun, x0 = x0, linsolver = lsqr_simple_wrapper(), callback = callback,
                         options = option)

print(report)
print('')
print(cb2.Xs)

print('\n')

print(least_squares(fun, report.x))


print('script finished!')
