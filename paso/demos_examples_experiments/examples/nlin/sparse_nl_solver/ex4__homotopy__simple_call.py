from paso.systems_of_euqations.nlin.generic_nlin_nr1.generic_nlin_nr1 import f_and_jac_f, f_df as fun, x0

from paso.solvers.nlin.sparse_nl_solver.homotopy.core import homotopy_solve
from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve

from paso.solvers.nlin.sparse_nl_solver.homotopy.predefined.callbacks import callback_print_progress


report = homotopy_solve(fun = fun, x0 = x0, callback = callback_print_progress())
print(report)

print('\n')

report = sparse_nl_solve(fun = fun, x0 = x0)
print(report)


print('script finished!')
