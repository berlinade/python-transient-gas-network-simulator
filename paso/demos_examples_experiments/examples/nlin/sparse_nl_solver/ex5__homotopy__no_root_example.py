import numpy as np

from paso.solvers.nlin.sparse_nl_solver.homotopy.core import homotopy_solve
from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve, sparse_newton_options, NLinSolveError

from paso.solvers.nlin.sparse_nl_solver.homotopy.predefined.callbacks import callback_print_progress


def fun(x): return x**2.0 + 0.1

x0 = np.array([2.2])


''' will find point of minimal residuum '''
report = homotopy_solve(fun = fun, x0 = x0, callback = callback_print_progress())
print(report)
print('\n\n')

''' will find point of minimal residuum '''
report = sparse_nl_solve(fun = fun, x0 = x0)
print(report)


print('\n\n\n' + '<<-- the following solve instances HAVE TO FAIL, due to missing existence of a root! -->>' + '\n\n\n')


options = sparse_newton_options()
options.no_convergence_is_Error = False
options.atol_root = 1.0e-8
def nlinsolver(*args, **kwargs): return sparse_nl_solve(*args, options = options, **kwargs)

''' will fail, due to no root! '''
try:
    report = homotopy_solve(fun = fun, x0 = x0, callback = callback_print_progress(), nlinsolver = nlinsolver)
    print(report)
except NLinSolveError:
    print('homotopy failed \n\n')

''' will fail, due to no root! '''
try:
    options.no_convergence_is_Error = True
    report = nlinsolver(fun = fun, x0 = x0)
    print(report)
except NLinSolveError:
    print('Newton failed \n\n')



print('script finished!')
