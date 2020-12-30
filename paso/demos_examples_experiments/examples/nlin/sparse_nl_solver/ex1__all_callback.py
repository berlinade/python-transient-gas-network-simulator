from paso.systems_of_euqations.nlin.generic_nlin_nr1.generic_nlin_nr1 import f_and_jac_f, f_df as fun, x0

from paso.solvers.nlin.sparse_nl_solver.newton.core import sparse_nl_solve, sparse_newton_options
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.linsolvers import spilu_simple_wrapper
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.callbacks import callback_store_all_iterates, \
                                                                           callback_print_progress, \
                                                                           callback_matrix_spy, \
                                                                           callback_of_callbacks


def jac(x): return (f_and_jac_f(x)[1]).tocsc(copy = True)


''' create options file for newton iteration (optional) '''
nopts = sparse_newton_options()
nopts.max_times_J_n_constant = 10
nopts.max_it = 10000
nopts.no_convergence_is_Error = False

''' try out all possible callbacks available so far '''
callback_print = callback_print_progress() # print out progress to console
callback_log = callback_print_progress(file_path_and_name = 'ex1__Newton_fullstep.log') # print out progress to log
callback_iter = callback_store_all_iterates() # not only get the root but any iterate before
callback_spy = callback_matrix_spy(stop_at_each_fig = False) # get a plot of the matrix sprsity pattern
callback = callback_of_callbacks(callback_print, callback_log, callback_iter, callback_spy) # call all other callbacks

report = sparse_nl_solve(fun = fun, x0 = x0, jac = jac,
                         linsolver = spilu_simple_wrapper(),
                         callback = callback, options = nopts)

print('')
print(report)
print('')

print(callback_iter.Xs)
callback_spy.conclude()


print('script finished!')
