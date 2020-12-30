from paso.systems_of_euqations.nlin.generic_nlin_nr1.generic_nlin_nr1 import f_and_jac_f, f_df as fun, x0

from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve


report = sparse_nl_solve(fun = fun, x0 = x0)

print(report)


print('script finished!')
