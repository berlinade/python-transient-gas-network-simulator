'''
    prepared, convenient wrapper for scipy sparse linear solvers
    ============================================================
'''

__author__ = ('Sascha Baumanns', 'Tom Streubel', 'Christian Strohm', 'Caren Tischendorf') # alphabetical order of surnames
__credits__ = ('Lennart Jansen',) # alphabetical order of surnames


'''
    imports
    =======
'''
import numpy as np
from scipy.sparse.linalg import lsqr

from paso.util.types_and_errors import Vec_t, CsMatrix_t, LinSolveError, LinSolve_t
from paso.solvers.nlin.sparse_nl_solver.newton.predefined.linsolvers import linsolver_template

from typing import Union


'''
    body
    ====
'''
class lsqr_simple_wrapper(linsolver_template):

    def __init__(self): super().__init__(name = 'scipy.sparse.linalg.lsqr')

    def __call__(self,
                 A : CsMatrix_t,
                 b : Vec_t,
                 A_did_change : bool = True) -> Vec_t:
        '''
            :param A: CSR -or- sparse system matrix of a linear system of equations: A*x = b
            :param b: right-hand-side (RHS) vector of a linear system of equations: A*x = b
            :param A_did_change: boolean flag whether the system matrix has changed since last call
            :return: solution x as vector of A*x = b
        '''
        try: return lsqr(A, b)[0]
        except: raise LinSolveError('lsqr failed!')
