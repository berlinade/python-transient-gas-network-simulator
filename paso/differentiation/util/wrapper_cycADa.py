import numpy as np
from scipy.sparse import csr_matrix

from ad.cycADa import tape, adFloat # necessary import for AD with cycADa


'''
    construct jacobian function of collocation method by cycADa
'''

def cycADa_wrapper(fun, ndim, return_jac_dense = False):
    trace = tape(num_of_sets = 1, ignore_kinks = True)     # initialize cycADa and cycADa tape structure

    x_ad = np.array([adFloat(trace) for _ in range(ndim)]) # initialize overloaded tracing variables
    f_ad = fun(x_ad)                                       # overload compatible function by cycADa

    trace.declare_dependent(f_ad)                          # mark output as dependent
    trace.allocJac(False)                                  # allocate cycADa memory for Jacobian

    def fun_ad(x):
        trace(x)

        return np.array([entry.val for entry in f_ad])  # create numpy array for return from evaluation

    def fun_jac_csr(x):
        trace.D(x) # update Jacoby matrix
        CSR_jac = csr_matrix((np.array(trace.data), abs(np.array(trace.indices)), np.array(trace.indptr)),
                             shape = (trace.m, trace.n)) # copy Jacoby information and create sparse matrix from

        if return_jac_dense: return CSR_jac.toarray()
        return CSR_jac

    return fun_ad, fun_jac_csr
